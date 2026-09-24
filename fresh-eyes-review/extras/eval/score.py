"""Score a harness batch against the fixture's answer key and summarize by condition.

Usage:
    python eval/score.py eval/results/<fixture>/<batch>
    python eval/score.py <batch> --grader anthropic   # add model-graded checks (costs API calls)

Writes scores.json in each run folder and summary.json + summary.md in the batch folder.

Scored by script: seeded recall (overall and per persona), decoy false positives,
leakage rate, curse-of-knowledge catch rate, anchoring rate, distinctiveness,
stance spread, persona effect vs. baseline (E), cost, and latency.
With --grader: string-match misses are rechecked by a model, and main-point
agreement is graded. Precision and blind usefulness need a human (see
unmatched_findings in scores.json).
"""

import argparse
import json
import statistics
import sys
from pathlib import Path

EXTRAS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(EXTRAS_DIR))

import engine  # noqa: E402,F401  (puts the skill scripts on the path)
import quality  # noqa: E402

GRADER_SCHEMA = {
    "type": "object",
    "properties": {"caught": {"type": "boolean"}, "reason": {"type": "string"}},
    "required": ["caught", "reason"], "additionalProperties": False,
}
MAIN_POINT_SCHEMA = {
    "type": "object",
    "properties": {"agreement": {"type": "string", "enum": ["yes", "partly", "no"]}, "reason": {"type": "string"}},
    "required": ["agreement", "reason"], "additionalProperties": False,
}


# ---------- matching ----------

def candidate_items(review):
    """Findings plus look-for checks marked unclear or missing, as (text, quote) pairs."""
    out = review["output"]
    items = [(f"{f['issue']} {f['why_it_matters']}", f["quote"]) for f in out.get("findings", [])]
    items += [(f"{c['item']} {c['note']}", c.get("quote") or "")
              for c in out.get("look_for", []) if c["status"] != "clear"]
    return items


def anchor_overlaps(anchor, quote):
    if not anchor or not quote:
        return False
    a, q = quality.normalize(anchor), quality.normalize(quote)
    if (len(q) >= 15 and q in a) or (len(a) >= 15 and a in q):
        return True
    wa, wq = quality.words(anchor), quality.words(quote)
    return bool(wa) and len(wa & wq) / len(wa | wq) >= 0.5


def keyword_hit(keywords, text):
    t = quality.normalize(text)
    return any(quality.normalize(k) in t for k in keywords)


def matches(issue, text, quote):
    """Keywords are checked against what the reader said (text), never the quote, so that
    'anchor+keywords' requires both the right passage and the right problem."""
    a = anchor_overlaps(issue.get("anchor"), quote)
    k = keyword_hit(issue.get("keywords", []), text)
    return {"anchor": a, "keywords": k, "anchor+keywords": a and k}[issue["match"]]


# ---------- per-run scoring ----------

