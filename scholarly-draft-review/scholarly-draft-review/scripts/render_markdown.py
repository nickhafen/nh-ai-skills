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
STAGE_LABEL = {"idea": "Idea", "early": "Early draft", "full": "Full draft", "workshop": "Workshop draft",
               "submission": "Submission draft"}
READER_TYPE_LABEL = {"nonexpert": "Nonexpert", "expert": "Law-trained, outside the specialty", "Expert": "Specialist",
                     "gatekeeper": "Gatekeeper", "custom": "Custom reader"}
WHEN_LABEL = {"now": "Now", "next_draft": "After the next draft", "before_submission": "Before you submit"}
PSEUDO = {"key-sentences": "Key-sentence outline"}
WORK_LABEL = {"verified": "Verified", "cited_in_draft": "Already cited in the draft",
              "not_checked": "Not checked: confirm it exists before relying on it",
              "kind": "Kind of work to search for"}
LISTENING_NOTE = ("When they respond, listen without defending. Ask \"Can you say more about that?\" rather than "
                  "explaining what you meant. If a reader found a passage unclear, it was unclear to that reader, "
                  "whatever you intended. Then respond to each comment, even if the response is to decide against it.")


def quote(text):
    text = " ".join((text or "").split())
    return f"> “{text}”" if text else ""


def names(results):
    table = {p["id"]: p["name"] for p in results["personas"]}
    table.update(PSEUDO)
    return table


def reader_list(ids, table):
    return ", ".join(table.get(i, i) for i in ids)


def issue_readers(issue):
    readers = {r["reader"] for r in issue.get("reasons", [])} | {ref.split("/")[0] for ref in issue["finding_refs"]}
    if issue["category"] == "key_sentence":
        readers.add("key-sentences")
    return sorted(readers)


def related_work(results):
    """Every related-work pointer with its check status. Works searched for and not found are marked not_found."""
    checks = {i["ref"]: i for i in (results.get("related_work_check") or {}).get("items", [])}
    out = []
    for review in results["persona_reviews"]:
        for n, item in enumerate(review["output"].get("related_work", []), start=1):
            ref = f"{review['persona_id']}/rw{n}"
            check = checks.get(ref, {}) if item["specific"] else {}
            status = check.get("status", "not_checked") if item["specific"] else "kind"
            out.append({"ref": ref, "reader": review["persona_id"], "work": item["work"], "why": item["why"],
                        "confidence": item["confidence"], "status": status, "url": check.get("url"),
                        "note": check.get("note", "")})
    return out


def work_line(w, table=None):
    work = f"[{w['work']}]({w['url']})" if w.get("url") else w["work"]
    who = f"; {table.get(w['reader'], w['reader'])}" if table else ""
    return f"- {work} — {w['why']} *({WORK_LABEL[w['status']]}; {w['confidence']} confidence{who})*"


def limitation_lines(results):
    return [f"- **{x['title']}.** {x['text']}" for x in results["quality"]["limitations"]]


def stage_line(a):
    s = a["stage"]
    text = f"**Stage:** {STAGE_LABEL[s['id']]}"
    if s["source"] == "inferred":
        text += f" (inferred: {s['basis']}; tell me if that's wrong)"
    return text


def claim_line(a):
    c = a["claim"]
    if c["source"] == "inferred":
        return f"**Claim (inferred):** {c['text']} — confirm it; much of the feedback shifts if it is wrong."
    return f"**Claim:** {c['text']}"


def front_matter(results):
    """The compact setup and reliance note shown first in each rendered report."""
    return ["<details open><summary><strong>Before you rely on this</strong></summary>", ""] + limitation_lines(results) + ["", "</details>", ""]


