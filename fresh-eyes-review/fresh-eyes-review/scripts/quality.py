"""Deterministic checks on a fresh-eyes-review results.json.

Standard library only, so it runs anywhere the skill runs.

Usage:
    python quality.py results.json            # print the quality block
    python quality.py results.json --write    # also write it back into the file

As a library, the pipeline calls split_sections(), attention_gaps(),
rank_issues(), and compute_quality().
"""

import json
import re
import sys
import unicodedata
from itertools import combinations

STANDING_CAVEATS = [
    "These are simulated readers. Treat their reactions as hypotheses. Simulated readers tend to be "
    "more agreeable and more uniform than real people, and they don't replace review by a real person.",
    "This review looks at how the writing is likely to land. It doesn't check whether the law, facts, "
    "or citations are correct, or whether the document is legally sufficient.",
]

DISTINCTIVENESS_FLAG = 0.5  # overlap at or above this between two personas is flagged
MIN_GAP_WORDS = 25  # shorter sections (salutations, signatures, captions, jury demands) aren't reported as gaps
SEVERITY_POINTS = {"high": 3, "medium": 2, "low": 1}


# ---------- text helpers ----------

def normalize(text):
    """Lowercase and fold quotes, dashes, and whitespace so quote matching tolerates typography."""
    text = unicodedata.normalize("NFKC", text or "")
    text = text.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                                         "–": "-", "—": "-", " ": " "}))
    text = re.sub(r"[\"'`*_]", "", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def quote_segments(quote):
    """Split a quote on ellipses; each segment must appear in the document."""
    parts = re.split(r"\.\.\.|…|\[\.\.\.\]", quote or "")
    return [p.strip() for p in parts if len(normalize(p)) >= 3]


def quote_in_document(quote, document_text):
    segments = quote_segments(quote)
    if not segments:
        return False
    doc = normalize(document_text)
    return all(normalize(seg) in doc for seg in segments)


def quote_position(quote, document_text):
    """Character offset of the quote's first segment in the document, or None."""
    segments = quote_segments(quote)
    if not segments:
        return None
    doc = normalize(document_text)
    pos = doc.find(normalize(segments[0]))
    if pos == -1:
        return None
    # Map the normalized offset back approximately by ratio; good enough for ordering and sections.
    return int(pos * len(document_text) / max(len(doc), 1))


def words(text):
    return set(re.findall(r"[a-z0-9']+", normalize(text)))


# ---------- document sections ----------

def split_sections(text):
    """Split a document into sections: markdown headings if present, otherwise paragraphs."""
    headings = list(re.finditer(r"^(#{1,6} .+|[A-Z][A-Z0-9 .,&'-]{3,60})$", text, re.M))
    sections = []
    if len(headings) >= 2:
        starts = [0] if headings[0].start() > 0 and text[:headings[0].start()].strip() else []
        starts += [h.start() for h in headings]
        for i, start in enumerate(starts):
            end = starts[i + 1] if i + 1 < len(starts) else len(text)
            chunk = text[start:end].strip()
            label = chunk.splitlines()[0].lstrip("# ").strip()[:60] if chunk else f"Section {i + 1}"
            sections.append({"id": f"s{i + 1}", "label": label, "start": start, "end": end})
        return sections
    for i, match in enumerate(re.finditer(r"\S(?:.*?)(?=\n\s*\n|\Z)", text, re.S)):
        first = " ".join(match.group(0).split()[:8])
        sections.append({"id": f"p{i + 1}", "label": f"¶{i + 1}: {first}…", "start": match.start(), "end": match.end()})
    return sections


def section_for_position(sections, pos):
    if pos is None:
        return None
    for section in sections:
        if section["start"] <= pos < section["end"]:
            return section["id"]
    return sections[-1]["id"] if sections else None


# ---------- findings ----------

def iter_findings(results):
    """Yield (finding_ref, persona_id, finding) for every persona finding."""
    for review in results.get("persona_reviews", []):
        pid = review["persona_id"]
        for i, finding in enumerate(review["output"].get("findings", []), start=1):
            yield f"{pid}/{i}", pid, finding


def finding_lookup(results):
    return {ref: (pid, f) for ref, pid, f in iter_findings(results)}


# ---------- coverage ----------

def attention_gaps(results):
    """Sections every persona that ran would skim or skip."""
    sections = results["document"]["sections"]
    maps = {r["persona_id"]: {e["section_id"]: e["attention"] for e in r["output"].get("attention_map", [])}
            for r in results.get("persona_reviews", []) if r["output"].get("attention_map")}
    if not maps:
        return []
    gaps = []
    for section in substantive(results):
        marks = [m.get(section["id"]) for m in maps.values()]
        if all(mark in ("skimmed", "skipped") for mark in marks):
            gaps.append({"section_id": section["id"], "label": section["label"], "readers": sorted(maps)})
    return gaps


def review_gaps(results):
    """Sections no persona read closely and no finding or 'what works' passage touches."""
    doc = results["document"]["text"]
    sections = results["document"]["sections"]
    touched = set()
    close = set()
    for review in results.get("persona_reviews", []):
        out = review["output"]
        for entry in out.get("attention_map", []):
            if entry["attention"] == "read_closely":
                close.add(entry["section_id"])
        quotes = [f["quote"] for f in out.get("findings", [])]
        quotes += [w["quote"] for w in out.get("what_works", [])]
        quotes += [c["quote"] for c in out.get("look_for", []) if c.get("quote")]
        for q in quotes:
            sid = section_for_position(sections, quote_position(q, doc))
            if sid:
                touched.add(sid)
    return [{"section_id": s["id"], "label": s["label"]} for s in substantive(results)
            if s["id"] not in close and s["id"] not in touched]


def substantive(results):
    """Sections long enough that missing them could matter."""
    doc = results["document"]["text"]
    return [s for s in results["document"]["sections"]
            if len(doc[s["start"]:s["end"]].split()) >= MIN_GAP_WORDS]


# ---------- ranking ----------

def rank_issues(results):
    """Score and rank synthesis issues using the weights in synthesis-rubric.md."""
    synthesis = results.get("synthesis")
    if not synthesis:
        return [], [], []
    issues = synthesis["output"]["issues"]
    roles = {p["id"]: p["role"] for p in results.get("personas", [])}
    lookup = finding_lookup(results)
    doc = results["document"]["text"]
    ranked = []
    for index, issue in enumerate(issues):
        readers = {lookup[r][0] for r in issue["finding_refs"] if r in lookup}
        readers |= {r["reader"] for r in issue.get("reasons", []) if r["reader"] in roles}
        if issue["category"] == "survival_failure":
            readers.add("ai-reader")
        count = max(len(readers), 1)
        primary = any(roles.get(r) == "primary" for r in readers) or issue["category"] == "survival_failure"
        score = SEVERITY_POINTS[issue["severity"]] * 3 + min(count, 3) * 2
        score += 2 if primary else 0
        score += 3 if issue["category"] in ("main_point_mismatch", "survival_failure") else 0
        score -= 1 if issue.get("depends_on_assumptions") else 0
        pos = quote_position(issue["quote"], doc)
        ranked.append({"issue_index": index, "score": float(score), "readers": count,
                       "primary": primary, "convergent": count >= 2, "_pos": pos if pos is not None else len(doc)})
    ranked.sort(key=lambda r: (-r["score"], r["_pos"]))
    for rank, item in enumerate(ranked, start=1):
        item["rank"] = rank
        del item["_pos"]
    priority = [r["issue_index"] for r in ranked[:7]]
    dropped = {d["finding_ref"] for d in synthesis["output"].get("dropped_findings", [])}
    convergent_refs = {ref for r in ranked if r["convergent"] for ref in issues[r["issue_index"]]["finding_refs"]}
    by_persona = {}
    for ref, pid, _ in iter_findings(results):
        if ref not in dropped and ref not in convergent_refs:
            by_persona.setdefault(pid, []).append(ref)
    reader_specific = [{"persona_id": pid, "finding_refs": refs} for pid, refs in by_persona.items()]
    return ranked, priority, reader_specific


# ---------- quality ----------

def distinctiveness(results):
    """Pairwise overlap between personas' findings (share of findings with a matching counterpart)."""
    per_persona = {}
    for _, pid, finding in iter_findings(results):
        per_persona.setdefault(pid, []).append(words(finding["quote"]) | words(finding["issue"]))
    pairs = []
    for a, b in combinations(sorted(per_persona), 2):
        fa, fb = per_persona[a], per_persona[b]
        if not fa or not fb:
            continue
        def matched(xs, ys):
            return sum(1 for x in xs if any(len(x & y) / max(len(x | y), 1) >= 0.35 for y in ys))
        overlap = (matched(fa, fb) + matched(fb, fa)) / (len(fa) + len(fb))
        pairs.append({"a": a, "b": b, "overlap": round(overlap, 3)})
    flagged = [p for p in pairs if p["overlap"] >= DISTINCTIVENESS_FLAG]
    return {"pairs": pairs, "flagged": flagged}


def compute_quality(results):
    doc = results["document"]["text"]
    total = verified = 0
    unverified = []
    for ref, _, finding in iter_findings(results):
        total += 1
        if quote_in_document(finding["quote"], doc):
            verified += 1
        else:
            unverified.append({"finding_ref": ref, "quote": finding["quote"]})

    reviews = [r for r in results.get("persona_reviews", []) if r["persona_id"] != "baseline"]
    actions = {normalize(r["output"]["likely_next_action"]["action"])[:60] for r in reviews}
    spread_note = ("All personas predict the same next action; check whether they are doing distinct work."
                   if len(reviews) > 1 and len(actions) == 1 else "")

    unassessed = []
    persona_files = {p["id"]: p for p in results.get("personas", [])}
    for review in reviews:
        expected = look_for_items(persona_files.get(review["persona_id"], {}).get("adapted_text", ""))
        got = {normalize(c["item"]) for c in review["output"].get("look_for", [])}
        for item in expected:
            if not any(normalize(item)[:40] in g or g[:40] in normalize(item) for g in got):
                unassessed.append({"persona_id": review["persona_id"], "item": item})

    key_assumptions = [a["text"] for a in results.get("assumptions", []) if not a.get("confirmed")]
    leaks = []
    if results.get("synthesis"):
        leaks = [{"finding_ref": d["finding_ref"], "note": d["note"]}
                 for d in results["synthesis"]["output"].get("dropped_findings", [])
                 if d["rule"] == "leaked_knowledge"]

    return {
        "anchoring": {"total": total, "verified": verified,
                      "rate": round(verified / total, 3) if total else None, "unverified": unverified},
        "distinctiveness": distinctiveness(results),
        "stance_spread": {"personas": len(reviews), "distinct_actions": len(actions), "note": spread_note},
        "assumption_load": {"count": len(key_assumptions), "key": key_assumptions[:5]},
        "coverage": {"unassessed_look_for": unassessed,
                     "attention_gaps": attention_gaps(results),
                     "review_gaps": review_gaps(results)},
        "leaks": leaks,
        "caveats": list(STANDING_CAVEATS),
    }


def look_for_items(persona_text):
    match = re.search(r"## 5\. What they look for\n(.*?)\n## ", persona_text or "", re.S)
    if not match:
        return []
    return [line[2:].strip() for line in match.group(1).splitlines() if line.startswith("- ")]


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    path = argv[0]
    with open(path, encoding="utf-8") as f:
        results = json.load(f)
    quality = compute_quality(results)
    print(json.dumps(quality, indent=2, ensure_ascii=False))
    if "--write" in argv:
        results["quality"] = quality
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
