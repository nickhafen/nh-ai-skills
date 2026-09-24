"""Model clients: the real Claude API client and an offline mock for testing the pipeline."""

import hashlib
import json
import random
import re
import time
from dataclasses import dataclass, field

# USD per million tokens (input, output), first-party API rates as of 2026-06.
# Update if pricing changes. Cache reads bill at 0.1x input; cache writes at 1.25x.
PRICES = {
    "claude-fable-5-1": (10.0, 50.0),
    "claude-opus-5-5": (4.0, 20.0),
    "claude-opus-5": (5.0, 25.0),
    "claude-sonnet-5": (2.0, 10.0),
    "claude-haiku-4-5": (1.0, 5.0),
}

# Models that accept the server-side `fallbacks: "default"` refusal fallback.
FALLBACK_MODELS = {"claude-opus-5", "claude-fable-5-1"}


class ModelError(RuntimeError):
    """A call finished but can't be used (refusal, truncation, unparseable output)."""


@dataclass
class CallResult:
    text: str
    parsed: object
    stop_reason: str
    usage: dict
    duration: float
    model: str
    extra: dict = field(default_factory=dict)


def estimate_cost(model, usage):
    if model not in PRICES:
        return None
    price_in, price_out = PRICES[model]
    return round((usage["input_tokens"] * price_in
                  + usage["cache_read_input_tokens"] * price_in * 0.1
                  + usage["cache_creation_input_tokens"] * price_in * 1.25
                  + usage["output_tokens"] * price_out) / 1_000_000, 4)


class AnthropicClient:
    """Calls Claude through the official SDK. Credentials come from the environment
    (ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, or an `ant auth login` profile)."""

    name = "anthropic"

    def __init__(self, model="claude-opus-5", effort="high", max_tokens=32000, fallbacks=True):
        import anthropic

        self._anthropic = anthropic
        self.client = anthropic.Anthropic(max_retries=4)
        self.model = model
        self.effort = effort
        self.max_tokens = max_tokens
        self.fallbacks = fallbacks and model in FALLBACK_MODELS

    def call(self, *, system, messages, schema=None, context=None, label=""):
        output_config = {"effort": self.effort}
        if schema is not None:
            output_config["format"] = {"type": "json_schema", "schema": schema}
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
            "thinking": {"type": "adaptive"},
            "output_config": output_config,
        }
        if system:
            kwargs["system"] = system
        if self.fallbacks:
            kwargs["betas"] = ["server-side-fallback-2026-07-01"]
            kwargs["fallbacks"] = "default"

        start = time.monotonic()
        # Streaming avoids HTTP timeouts on long reviews; we only need the final message.
        with self.client.beta.messages.stream(**kwargs) as stream:
            message = stream.get_final_message()
        duration = time.monotonic() - start

        if message.stop_reason == "refusal":
            category = getattr(message.stop_details, "category", None) if message.stop_details else None
            raise ModelError(f"{label}: model declined (category: {category})")
        if message.stop_reason == "max_tokens":
            raise ModelError(f"{label}: output hit max_tokens ({self.max_tokens}); raise the limit")

        text = "".join(block.text for block in message.content if block.type == "text")
        parsed = None
        if schema is not None:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ModelError(f"{label}: response was not valid JSON ({exc})") from exc
        u = message.usage
        usage = {
            "input_tokens": u.input_tokens or 0,
            "output_tokens": u.output_tokens or 0,
            "cache_read_input_tokens": getattr(u, "cache_read_input_tokens", 0) or 0,
            "cache_creation_input_tokens": getattr(u, "cache_creation_input_tokens", 0) or 0,
        }
        return CallResult(text=text, parsed=parsed, stop_reason=message.stop_reason, usage=usage,
                          duration=duration, model=message.model, extra={"request_id": message._request_id})