def score_run(results, key, grader=None):
    reviews = {r["persona_id"]: r for r in results["persona_reviews"]}
    tiers = {p["id"]: p["tier"] for p in results["personas"]}
    issues = key["issues"]
    seeded = [i for i in issues if i["type"] in ("convergent", "persona-specific", "curse-of-knowledge")]

    caught = {}  # (issue_id, persona_id) -> bool
    for issue in seeded + [i for i in issues if i["type"] == "decoy"]:
        for pid, review in reviews.items():
            hit = any(matches(issue, text, quote) for text, quote in candidate_items(review))
            if not hit and grader and issue["type"] != "decoy" and pid in issue["expected_personas"]:
                hit = grade_issue(grader, issue, review)
            caught[(issue["id"], pid)] = hit

    recall_overall = _rate(sum(any(caught[(i["id"], p)] for p in reviews) for i in seeded), len(seeded))
    per_persona = {}
    for pid in reviews:
        expected = [i for i in seeded if pid in i["expected_personas"]]
        if expected:
            per_persona[pid] = _rate(sum(caught[(i["id"], pid)] for i in expected), len(expected))

    decoys = [i for i in issues if i["type"] == "decoy"]
    decoy_hits = sum(any(caught[(d["id"], p)] for p in reviews) for d in decoys)

    probes = [i for i in issues if i["type"] == "leakage-probe"]
    tier_c = [pid for pid in reviews if tiers.get(pid) == "C"]
    leaked = []
    for pid in tier_c:
        text = json.dumps(reviews[pid]["output"], ensure_ascii=False)
        if any(keyword_hit(p["keywords"], text) for p in probes):
            leaked.append(pid)
    leakage_rate = _rate(len(leaked), len(tier_c)) if probes else None

    cok = [i for i in issues if i["type"] == "curse-of-knowledge"]
    uninformed = [pid for pid in reviews if tiers.get(pid) in ("B", "C")]
    cok_rate = _rate(sum(any(caught[(i["id"], p)] for p in uninformed) for i in cok), len(cok)) if cok else None

    all_items = [(pid, text, quote) for pid, r in reviews.items() for text, quote in candidate_items(r)]
    unmatched = [{"persona_id": pid, "text": text, "quote": quote} for pid, text, quote in all_items
                 if not any(matches(i, text, quote) for i in issues if i["type"] != "leakage-probe")]

    main_point = None
    if grader:
        goal = results["analysis"]["goal"]["text"]
        main_point = {pid: grade_main_point(grader, goal, r["output"]["main_point"]) for pid, r in reviews.items()}

    q = results["quality"]
    pairs = q["distinctiveness"]["pairs"]
    return {
        "condition": results["run"]["condition"],
        "seeded_recall": recall_overall,
        "recall_by_persona": per_persona,
        "caught": {f"{i}|{p}": v for (i, p), v in caught.items()},
        "decoy_false_positives": decoy_hits,
        "leakage_rate": leakage_rate,
        "leaked_personas": leaked,
        "curse_of_knowledge_catch_rate": cok_rate,
        "anchoring_rate": q["anchoring"]["rate"],
        "mean_overlap": round(statistics.mean(p["overlap"] for p in pairs), 3) if pairs else None,
        "stance_spread": _rate(q["stance_spread"]["distinct_actions"], q["stance_spread"]["personas"]),
        "main_point_agreement": main_point,
        "findings_total": len(all_items),
        "unmatched_findings": unmatched,
        "calls": results["run"]["usage"]["calls"],
        "tokens": results["run"]["usage"]["input_tokens"] + results["run"]["usage"]["output_tokens"],
        "cost_usd": results["run"]["usage"]["estimated_cost_usd"],
        "duration_seconds": results["run"]["duration_seconds"],
    }


def _rate(n, d):
    return round(n / d, 3) if d else None


def grade_issue(grader, issue, review):
    prompt = (f"A reviewer was expected to notice this issue in a legal document:\n{issue['description']}\n\n"
              f"Here is the reviewer's output:\n{json.dumps(review['output'], ensure_ascii=False)}\n\n"
              "Did the reviewer identify substantially the same issue? Answer strictly.")
    result = grader.call(system=None, messages=[{"role": "user", "content": prompt}], schema=GRADER_SCHEMA,
                         label=f"grade:{issue['id']}:{review['persona_id']}")
    return bool(result.parsed["caught"])


def grade_main_point(grader, goal, main_point):
    prompt = (f"Author's goal: {goal}\n\nA reader's one-sentence understanding of the document: {main_point}\n\n"
              "Does the reader's understanding match what the author wants the reader to understand and do?")
    result = grader.call(system=None, messages=[{"role": "user", "content": prompt}], schema=MAIN_POINT_SCHEMA,
                         label="grade:main-point")
    return result.parsed["agreement"]


# ---------- persona effect (needs E in the same batch) ----------

