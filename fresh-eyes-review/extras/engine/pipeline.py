"""Run one review of one document under one execution condition and return results.json content.

Conditions (see the Validation plan in the build spec):
    A  single context, all personas in sequence, no information-restriction instructions
    B  single context, all personas in sequence, explicit "this reader does not know X"
    C  isolated: one fresh context per persona, background routed by access tier
    D  isolated, every persona gets the full background
    E  baseline: one generic senior-lawyer review, no persona
"""

import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import quality  # the skill's scripts/quality.py

from . import TOOL_VERSION, prompts
from .model import estimate_cost
from .references import adapt_persona, content_hash, git_commit, model_schema

CONDITIONS = {
    "A": {"execution": "single", "routing": "full", "restrict": False},
    "B": {"execution": "single", "routing": "full", "restrict": True},
    "C": {"execution": "isolated", "routing": "tier"},
    "D": {"execution": "isolated", "routing": "full"},
    "E": {"execution": "baseline", "routing": "full"},
}


class Recorder:
    """Collects every model call verbatim (with the document text swapped for a marker)."""

    def __init__(self, document):
        self.document = document
        self.records = []
        self.counts = {}

    def _scrub(self, text):
        return text.replace(self.document, prompts.DOCUMENT_MARKER) if self.document else text

    def add(self, stage, persona_id, system, messages, result, prompt_id=None):
        if prompt_id is None:
            base = f"{stage}-{persona_id}" if persona_id else stage
            self.counts[base] = self.counts.get(base, 0) + 1
            prompt_id = base if self.counts[base] == 1 else f"{base}-{self.counts[base]}"
        flat = [{"role": m["role"], "content": self._scrub(_flatten(m["content"]))} for m in messages]
        self.records.append({
            "id": prompt_id, "stage": stage, "persona_id": persona_id,
            "system": self._scrub(system) if system else None, "messages": flat,
            "response_text": result.text, "stop_reason": result.stop_reason,
            "usage": result.usage, "duration_seconds": round(result.duration, 3),
        })
        return prompt_id


def _flatten(content):
    if isinstance(content, str):
        return content
    return "\n\n".join(block.get("text", "") for block in content)


def build_personas(config, condition):
    background = config.get("background", [])
    if condition == "E":
        return [{"id": "baseline", "name": "Senior lawyer (no persona)", "tier": "none", "role": "baseline",
                 "adaptations": [], "added_context": [], "background_ids": [b["id"] for b in background],
                 "adapted_text": prompts.BASELINE_TASK}]
    records = []
    for spec in config["personas"]:
        fields, text = adapt_persona(spec["id"], spec.get("adaptations", []), spec.get("added_context", []))
        tier = fields.get("tier", "C")
        if CONDITIONS[condition]["routing"] == "tier":
            allowed = [b for b in background if b["sensitivity"] in prompts.TIER_ACCESS[tier]]
        else:
            allowed = list(background)
        records.append({"id": spec["id"], "name": fields.get("name", spec["id"]), "tier": tier,
                        "role": spec.get("role", "primary"), "adaptations": spec.get("adaptations", []),
                        "added_context": spec.get("added_context", []),
                        "background_ids": [b["id"] for b in allowed], "adapted_text": text})
    return records


def _context(config, sections, **extra):
    ctx = {"document": config["document"], "section_ids": [s["id"] for s in sections]}
    ctx.update(extra)
    return ctx


