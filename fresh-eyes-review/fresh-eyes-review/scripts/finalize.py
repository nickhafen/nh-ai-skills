"""Assemble a review's working files into results.json, check it, and render the report.

Usage:
    python finalize.py <working-folder> [--platform claude-code] [--model <model>]

Reads from the working folder:
    document.md            written by prepare.py
    setup.json             inputs, analysis, assumptions, personas (ids + adaptations)
    reviews/<id>.json      one persona review each (persona-review-format.md)
    ai-reader.json         optional: recipient, batteries, answers, survival_check
    synthesis.json         the synthesis output

Fills in what scripts can supply (run metadata, sections, persona text from the
library, ranking, quality), validates against the schema, and writes results.json,
report.md, and summary.md. Exit code 1 means something needs fixing; the errors say what.
"""

import argparse
import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import quality
import render_markdown
import render_report
from validate_results import validate

SKILL_DIR = Path(__file__).resolve().parent.parent
PERSONA_DIR = SKILL_DIR / "references" / "personas"
TOOL_VERSION = "0.1.0"


def load_json(path, required=True):
    if not path.exists():
        if required:
            raise SystemExit(f"Missing {path.name} in {path.parent}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path.name} is not valid JSON: {exc}")


def persona_file(persona_id, workdir):
    """Library persona, or a custom one saved in the working folder's personas/ folder."""
    for folder in (workdir / "personas", PERSONA_DIR):
        path = folder / f"{persona_id}.md"
        if path.exists():
            return path
    raise SystemExit(f"No persona file for '{persona_id}'. Use a library id, or save a custom persona "
                     f"to {workdir / 'personas' / (persona_id + '.md')}")


def adapted_persona(spec, workdir):
    text = persona_file(spec["id"], workdir).read_text(encoding="utf-8").replace("\r\n", "\n")
    fields = {}
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if match:
        text = text[match.end():]
        for line in match.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                fields[key.strip()] = value.split("#", 1)[0].strip()
    lines = [f"- {a['parameter']}: {a['value']} ({a['reason']})" for a in spec.get("adaptations", [])]
    lines += [f"- Context this reader would have: {c}" for c in spec.get("added_context", [])]
    if lines:
        text = text.strip() + "\n\n## Adaptations for this document\n\n" + "\n".join(lines)
    return {
        "id": spec["id"],
        "name": fields.get("name", spec["id"]),
        "tier": fields.get("tier", "C"),
        "role": spec.get("role", "primary"),
        "adaptations": spec.get("adaptations", []),
        "added_context": spec.get("added_context", []),
        "background_ids": spec.get("background_ids", []),
        "adapted_text": text.strip(),
    }


def content_hash():
    digest = hashlib.sha256()
    for path in sorted(SKILL_DIR.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            digest.update(str(path.relative_to(SKILL_DIR)).replace("\\", "/").encode())
            digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()[:16]


def assemble(workdir, platform, model):
    document = (workdir / "document.md").read_text(encoding="utf-8").strip()
    setup = load_json(workdir / "setup.json")
    personas = [adapted_persona(spec, workdir) for spec in setup["personas"]]

    reviews = []
    for p in personas:
        review = load_json(workdir / "reviews" / f"{p['id']}.json", required=False)
        if review is None:
            print(f"warning: no review for {p['id']}", file=sys.stderr)
            continue
        review.pop("persona_id", None)
        reviews.append({"persona_id": p["id"], "prompt_ids": [], "output": review})

    ai = load_json(workdir / "ai-reader.json", required=False)
    prompts = []
    if ai:
        for a in ai["answers"]:
            a["prompt_id"] = a.get("prompt_id") or f"ai-{a['number']}"
            if a.get("answer") is not None:
                prompts.append({"id": a["prompt_id"], "stage": "ai_reader", "persona_id": None, "system": None,
                                "messages": [{"role": "user", "content": f"[[DOCUMENT]]\n\n{a['prompt']}"}],
                                "response_text": a["answer"], "stop_reason": None,
                                "usage": {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0,
                                          "cache_creation_input_tokens": 0},
                                "duration_seconds": 0.0})
        ai.setdefault("model", model)
        if not any(a.get("answer") for a in ai["answers"]):
            ai.setdefault("method", "not_run")
        ai.setdefault("survival_check", None)

    synthesis_output = load_json(workdir / "synthesis.json", required=False)
    inputs = setup.get("inputs", {})
    results = {
        "schema_version": "0.1",
        "run": {
            "id": uuid.uuid4().hex[:12],
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "tool_version": TOOL_VERSION,
            "content_hash": content_hash(),
            "git_commit": None,
            "model": model,
            "execution": "single",
            "condition": None,
            "mode": setup.get("mode", "fast"),
            "platform": platform,
            "usage": {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0,
                      "cache_creation_input_tokens": 0, "estimated_cost_usd": None},
            "duration_seconds": 0.0,
        },
        "document": {"title": setup.get("title"), "text": document, "word_count": len(document.split()),
                     "sections": quality.split_sections(document)},
        "inputs": {"goal": inputs.get("goal"), "audience": inputs.get("audience"),
                   "background": inputs.get("background", []),
                   "persona_overrides": inputs.get("persona_overrides", []),
                   "house_settings": inputs.get("house_settings")},
        "analysis": setup["analysis"],
        "assumptions": setup.get("assumptions", []),
        "personas": personas,
        "persona_reviews": reviews,
        "ai_reader": ai,
        "synthesis": None,
        "quality": None,
        "prompts": prompts,
    }
    if synthesis_output is not None:
        results["synthesis"] = {"output": synthesis_output, "ranked_issues": [], "priority_actions": [],
                                "reader_specific": []}
        ranked, priority, reader_specific = quality.rank_issues(results)
        results["synthesis"].update(ranked_issues=ranked, priority_actions=priority, reader_specific=reader_specific)
    results["quality"] = quality.compute_quality(results)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("workdir")
    parser.add_argument("--platform", default="claude-code")
    parser.add_argument("--model", default="unknown")
    args = parser.parse_args(argv)
    workdir = Path(args.workdir)

    results = assemble(workdir, args.platform, args.model)
    errors = validate(results)
    (workdir / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        print("results.json has problems to fix in the working files:")
        for error in errors[:30]:
            print(f"  - {error}")
        return 1

    report = render_markdown.render_report(results)
    (workdir / "report.md").write_text(report, encoding="utf-8")
    (workdir / "report.html").write_text(render_report.render_html(results), encoding="utf-8")
    summary = render_markdown.render_summary(results, report_path=workdir / "report.html")
    (workdir / "summary.md").write_text(summary, encoding="utf-8")
    unverified = results["quality"]["anchoring"]["unverified"]
    if unverified:
        print(f"note: {len(unverified)} quote(s) not found verbatim in the document: "
              + ", ".join(u["finding_ref"] for u in unverified))
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