class ClaudeCodeClient:
    """Runs each call through the Claude Code CLI (`claude -p`) on the user's own Claude plan.

    No API key needed; calls count against the plan's usage limits. Differences from the
    API client: Claude Code adds some framing of its own (user-level CLAUDE.md may load),
    and a call with no system prompt gets a neutral chat-assistant one instead of Claude
    Code's coding prompt. Multi-turn conversations (conditions A and B) resume the CLI
    session, so they are real multi-turn conversations.
    """

    name = "claude-code"
    NEUTRAL_SYSTEM = "You are Claude, an AI assistant made by Anthropic. Answer the user's question helpfully."

    def __init__(self, model="claude-opus-5", effort="high", timeout=900, workdir=None):
        import shutil
        import tempfile
        import threading

        self.executable = shutil.which("claude")
        if not self.executable:
            raise RuntimeError("Claude Code CLI ('claude') not found on PATH")
        self.model = model
        self.effort = effort
        self.timeout = timeout
        # Run outside the repo so the project's CLAUDE.md isn't loaded into reviews.
        self.workdir = workdir or tempfile.mkdtemp(prefix="fer-claude-code-")
        self._sessions = {}  # hash of conversation so far -> CLI session id
        self._lock = threading.Lock()
        self.reported_cost_usd = 0.0

    @staticmethod
    def _key(messages):
        return hashlib.sha256(json.dumps([{"role": m["role"], "content": _flatten(m["content"])}
                                          for m in messages], ensure_ascii=False).encode()).hexdigest()

    def call(self, *, system, messages, schema=None, context=None, label=""):
        import os
        import subprocess

        resume = None
        if len(messages) > 1:
            resume = self._sessions.get(self._key(messages[:-1]))
            if resume is None:
                raise ModelError(f"{label}: no CLI session to continue this conversation")
        # --disable-slash-commands drops the skills listing (~16.7k tokens per call);
        # --strict-mcp-config keeps the user's MCP servers out.
        cmd = [self.executable, "-p", "--output-format", "json", "--tools", "",
               "--disable-slash-commands", "--strict-mcp-config",
               "--model", self.model, "--effort", self.effort,
               "--system-prompt", system or self.NEUTRAL_SYSTEM]
        if schema is not None:
            cmd += ["--json-schema", json.dumps(schema)]
        if resume:
            cmd += ["--resume", resume]
        prompt = _flatten(messages[-1]["content"])

        # Don't let this desktop session's host-auth wiring leak into the child CLI.
        env = {k: v for k, v in os.environ.items()
               if not (k.startswith("CLAUDE_CODE_") or k in ("CLAUDECODE", "ANTHROPIC_BASE_URL"))}
        start = time.monotonic()
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8",
                              cwd=self.workdir, env=env, timeout=self.timeout)
        duration = time.monotonic() - start
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise ModelError(f"{label}: CLI returned no JSON (exit {proc.returncode}): "
                             f"{(proc.stderr or proc.stdout)[:300]}") from exc
        if data.get("is_error"):
            raise ModelError(f"{label}: {data.get('result') or data.get('terminal_reason')}")

        text = data.get("result") or ""
        parsed = None
        if schema is not None:
            parsed = data.get("structured_output")
            if parsed is None:
                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError as exc:
                    raise ModelError(f"{label}: response was not valid JSON ({exc})") from exc
            text = json.dumps(parsed, ensure_ascii=False)
        u = data.get("usage") or {}
        usage = {
            "input_tokens": u.get("input_tokens", 0) or 0,
            "output_tokens": u.get("output_tokens", 0) or 0,
            "cache_read_input_tokens": u.get("cache_read_input_tokens", 0) or 0,
            "cache_creation_input_tokens": u.get("cache_creation_input_tokens", 0) or 0,
        }
        cost = data.get("total_cost_usd") or 0.0
        with self._lock:
            self.reported_cost_usd += cost
            self._sessions[self._key(messages + [{"role": "assistant", "content": text}])] = data["session_id"]
        # Claude Code may run small side tasks on another model; report the one that did the most work.
        model_usage = data.get("modelUsage") or {}
        main = max(model_usage, key=lambda m: model_usage[m].get("costUSD", 0), default=self.model)
        return CallResult(text=text, parsed=parsed, stop_reason=data.get("stop_reason") or "end_turn",
                          usage=usage, duration=duration, model=main,
                          extra={"session_id": data["session_id"], "cost_usd": cost,
                                 "model_usage": model_usage, "duration_api_ms": data.get("duration_api_ms")})


