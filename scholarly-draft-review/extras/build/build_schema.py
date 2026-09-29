"""Generate the skill's assets/results.schema.json.

Usage (from extras/):
    python build/build_schema.py           # write the schema
    python build/build_schema.py --check   # exit 1 if the schema file is out of date

Edit the schema here, not in the JSON file. Model-written objects follow structured-output
limits (every object closed, every field required, nullable fields as anyOf with null,
no numeric or length limits), so the same $defs could later be sent to an API.
"""

import argparse
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "scholarly-draft-review" / "assets" / "results.schema.json"

STR = {"type": "string"}
INT = {"type": "integer"}
NUM = {"type": "number"}
BOOL = {"type": "boolean"}
STAGES = ["idea", "early", "full", "workshop", "submission"]


def obj(description=None, **props):
    schema = {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}
    if description:
        schema["description"] = description
    return schema


def arr(items):
    return {"type": "array", "items": items}


def enum(*values):
    return {"type": "string", "enum": list(values)}


def null(schema):
    return {"anyOf": [schema, {"type": "null"}]}


def ref(name):
    return {"$ref": f"#/$defs/{name}"}


SEVERITY = enum("high", "medium", "low")

DEFS = {
    "look_for_check": obj(
        "One item from the persona's 'What they look for' section.",
        item=STR, status=enum("clear", "unclear_or_buried", "missing", "not_applicable"), quote=null(STR), note=STR),
    "finding": obj(
        "A single anchored finding. quote must be verbatim from the draft.",
        quote=STR, issue=STR, why_it_matters=STR, severity=SEVERITY),
    "passage_note": obj(quote=STR, note=STR),
    "related_work_item": obj(
        "A work or kind of work a reader points to. specific=true names a particular work, author, or case.",
        work=STR, specific=BOOL, why=STR, confidence=SEVERITY),
    "persona_review_output": obj(
        "What each reader returns. See references/persona-review-format.md.",
        main_point=STR, look_for=arr(ref("look_for_check")), findings=arr(ref("finding")),
        what_works=arr(ref("passage_note")), related_work=arr(ref("related_work_item"))),
    "key_sentence_output": obj(
        "The key-sentence check. See SKILL.md step 6.",
        verdict=STR, flags=arr(obj(paragraph_id=STR, quote=STR, issue=STR))),
    "synthesis_output": obj(
        "What the synthesis writes. See references/synthesis-rubric.md.",
        issues=arr(obj(
            title=STR, quote=STR, summary=STR, finding_refs=arr(STR), reasons=arr(obj(reader=STR, reason=STR)),
            severity=SEVERITY, category=enum("finding", "claim_mismatch", "key_sentence"),
            timing=enum("now", "later"), direction=STR)),
        dropped_findings=arr(obj(
            finding_ref=STR,
            rule=enum("no_anchor", "no_goal_link", "substance", "unverified_source", "out_of_lane", "known_gap",
                      "leaked_knowledge"),
            note=STR)),
        tradeoffs=arr(obj(quote=STR, sides=arr(obj(reader=STR, wants=STR, why=STR)), note=STR)),
        whats_working=arr(obj(quote=STR, readers=arr(STR), note=STR)),
        feedback_plan=arr(obj(who=STR, when=enum("now", "next_draft", "before_submission"), ask=STR, why=STR))),
    "section": obj(id=STR, label=STR),
    "key_sentence": obj(id=STR, section_id=null(STR), text=STR),
    "persona_record": obj(
        "A reader as adapted for this run.",
        id=STR, name=STR, reader_type=enum("nonexpert", "expert", "Expert", "gatekeeper", "custom"),
        briefing=enum("briefed", "cold"),
        adaptations=arr(obj(parameter=STR, value=STR, reason=STR)), added_context=arr(STR), adapted_text=STR),
}

sourced = lambda: obj(text=STR, source=enum("stated", "inferred"))  # noqa: E731

PROPERTIES = {
    "schema_version": {"const": "0.2"},
    "run": obj(id=STR, created_at=STR, tool_version=STR, content_hash=STR, model=STR, platform=STR),
    "document": obj(title=null(STR), source_file=null(STR), working_copy=STR, word_count=INT,
                    sections=arr(ref("section")), key_sentences=arr(ref("key_sentence"))),
    "inputs": obj(intended_claim=null(STR), stage=null(enum(*STAGES)), venue=null(STR),
                  feedback_wanted=null(STR), known_gaps=arr(STR), prior_feedback=null(STR),
                  persona_overrides=arr(STR), house_settings=null(STR)),
    "analysis": obj(
        piece_type=STR,
        stage=obj(id=enum(*STAGES), source=enum("stated", "inferred"), basis=STR),
        venue=null(STR), field=STR, prescriptive=BOOL, claim=sourced(), stage_focus=STR, plan_line=STR),
    "assumptions": arr(obj(id=STR, text=STR, basis=STR, confirmed=BOOL)),
    "personas": arr(ref("persona_record")),
    "persona_reviews": arr(obj(persona_id=STR, output=ref("persona_review_output"))),
    "related_work_check": null(obj(
        method=enum("searched", "not_run"),
        items=arr(obj(ref=STR, work=STR, status=enum("verified", "cited_in_draft", "not_found", "not_checked"),
                      url=null(STR), note=STR)))),
    "key_sentence_check": null(ref("key_sentence_output")),
    "synthesis": null(obj(
        output=ref("synthesis_output"),
        ranked_issues=arr(obj(issue_index=INT, rank=INT, score=NUM, readers=INT, convergent=BOOL, timing=enum("now", "later"))),
        priority_actions=arr(INT), parked=arr(INT))),
    "quality": obj(
        anchoring=obj(total=INT, verified=INT, unverified=arr(obj(finding_ref=STR, quote=STR))),
        related_work=obj(specific=INT, verified=INT, cited_in_draft=INT, not_found=INT, not_checked=INT),
        limitations=arr(obj(title=STR, text=STR, scope=enum("standing", "run")))),
}


def schema():
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "scholarly-draft-review results",
        "description": "One run of scholarly-draft-review. Every output format is rendered from this file. "
                       "See references/output-spec.md. Generated by extras/build/build_schema.py; don't edit by hand.",
        "type": "object",
        "additionalProperties": False,
        "required": list(PROPERTIES),
        "properties": PROPERTIES,
        "$defs": DEFS,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    text = json.dumps(schema(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else None
        if current != text:
            print(f"{OUT.name} is out of date. Run python build/build_schema.py")
            return 1
        print(f"{OUT.name} is up to date.")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