def issue_block(issue, n, ranked, table):
    tags = [SEVERITY_LABEL[issue["severity"]]]
    out = [f"### {n}. {issue['title']}", "",
           f"*{' · '.join(tags)} — raised by {reader_list(issue_readers(issue), table)}*", ""]
    if issue["quote"]:
        out += [quote(issue["quote"]), ""]
    out += [issue["summary"], ""]
    if issue.get("direction"):
        out += [f"**Direction:** {issue['direction']}", ""]
    return out


def render_report(results):
    table = names(results)
    a = results["analysis"]
    doc = results["document"]
    out = [f"# Scholarly draft review: {doc.get('title') or a['piece_type']}", ""]
    out += front_matter(results)

    synthesis = results.get("synthesis")
    if synthesis:
        issues = synthesis["output"]["issues"]
        ranked = {r["issue_index"]: r for r in synthesis["ranked_issues"]}
        out += ["## Priority actions", "", f"What matters at this stage: {a['stage_focus']}", ""]
        for n, index in enumerate(synthesis["priority_actions"], start=1):
            out += issue_block(issues[index], n, ranked.get(index, {}), table)
        shown = set(synthesis["priority_actions"]) | set(synthesis["parked"])
        others = sorted((i for i in range(len(issues)) if i not in shown), key=lambda i: ranked.get(i, {}).get("rank", 999))
        if others:
            out += ["**Other issues to look at now**", ""]
            out += [f"- {issues[i]['title']} ({SEVERITY_LABEL[issues[i]['severity']].lower()}; "
                    f"{reader_list(issue_readers(issues[i]), table)})" for i in others] + [""]
        if synthesis["parked"]:
            out += ["## For a later draft", "", "Real issues, but not priorities at this stage.", ""]
            for i in synthesis["parked"]:
                issue = issues[i]
                out.append(f"- **{issue['title']}** — {issue['summary']} *({reader_list(issue_readers(issue), table)})*")
            out.append("")

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

        working = synthesis["output"].get("whats_working", [])
        if working:
            out += ["## What's working", ""]
            for w in working:
                out += [quote(w["quote"]), "", f"{w['note']} *({reader_list(w['readers'], table)})*", ""]

        plan = synthesis["output"].get("feedback_plan", [])
        if plan:
            out += ["## Who to ask next", "", "| When | Who | What to ask | Why |", "| --- | --- | --- | --- |"]
            for x in plan:
                out.append(f"| {WHEN_LABEL[x['when']]} | {x['who']} | {x['ask']} | {x['why']} |".replace("\n", " "))
            out += ["", LISTENING_NOTE, ""]

    # By reader
    out += ["## By reader", ""]
    personas = {p["id"]: p for p in results["personas"]}
    for review in results["persona_reviews"]:
        p = personas.get(review["persona_id"], {"name": review["persona_id"], "reader_type": "custom"})
        o = review["output"]
        out += [f"### {p['name']}", "", f"*{READER_TYPE_LABEL.get(p.get('reader_type'), '')}*", "",
                f"**What they think it argues:** {o['main_point']}", ""]
        if o.get("look_for"):
            out += ["| They look for | Status | Note |", "| --- | --- | --- |"]
            for c in o["look_for"]:
                out.append(f"| {c['item']} | {STATUS_LABEL[c['status']]} | {c['note'].replace('|', '/')} |")
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
        pointers = [w for w in related_work(results) if w["reader"] == review["persona_id"] and w["status"] != "not_found"]
        if pointers:
            out += ["**Would point you to**", ""] + [work_line(w) for w in pointers] + [""]

    # Key sentences
    ks = results.get("key_sentence_check")
    outline = doc.get("key_sentences", [])
    if ks or outline:
        out += ["## Key-sentence outline", ""]
        if ks:
            out += [ks["verdict"], ""]
            for i, f in enumerate(ks["flags"], start=1):
                out += [f"{i}. **{f['paragraph_id']}** — {f['issue']}", "", "   " + quote(f["quote"]), ""]
        if outline:
            labels = {s["id"]: s["label"] for s in doc["sections"]}
            out += ["<details><summary>The first sentence of every body paragraph</summary>", ""]
            current = None
            for k in outline:
                if k["section_id"] != current:
                    current = k["section_id"]
                    out += ["", f"**{labels.get(current, current)}**", ""]
                out.append(f"- *{k['id']}* {k['text']}")
            out += ["", "</details>", ""]

    # Method
    run, q = results["run"], results["quality"]
    source = doc.get("source_file") or "your draft"
    out += ["## Method", "",
            f"- **Draft:** {source} ({doc['word_count']} words; working copy `{doc['working_copy']}`). "
            "This report refers to the draft by filename and doesn't include its text.",
            f"- **Run:** {run['id']} · {run['created_at']} · {run['platform']} · model {run['model']} · skill content "
            f"{run['content_hash']}. Each reader reviewed the draft in turn, in one conversation.",
            f"- **Quotes checked:** {q['anchoring']['verified']} of {q['anchoring']['total']} quote the draft word for word."]
    rw = q["related_work"]
    if rw["specific"]:
        out.append(f"- **Named works:** {rw['specific']} named; {rw['verified']} verified, {rw['cited_in_draft']} "
                   f"already cited, {rw['not_checked']} not checked, {rw['not_found']} not found and left out.")
    out.append("")
    if results.get("assumptions"):
        out += ["**Assumptions**", ""]
        out += [f"- {x['text']} *({'confirmed' if x['confirmed'] else 'inferred'}: {x['basis']})*"
                for x in results["assumptions"]] + [""]
    if synthesis and synthesis["output"].get("dropped_findings"):
        out += ["**Findings set aside**", ""]
        out += [f"- `{d['finding_ref']}` ({d['rule'].replace('_', ' ')}): {d['note']}"
                for d in synthesis["output"]["dropped_findings"]] + [""]
    lost = [w for w in related_work(results) if w["status"] == "not_found"]
    if lost:
        out += ["**Named works that couldn't be found**", ""]
        out += [f"- `{w['ref']}` {w['work']}" + (f" — {w['note']}" if w["note"] else "") for w in lost] + [""]
    for p in results["personas"]:
        out += [f"<details><summary>{p['name']}, as adapted for this draft ({p['briefing']})</summary>", "",
                p["adapted_text"], "", "</details>", ""]
    return "\n".join(out).rstrip() + "\n"