def run_persona_reviews(config, condition, personas, sections, client, recorder, workers):
    schema = model_schema("persona_review_output")
    system = prompts.review_system()
    background = config.get("background", [])
    by_id = {b["id"]: b for b in background}
    goal = config.get("goal")
    execution = CONDITIONS[condition]["execution"]
    reviews = []

    if execution == "single":
        restrict = CONDITIONS[condition]["restrict"]
        intro_items = list(background) + ([{"id": "goal", "text": f"Author's goal: {goal}"}] if goal else [])
        messages = []
        for index, persona in enumerate(personas):
            restricted = None
            if restrict:
                allowed = prompts.TIER_ACCESS[persona["tier"]]
                restricted = [b for b in background if b["sensitivity"] not in allowed] or None
            task = prompts.persona_task(persona, restricted_items=restricted)
            if index == 0:
                content = [prompts.document_block(config["document"], sections),
                           {"type": "text", "text": prompts.single_context_intro(intro_items) + "\n\n" + task}]
            else:
                content = task
            messages.append({"role": "user", "content": content})
            result = client.call(system=system, messages=messages, schema=schema,
                                 context=_context(config, sections), label=f"{condition}:{persona['id']}")
            pid = recorder.add("persona_review", persona["id"], system, list(messages), result)
            messages.append({"role": "assistant", "content": result.text})
            reviews.append({"persona_id": persona["id"], "prompt_ids": [pid], "output": result.parsed})
        return reviews

    def one(persona):
        items = [by_id[i] for i in persona["background_ids"]]
        persona_goal = goal if persona["tier"] in ("A", "none") else None
        text = prompts.BASELINE_TASK if persona["id"] == "baseline" else prompts.persona_task(
            persona, items, goal=persona_goal)
        if persona["id"] == "baseline":
            text = (f"<background>\n{prompts.background_text(items)}\n</background>\n\n"
                    + (f"<author_goal>\n{goal}\n</author_goal>\n\n" if goal else "") + text)
        messages = [{"role": "user", "content": [prompts.document_block(config["document"], sections),
                                                 {"type": "text", "text": text}]}]
        result = client.call(system=system, messages=messages, schema=schema,
                             context=_context(config, sections), label=f"{condition}:{persona['id']}")
        return persona, messages, result

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for persona, messages, result in pool.map(one, personas):
            pid = recorder.add("persona_review", persona["id"], system, messages, result)
            reviews.append({"persona_id": persona["id"], "prompt_ids": [pid], "output": result.parsed})
    return reviews


def run_ai_reader(config, analysis, client, workers=4):
    """Run the AI-reader batteries in fresh contexts, then the survival check.

    Returns (ai_reader block, prompt records). Independent of the persona condition, so the
    harness can run it once and share it across conditions.
    """
    spec = config.get("ai_reader")
    if not spec:
        return None, []
    recorder = Recorder(config["document"])
    batteries = prompts.ai_reader_batteries()
    jobs = [(battery, number, prompt) for battery in spec["batteries"] for number, prompt in batteries[battery]]

    def one(job):
        battery, number, prompt = job
        messages = [{"role": "user", "content": prompts.ai_reader_message(config["document"], prompt)}]
        result = client.call(system=None, messages=messages, schema=None,
                             context={"document": config["document"]}, label=f"ai-{number}")
        return job, messages, result

    answers = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for (battery, number, prompt), messages, result in pool.map(one, jobs):
            pid = recorder.add("ai_reader", None, None, messages, result, prompt_id=f"ai-{number}")
            answers.append({"prompt_id": pid, "number": number, "battery": battery,
                            "prompt": prompt, "answer": result.text})

    system = prompts.survival_system(analysis)
    messages = [{"role": "user", "content": prompts.survival_user(config["document"], answers)}]
    result = client.call(system=system, messages=messages, schema=model_schema("survival_check_output"),
                         context={"document": config["document"], "prompt_ids": [a["prompt_id"] for a in answers]},
                         label="survival")
    recorder.add("survival_check", None, system, messages, result, prompt_id="survival-check")
    block = {"method": "fresh_context", "model": client.model, "recipient": spec["recipient"], "batteries": spec["batteries"],
             "answers": answers, "survival_check": result.parsed}
    return block, recorder.records


