"""Render a results.json as a markdown report (and a short chat summary).

Usage:
    python render_markdown.py results.json [--out report.md] [--summary]

Section order follows references/output-spec.md. Formatting only: every word of
content comes from results.json.
"""

import argparse
import json
import sys
from pathlib import Path

SEVERITY_LABEL = {"high": "High", "medium": "Medium", "low": "Low"}
STATUS_LABEL = {"clear": "Clear", "unclear_or_buried": "Unclear or buried", "missing": "Missing", "not_applicable": "n/a"}
ATTENTION_LABEL = {"read_closely": "read closely", "skimmed": "skimmed", "skipped": "skipped"}
SURVIVAL_LABEL = {"ask": "The ask", "deadline": "The deadline", "leverage": "The key point",
                  "characterization": "How the document is characterized", "advice": "The suggested response"}
RESULT_LABEL = {"yes": "Came through", "partly": "Partly came through", "no": "Lost", "not_applicable": "n/a"}


def quote(text):
    text = " ".join((text or "").split())
    return f"> “{text}”" if text else ""


def names(results):
    table = {p["id"]: p["name"] for p in results["personas"]}
    table["ai-reader"] = "AI reader"
    return table


def reader_list(ids, table):
    return ", ".join(table.get(i, i) for i in ids)


def issue_readers(issue):
    return sorted({r["reader"] for r in issue.get("reasons", [])} | {ref.split("/")[0] for ref in issue["finding_refs"]})