class MockClient:
    """Offline stand-in that returns schema-valid output built from the document.

    It exercises every code path (prompts, routing, schema, scoring) without API calls.
    Its reviews are meaningless; never use its output to judge quality.
    """

    name = "mock"

    def __init__(self, model="mock", seed=0):
        self.model = model
        self.seed = seed

    def call(self, *, system, messages, schema=None, context=None, label=""):
        context = context or {}
        rng = random.Random(int(hashlib.sha256(f"{self.seed}:{label}".encode()).hexdigest()[:8], 16))
        sentences = _sentences(context.get("document", "")) or ["(empty document)"]
        if schema is None:
            text = f"[mock answer to {label}] The document says: {rng.choice(sentences)}"
            parsed = None
        else:
            parsed = _generate(schema, "", rng, sentences, context)
            text = json.dumps(parsed, ensure_ascii=False)
        prompt_chars = len(system or "") + sum(len(_flatten(m["content"])) for m in messages)
        usage = {"input_tokens": prompt_chars // 4, "output_tokens": len(text) // 4,
                 "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
        return CallResult(text=text, parsed=parsed, stop_reason="end_turn", usage=usage,
                          duration=0.0, model=self.model)


def _flatten(content):
    if isinstance(content, str):
        return content
    return "\n\n".join(block.get("text", "") for block in content)


def _sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if len(p.strip()) > 25]


QUOTE_KEYS = {"quote", "document_quote"}
ID_POOLS = {
    "section_id": "section_ids",
    "finding_refs": "finding_refs",
    "finding_ref": "finding_refs",
    "prompt_id": "prompt_ids",
    "prompt_ids": "prompt_ids",
    "reader": "persona_ids",
    "readers": "persona_ids",
    "assumption_id": "assumption_ids",
    "depends_on_assumptions": "assumption_ids",
}


def _generate(schema, key, rng, sentences, context):
    if "anyOf" in schema:
        options = [s for s in schema["anyOf"] if s.get("type") != "null"]
        if not options or rng.random() < 0.15:
            return None
        return _generate(options[0], key, rng, sentences, context)
    kind = schema.get("type")
    if kind == "object":
        return {k: _generate(v, k, rng, sentences, context) for k, v in schema["properties"].items()}
    if kind == "array":
        pool = context.get(ID_POOLS.get(key, ""), None)
        if key == "attention_map" and context.get("section_ids"):
            return [{"section_id": sid,
                     "attention": rng.choice(["read_closely", "skimmed", "skipped"]),
                     "would_miss": None} for sid in context["section_ids"]]
        count = rng.randint(1, 3) if pool is None else min(len(pool), rng.randint(0, 2))
        if pool is not None:
            return rng.sample(pool, count) if count else []
        return [_generate(schema["items"], key, rng, sentences, context) for _ in range(count)]
    if kind == "string":
        if "enum" in schema:
            return rng.choice(schema["enum"])
        if key in QUOTE_KEYS:
            return rng.choice(sentences)
        pool = context.get(ID_POOLS.get(key, ""))
        if pool:
            return rng.choice(pool)
        if key == "ai_quote":
            return "[mock AI answer excerpt]"
        return f"[mock {key}]"
    if kind == "integer":
        return 0
    if kind == "number":
        return 0.0
    if kind == "boolean":
        return rng.random() < 0.5
    return None