def build_analysis(config, personas):
    a = dict(config["analysis"])
    goal = config.get("goal")
    a["goal"] = {"text": goal or a.get("inferred_goal", ""), "source": "stated" if goal else "inferred"}
    a.pop("inferred_goal", None)
    names = ", ".join(p["name"] for p in personas)
    recipient = (config.get("ai_reader") or {}).get("recipient")
    a["plan_line"] = (f"Read as a {a['document_type']}. Goal ({a['goal']['source']}): {a['goal']['text']} "
                      f"Readers: {names}." + (f" AI-reader check as {recipient}." if recipient else ""))
    return a


def run(config, condition, client, *, ai_reader=None, run_synthesis=True, workers=4, platform="harness"):
    """Run one condition on one document. ai_reader=(block, records) reuses a shared AI-reader run."""
    if condition not in CONDITIONS:
        raise ValueError(f"Unknown condition {condition!r}; expected one of {sorted(CONDITIONS)}")
    start = time.monotonic()
    document = config["document"]
    sections = quality.split_sections(document)
    recorder = Recorder(document)
    personas = build_personas(config, condition)
    analysis = build_analysis(config, personas)

    reviews = run_persona_reviews(config, condition, personas, sections, client, recorder, workers)

    ai_block, ai_records = ai_reader if ai_reader is not None else run_ai_reader(config, analysis, client, workers)

    results = {
        "schema_version": "0.1",
        "run": {
            "id": uuid.uuid4().hex[:12],
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "tool_version": TOOL_VERSION,
            "content_hash": content_hash(),
            "git_commit": git_commit(),
            "model": client.model,
            "execution": CONDITIONS[condition]["execution"],
            "condition": condition,
            "mode": config.get("mode", "fast"),
            "platform": platform,
            "usage": {},
            "duration_seconds": 0.0,
        },
        "document": {"title": config.get("title"), "text": document,
                     "word_count": len(document.split()), "sections": sections},
        "inputs": {"goal": config.get("goal"), "audience": config.get("audience"),
                   "background": config.get("background", []),
                   "persona_overrides": [p["id"] for p in config.get("personas", [])],
                   "house_settings": config.get("house_settings")},
        "analysis": analysis,
        "assumptions": config.get("assumptions", []),
        "personas": personas,
        "persona_reviews": reviews,
        "ai_reader": ai_block,
        "synthesis": None,
        "quality": None,
        "prompts": [],
    }

    if run_synthesis:
        gaps = quality.attention_gaps(results)
        review_gaps = quality.review_gaps(results)
        system = prompts.synthesis_system()
        messages = [{"role": "user", "content": prompts.synthesis_user(results, gaps, review_gaps)}]
        refs = [ref for ref, _, _ in quality.iter_findings(results)]
        ctx = {"document": document, "finding_refs": refs, "persona_ids": [p["id"] for p in personas],
               "prompt_ids": [a["prompt_id"] for a in (ai_block or {}).get("answers", [])],
               "assumption_ids": [a["id"] for a in results["assumptions"]], "section_ids": [s["id"] for s in sections]}
        result = client.call(system=system, messages=messages, schema=model_schema("synthesis_output"),
                             context=ctx, label=f"{condition}:synthesis")
        recorder.add("synthesis", None, system, messages, result, prompt_id="synthesis")
        results["synthesis"] = {"output": result.parsed, "ranked_issues": [], "priority_actions": [],
                                "reader_specific": []}
        ranked, priority, reader_specific = quality.rank_issues(results)
        results["synthesis"].update(ranked_issues=ranked, priority_actions=priority, reader_specific=reader_specific)

    results["prompts"] = recorder.records + list(ai_records)
    results["quality"] = quality.compute_quality(results)

    totals = {"calls": 0, "input_tokens": 0, "output_tokens": 0,
              "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    for record in results["prompts"]:
        totals["calls"] += 1
        for key in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"):
            totals[key] += record["usage"][key]
    totals["estimated_cost_usd"] = estimate_cost(client.model, totals)
    results["run"]["usage"] = totals
    results["run"]["duration_seconds"] = round(time.monotonic() - start, 2)
    return results