def render_report(results):
    table = names(results)
    a = results["analysis"]
    out = [f"# Fresh-eyes review: {results['document'].get('title') or a['document_type']}", ""]
    out += [f"**Plan.** {a['plan_line']}", ""]
    if a["goal"]["source"] == "inferred":
        out += [f"**Goal (inferred — correct me if this is wrong):** {a['goal']['text']}", ""]
    out += ["*These are simulated readers: treat their reactions as likely, not certain. This is a review of how "
            "the writing lands, not of whether the law or facts are right.*", ""]

    synthesis = results.get("synthesis")
    issues = synthesis["output"]["issues"] if synthesis else []
    ranked = {r["issue_index"]: r for r in synthesis["ranked_issues"]} if synthesis else {}

    # Priority actions
    if synthesis:
        out += ["## Priority actions", ""]
        for n, index in enumerate(synthesis["priority_actions"], start=1):
            issue = issues[index]
            tags = [SEVERITY_LABEL[issue["severity"]]]
            if ranked.get(index, {}).get("convergent"):
                tags.append("several readers")
            if issue.get("depends_on_assumptions"):
                tags.append("depends on an assumption")
            out += [f"### {n}. {issue['title']}", "",
                    f"*{' · '.join(tags)} — raised by {reader_list(issue_readers(issue), table)}*", ""]
            if issue["quote"]:
                out += [quote(issue["quote"]), ""]
            out += [issue["summary"], ""]
            if issue.get("fix_direction"):
                out += [f"**Direction:** {issue['fix_direction']}", ""]
        others = [i for i in range(len(issues)) if i not in synthesis["priority_actions"]]
        if others:
            out += ["**Other issues**", ""]
            for index in sorted(others, key=lambda i: ranked.get(i, {}).get("rank", 999)):
                issue = issues[index]
                out.append(f"- {issue['title']} ({SEVERITY_LABEL[issue['severity']].lower()}; "
                           f"{reader_list(issue_readers(issue), table)})")
            out.append("")

        # Tradeoffs
        tradeoffs = synthesis["output"].get("tradeoffs", [])
        if tradeoffs:
            out += ["## Tradeoffs", "", "Readers pull in different directions here. These are yours to decide.", ""]
            for t in tradeoffs:
                out += [quote(t["quote"]), ""]
                for side in t["sides"]:
                    out.append(f"- **{table.get(side['reader'], side['reader'])}** wants {side['wants']} — {side['why']}")
                if t.get("note"):
                    out += ["", t["note"]]
                out.append("")

    # By reader
    out += ["## By reader", ""]
    personas = {p["id"]: p for p in results["personas"]}
    for review in results["persona_reviews"]:
        p = personas.get(review["persona_id"], {"name": review["persona_id"], "role": ""})
        o = review["output"]
        out += [f"### {p['name']}" + (" (secondary reader)" if p.get("role") == "secondary" else ""), "",
                f"**What they think it says:** {o['main_point']}", "",
                f"**Gut reaction:** “{o['gut_reaction']}”", "",
                f"**Likely next step:** {o['likely_next_action']['action']} — {o['likely_next_action']['driver']}", ""]
        if o.get("look_for"):
            out += ["| They look for | Status | Note |", "| --- | --- | --- |"]
            for c in o["look_for"]:
                note = c["note"].replace("|", "/")
                out.append(f"| {c['item']} | {STATUS_LABEL[c['status']]} | {note} |")
            out.append("")
        if o.get("findings"):
            out += ["**Findings**", ""]
            for i, f in enumerate(o["findings"], start=1):
                out += [f"{i}. **{f['issue']}** ({SEVERITY_LABEL[f['severity']].lower()})  ", f"   {f['why_it_matters']}", ""]
                out += ["   " + quote(f["quote"]), ""]
        if o.get("what_works"):
            out += ["**Keep**", ""]
            for w in o["what_works"]:
                out += [quote(w["quote"]), "", w["note"], ""]
        skimmed = [e for e in o.get("attention_map", []) if e["attention"] != "read_closely" and e.get("would_miss")]
        if skimmed:
            out += ["**What they'd likely miss**", ""]
            for e in skimmed:
                out.append(f"- {e['section_id']} ({ATTENTION_LABEL[e['attention']]}): {e['would_miss']}")
            out.append("")

    # AI reader
    ai = results.get("ai_reader")
    if ai:
        ran = any(x.get("answer") for x in ai["answers"])
        out += ["## What an AI assistant tells the recipient", ""]
        if ran:
            if ai.get("method") == "same_conversation":
                out += ["**Caution:** these answers were produced in the same conversation as the review, not in a fresh "
                        "context, so they may reflect what the reviewer already knew. Treat them as rough.", ""]
            else:
                out += [f"The document was given to a fresh AI assistant with no other context, followed by questions "
                        f"{ai['recipient']} might ask.", ""]
            sc = ai.get("survival_check")
            if sc:
                out += ["| Did it come through? | Result | Note |", "| --- | --- | --- |"]
                for c in sc["checks"]:
                    out.append(f"| {SURVIVAL_LABEL[c['check']]} | {RESULT_LABEL[c['result']]} | {c['note'].replace('|', '/')} |")
                out.append("")
            for x in ai["answers"]:
                out += [f"<details><summary>“{x['prompt']}”</summary>", "", x["answer"] or "", "", "</details>", ""]
        else:
            out += [f"{ai['recipient']} may paste this document into an AI assistant. To see what it tells them, "
                    "open a **new** chat (any assistant), paste the document, and ask one of these questions. "
                    "Use a fresh chat for each question.", ""]
            for x in ai["answers"]:
                out += ["```", x["prompt"], "```"]
            out.append("")
        if synthesis and synthesis["output"].get("ai_reader_highlights"):
            for h in synthesis["output"]["ai_reader_highlights"]:
                out.append(f"- {h['note']}")
            out.append("")

    if synthesis:
        # What's working
        working = synthesis["output"].get("whats_working", [])
        if working:
            out += ["## What's working", ""]
            for w in working:
                out += [quote(w["quote"]), "", f"{w['note']} *({reader_list(w['readers'], table)})*", ""]

        # Next steps
        steps = synthesis["output"]["next_steps"]
        out += ["## Next steps", ""]
        if steps.get("revision_prompts"):
            out += ["**Revision prompts.** Paste one into an AI assistant along with your document. Each asks for "
                    "options, not a finished rewrite.", ""]
            for rp in steps["revision_prompts"]:
                title = issues[rp["issue_index"]]["title"] if 0 <= rp["issue_index"] < len(issues) else ""
                out += [f"*{title}*", "", "```", rp["prompt"], "```", ""]
        if steps.get("assumptions_to_confirm"):
            assumptions = {x["id"]: x["text"] for x in results.get("assumptions", [])}
            out += ["**Assumptions to confirm**", ""]
            for x in steps["assumptions_to_confirm"]:
                out.append(f"- {assumptions.get(x['assumption_id'], x['assumption_id'])} — {x['what_changes']}")
            out.append("")
        if steps.get("follow_up_reviews"):
            out += ["**Follow-up reviews**", ""]
            out += [f"- {x['suggestion']} — {x['reason']}" for x in steps["follow_up_reviews"]] + [""]
        if steps.get("real_review"):
            out += ["**Show it to a real person**", ""]
            out += [f"- {x['who']} — {x['why']}" for x in steps["real_review"]] + [""]

    # Run quality
    q = results["quality"]
    out += ["## About this run", ""]
    rate = q["anchoring"]["rate"]
    out.append(f"- **Quotes checked:** {q['anchoring']['verified']} of {q['anchoring']['total']} findings quote the "
               f"document verbatim" + ("." if rate in (None, 1.0) else " — the rest are paraphrases; check them."))
    for pair in q["distinctiveness"]["flagged"]:
        out.append(f"- **Overlap:** {table.get(pair['a'], pair['a'])} and {table.get(pair['b'], pair['b'])} raised "
                   "mostly the same issues; one of them may not be adding much.")
    if q["stance_spread"]["note"]:
        out.append(f"- **Stance:** {q['stance_spread']['note']}")
    cov = q["coverage"]
    if cov["attention_gaps"]:
        out.append("- **Likely to be skimmed by every reader:** " + "; ".join(g["label"] for g in cov["attention_gaps"]))
    if cov["review_gaps"]:
        out.append("- **Not closely reviewed by any reader in this run:** " + "; ".join(g["label"] for g in cov["review_gaps"]))
    if q["assumption_load"]["count"]:
        out.append("- **Unconfirmed assumptions:** " + "; ".join(q["assumption_load"]["key"]))
    out += [""] + [f"*{c}*" for c in q["caveats"]] + [""]

    # Methodology
    out += ["## Methodology", "",
            f"Run {results['run']['id']} · {results['run']['created_at']} · {results['run']['platform']} · "
            f"persona reviews in {'one conversation' if results['run']['execution'] == 'single' else 'separate conversations'}"
            f" · skill content {results['run']['content_hash']}", ""]
    if results.get("assumptions"):
        out += ["**Assumptions**", ""]
        out += [f"- {x['text']} *({'confirmed' if x['confirmed'] else 'inferred'}: {x['basis']})*"
                for x in results["assumptions"]] + [""]
    for p in results["personas"]:
        out += [f"<details><summary>{p['name']}, as adapted for this document (tier {p['tier']})</summary>", "",
                p["adapted_text"], "", "</details>", ""]
    return "\n".join(out).rstrip() + "\n"


