"""Assemble a review's working files into results.json, check it, and render the report.

Usage:
    python finalize.py <working-folder> [--platform claude-code] [--model <model>]

Reads from the working folder:
    document.md, source.json   written by prepare.py
    setup.json             inputs, analysis, assumptions, readers (ids + adaptations)
    reviews/<id>.json      one reader review each (persona-review-format.md)
    related-work.json      optional: the named-work check; specific works it doesn't list become not_checked
    key-sentences.json     optional: the key-sentence check (verdict + flags)
    synthesis.json         the synthesis output

Fills in what scripts can supply (run metadata, sections, the key-sentence outline,
persona text from the library, ranking, quality), validates against the schema, and
writes results.json, report.md, report.html, and summary.md. The results and reports name
the draft by filename rather than including its text. Exit code 1 means something needs
fixing; the errors say what.
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
TOOL_VERSION = "0.2.0"
READER_TYPES = {"nonexpert", "expert", "Expert", "gatekeeper"}


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


def front_matter(text):
    fields = {}
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return fields, text
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.split("#", 1)[0].strip()
    return fields, text[match.end():]


def adapted_persona(spec, workdir):
    raw = persona_file(spec["id"], workdir).read_text(encoding="utf-8").replace("\r\n", "\n")
    fields, text = front_matter(raw)
    lines = [f"- {a['parameter']}: {a['value']} ({a['reason']})" for a in spec.get("adaptations", [])]
    lines += [f"- Context this reader would have: {c}" for c in spec.get("added_context", [])]
    if lines:
        text = text.strip() + "\n\n## Adaptations for this draft\n\n" + "\n".join(lines)
    reader_type = fields.get("reader_type", "")
    briefing = fields.get("briefing", "")
    return {
        "id": spec["id"],
        "name": fields.get("name", spec["id"]),
        "reader_type": reader_type if reader_type in READER_TYPES else "custom",
        "briefing": briefing if briefing in ("briefed", "cold") else "briefed",
        "adaptations": spec.get("adaptations", []),
        "added_context": spec.get("added_context", []),
        "adapted_text": text.strip(),
    }


def content_hash():
    digest = hashlib.sha256()
    for path in sorted(SKILL_DIR.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            digest.update(str(path.relative_to(SKILL_DIR)).replace("\\", "/").encode())
            digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()[:16]


def related_work_block(reviews, data):
    """Every specific work a reader named, with its check status. Unlisted works are not_checked, never verified."""
    named = {}
    for review in reviews:
        for i, item in enumerate(review["output"]["related_work"], start=1):
            if item.get("specific"):
                named[f"{review['persona_id']}/rw{i}"] = item["work"]
    if not named and not data:
        return None
    data = data or {}
    listed = {item.get("ref"): item for item in data.get("items", [])}
    items = []
    for ref, work in named.items():
        item = dict(listed.get(ref) or {"status": "not_checked", "note": "Not looked up in this run."})
        item.update(ref=ref, work=item.get("work") or work)
        item.setdefault("url", None)
        item.setdefault("note", "")
        items.append(item)
    return {"method": data.get("method", "not_run"), "items": items}


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
        review.setdefault("related_work", [])
        reviews.append({"persona_id": p["id"], "output": review})

    sections = quality.split_sections(document)
    source = load_json(workdir / "source.json", required=False) or {}
    inputs = {"intended_claim": None, "stage": None, "venue": None, "feedback_wanted": None,
              "known_gaps": [], "prior_feedback": None, "persona_overrides": [],
              "house_settings": None}
    inputs.update(setup.get("inputs", {}))

    results = {
        "schema_version": "0.2",
        "run": {"id": uuid.uuid4().hex[:12], "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "tool_version": TOOL_VERSION, "content_hash": content_hash(), "model": model, "platform": platform},
        "document": {"title": setup.get("title"), "source_file": source.get("source_file"),
                     "working_copy": "document.md", "word_count": len(document.split()),
                     "sections": [{"id": x["id"], "label": x["label"]} for x in sections],
                     "key_sentences": quality.key_sentences(document, sections)},
        "inputs": inputs,
        "analysis": setup["analysis"],
        "assumptions": setup.get("assumptions", []),
        "personas": personas,
        "persona_reviews": reviews,
        "related_work_check": related_work_block(reviews, load_json(workdir / "related-work.json", required=False)),
        "key_sentence_check": load_json(workdir / "key-sentences.json", required=False),
        "synthesis": None,
        "quality": None,
    }
    synthesis_output = load_json(workdir / "synthesis.json", required=False)
    if synthesis_output is not None:
        results["synthesis"] = {"output": synthesis_output, "ranked_issues": [], "priority_actions": [],
                                "parked": []}
        try:
            ranked, priority, parked = quality.rank_issues(results, document)
        except KeyError as exc:
            raise SystemExit(f"synthesis.json: an issue is missing the field {exc}")
        results["synthesis"].update(ranked_issues=ranked, priority_actions=priority, parked=parked)
    results["quality"] = quality.compute_quality(results, document)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("workdir")
    parser.add_argument("--platform", default="claude-code")
    parser.add_argument("--model", default="unknown")
    args = parser.parse_args(argv)
    workdir = Path(args.workdir)
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to a legacy code page
    except (AttributeError, ValueError):
        pass

    results = assemble(workdir, args.platform, args.model)
    errors = validate(results)
    (workdir / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        print("results.json has problems to fix in the working files:")
        for error in errors[:30]:
            print(f"  - {error}")
        return 1

    (workdir / "report.md").write_text(render_markdown.render_report(results), encoding="utf-8")
    (workdir / "report.html").write_text(render_report.render_html(results), encoding="utf-8")
    summary = render_markdown.render_summary(results, report_path=workdir / "report.html")
    (workdir / "summary.md").write_text(summary, encoding="utf-8")
    unverified = results["quality"]["anchoring"]["unverified"]
    if unverified:
        print(f"note: {len(unverified)} quote(s) not found verbatim in the draft: "
              + ", ".join(u["finding_ref"] for u in unverified))
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