def persona_effect(results, baseline):
    """Share of each persona's findings with no close counterpart in the baseline run (higher = more distinct)."""
    base = [quality.words(f["quote"]) | quality.words(f["issue"]) for f in baseline["persona_reviews"][0]["output"]["findings"]]
    effect = {}
    for review in results["persona_reviews"]:
        mine = [quality.words(f["quote"]) | quality.words(f["issue"]) for f in review["output"]["findings"]]
        if not mine:
            continue
        novel = sum(1 for m in mine if not any(len(m & b) / max(len(m | b), 1) >= 0.35 for b in base))
        effect[review["persona_id"]] = round(novel / len(mine), 3)
    return effect


# ---------- summary ----------

SUMMARY_METRICS = ["seeded_recall", "curse_of_knowledge_catch_rate", "leakage_rate", "decoy_false_positives",
                   "anchoring_rate", "mean_overlap", "stance_spread", "persona_effect_mean",
                   "calls", "tokens", "cost_usd", "duration_seconds"]


def summarize(scores):
    by_condition = {}
    for s in scores:
        by_condition.setdefault(s["condition"], []).append(s)
    summary = {}
    for condition, runs in sorted(by_condition.items()):
        row = {"runs": len(runs)}
        for metric in SUMMARY_METRICS:
            values = [r[metric] for r in runs if r.get(metric) is not None]
            if values:
                row[metric] = {"mean": round(statistics.mean(values), 3),
                               "sd": round(statistics.stdev(values), 3) if len(values) > 1 else 0.0}
        summary[condition] = row
    return summary


def summary_markdown(summary, manifest):
    lines = [f"# Scores: {manifest['fixture']} / {manifest['batch']}", "",
             f"Client: {manifest['client']} · model: {manifest['model']} · content hash: {manifest['content_hash']}"
             f" · commit: {manifest['git_commit']}", ""]
    if manifest["client"] == "mock":
        lines += ["> Mock client: these numbers test the pipeline only and say nothing about quality.", ""]
    lines += ["Values are mean ± sd across runs.", "",
              "| Metric | " + " | ".join(summary) + " |", "| --- |" + " --- |" * len(summary)]
    for metric in SUMMARY_METRICS:
        cells = []
        for condition in summary:
            v = summary[condition].get(metric)
            cells.append(f"{v['mean']} ± {v['sd']}" if v else "—")
        lines.append(f"| {metric} | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("batch")
    parser.add_argument("--grader", choices=["none", "anthropic", "mock"], default="none")
    parser.add_argument("--grader-model", default="claude-opus-5")
    args = parser.parse_args(argv)

    batch = Path(args.batch)
    manifest = json.loads((batch / "manifest.json").read_text(encoding="utf-8"))
    key = json.loads((EXTRAS_DIR / manifest["fixture"] / "answer_key.json").read_text(encoding="utf-8"))
    grader = None
    if args.grader == "anthropic":
        from engine.model import AnthropicClient
        grader = AnthropicClient(model=args.grader_model, effort="medium")
    elif args.grader == "mock":
        from engine.model import MockClient
        grader = MockClient()

    loaded = {}
    for entry in manifest["results"]:
        if entry["status"] == "ok":
            loaded[entry["label"]] = json.loads((batch / entry["path"]).read_text(encoding="utf-8"))

    scores = []
    for label, results in loaded.items():
        s = score_run(results, key, grader)
        run_k = label.split("-run")[1]
        baseline = loaded.get(f"E-run{run_k}")
        if baseline and results["run"]["condition"] != "E":
            effect = persona_effect(results, baseline)
            s["persona_effect"] = effect
            s["persona_effect_mean"] = round(statistics.mean(effect.values()), 3) if effect else None
        (batch / label / "scores.json").write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")
        scores.append(s)

    summary = summarize(scores)
    (batch / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    md = summary_markdown(summary, manifest)
    (batch / "summary.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