def render_summary(results, report_path=None):
    table = names(results)
    a = results["analysis"]
    lines = [f"**Plan.** {a['plan_line']}"]
    if a["goal"]["source"] == "inferred":
        lines.append(f"**Inferred goal:** {a['goal']['text']} (tell me if that's wrong)")
    synthesis = results.get("synthesis")
    if synthesis:
        issues = synthesis["output"]["issues"]
        lines += ["", "**Top priorities**"]
        for n, index in enumerate(synthesis["priority_actions"][:3], start=1):
            issue = issues[index]
            lines.append(f"{n}. {issue['title']} ({reader_list(issue_readers(issue), table)})")
        tradeoffs = synthesis["output"].get("tradeoffs", [])
        if tradeoffs:
            t = tradeoffs[0]
            sides = " vs. ".join(table.get(s["reader"], s["reader"]) for s in t["sides"])
            lines += ["", f"**Biggest tradeoff:** {sides} — {t['note'] or t['sides'][0]['wants']}"]
    gaps = results["quality"]["coverage"]["review_gaps"]
    if gaps:
        lines += ["", "**Not closely reviewed:** " + "; ".join(g["label"] for g in gaps)]
    ai = results.get("ai_reader")
    if ai and not any(x.get("answer") for x in ai["answers"]):
        lines += ["", "**AI-reader check:** not run here; the report has the recipient's questions to try in a new chat."]
    if report_path:
        lines += ["", f"Full report: {report_path}"]
    lines += ["", "*Simulated readers: reactions are likely, not certain. Writing review only, not a check of the law or facts.*"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("results")
    parser.add_argument("--out")
    parser.add_argument("--summary", action="store_true", help="print the short chat summary instead")
    args = parser.parse_args(argv)
    results = json.loads(Path(args.results).read_text(encoding="utf-8"))
    text = render_summary(results, args.out) if args.summary else render_report(results)
    if args.out and not args.summary:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