def render_summary(results, report_path=None):
    table = names(results)
    a = results["analysis"]
    lines = [f"**Plan.** {a['plan_line']}", stage_line(a), claim_line(a)]
    synthesis = results.get("synthesis")
    if synthesis:
        issues = synthesis["output"]["issues"]
        lines += ["", "**Top priorities now**"]
        for n, index in enumerate(synthesis["priority_actions"][:3], start=1):
            issue = issues[index]
            lines.append(f"{n}. {issue['title']} ({reader_list(issue_readers(issue), table)})")
        if synthesis["parked"]:
            lines.append(f"For a later draft: {len(synthesis['parked'])} issue(s), listed in the report.")
        tradeoffs = synthesis["output"].get("tradeoffs", [])
        if tradeoffs:
            t = tradeoffs[0]
            sides = " vs. ".join(table.get(s["reader"], s["reader"]) for s in t["sides"])
            lines += ["", f"**Biggest tradeoff:** {sides} — {t['note'] or t['sides'][0]['wants']}"]
        plan = synthesis["output"].get("feedback_plan", [])
        if plan:
            lines += ["", f"**Who to ask next:** {plan[0]['who']} — “{plan[0]['ask']}”"]
    rw = results["quality"]["related_work"]
    if rw["verified"]:
        lines += ["", f"**Related work:** {rw['verified']} named work{'s' if rw['verified'] > 1 else ''} found by "
                      "search and linked in the report"]
    lines += ["", "**Before you rely on this**"] + limitation_lines(results)
    if report_path:
        lines += ["", f"Full report: {report_path}"]
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
