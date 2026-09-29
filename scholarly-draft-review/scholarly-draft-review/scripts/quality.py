"""Deterministic checks for scholarly-draft-review: sections, the key-sentence outline,
quote verification, ranking, and the limitations to disclose.

Standard library only, so it runs anywhere the skill runs.

Usage:
    python quality.py results.json document.md   # print the quality block

As a library, the other scripts call split_sections(), key_sentences(),
rank_issues(), and compute_quality().
"""

import json
import math
import re
import sys
import unicodedata

# Shown in every chat summary and report. Keep in sync with "Limitations to disclose" in synthesis-rubric.md.
STANDING_LIMITATIONS = [
    ("These are simulated readers",
     "The readers are AI simulations of typical readers, not real people. Their reactions are hypotheses, and "
     "simulated readers tend to be more agreeable and more alike than real ones."),
    ("AI can be wrong, including about sources",
     "The AI can misread your draft, misstate what it says, or invent or misdescribe sources. Quotes from your "
     "draft are checked word for word; summaries and paraphrases aren't. A named work is marked verified only if a "
     "search found it, which confirms it exists and seems to address the topic, not that it says what the reader "
     "claims."),
    ("Novelty views are leads",
     "What the AI knows about legal scholarship is incomplete and out of date, especially recent work. Treat its "
     "views on whether your claim is new, and its reading suggestions, as leads, and do your own search before "
     "relying on them."),
    ("Not a cite-check",
     "This review doesn't verify the law, cases, facts, or citations in your draft. A reader may flag something to "
     "check; nothing here confirms that anything is correct."),
    ("Verify before you act",
     "Check anything you plan to act on against your draft and the sources, and get real readers' reactions before "
     "you submit. The feedback plan suggests who to ask."),
    ("Your draft went to an AI service",
     "Follow any rules that apply to your use of AI tools, such as a journal's or publisher's policy."),
]
STAGE_NAMES = {"idea": "an idea-stage", "early": "an early", "full": "a full", "workshop": "a workshop",
               "submission": "a submission"}
WORK_STATUSES = ("verified", "cited_in_draft", "not_found", "not_checked")

STAGES = ["idea", "early", "full", "workshop", "submission"]
PSEUDO_READERS = {"key-sentences": "Key-sentence outline"}
MAX_PARAGRAPH_SECTIONS = 25  # drafts without headings are grouped into at most this many sections
MIN_KEY_SENTENCE_WORDS = 12  # shorter paragraphs are skipped in the key-sentence outline
PRIORITY_LIMIT = 7
SEVERITY_POINTS = {"high": 3, "medium": 2, "low": 1}

FOOTNOTE_MARK = re.compile(r"\[\^\d+\]")
HEADING_PATTERNS = [
    re.compile(r"^#{1,6} \S.*$"),                                    # markdown
    re.compile(r"^[A-Z][A-Z0-9 .,:;&'’()\-–—]{3,90}$"),              # ALL CAPS
    re.compile(r"^Part [IVXLC0-9]+\b.{0,90}$", re.I),                # Part I: ...
    re.compile(r"^[IVXLC]{1,6}\.\s+\S.{0,90}$"),                     # I. Introduction
    re.compile(r"^[A-H]\.\s+[A-Z]\S*(?:\s+\S+){0,11}$"),            # A. The Rise of X
    re.compile(r"^(Introduction|Conclusion|Abstract|Background|Acknowledgm?ents|Footnotes|Notes)$", re.I),
]
INTRO_HEADING = re.compile(r"^(?:[IVX0-9]+\.\s+)?introduction\b", re.I)
ABBREVIATIONS = {
    "v", "vs", "id", "e.g", "i.e", "cf", "see", "no", "nos", "inc", "co", "corp", "ltd", "mr", "ms", "mrs", "dr",
    "prof", "stat", "cir", "ct", "app", "supp", "rev", "u.s", "u.s.c", "c.f.r", "fed", "reg", "art", "cl", "sec",
    "ch", "pt", "para", "al", "st", "ass'n", "dep't", "gov't", "univ", "jr", "sr", "ed", "eds", "cong", "sess",
    "amend", "const", "etc", "approx", "fig", "vol", "pp", "p", "n", "nn", "l", "j", "l.j", "l.q", "ann", "misc",
    # Common case-name and reporter abbreviations (Bluebook T6 style)
    "mfg", "bros", "assn", "dept", "govt", "int'l", "nat'l", "sys", "hosp", "indus", "ins", "mut", "prods", "servs",
    "tech", "elec", "envtl", "comm'n", "auth", "dist", "twp", "cnty", "bd", "admin", "ctr", "grp", "mgmt", "org",
    "pharm", "transp", "sch", "educ", "fin", "invs", "cmty", "sav", "fed'n", "e.d", "s.d", "n.d", "w.d", "d.c",
}
SENTENCE_END = re.compile(r"[.?!][\"”’')\]]*(?:\[\^\d+\])?\d{0,3}(?=\s+[\"“‘'(\[]?[A-Z0-9])")


# ---------- text helpers ----------

def normalize(text):
    """Lowercase and fold quotes, dashes, footnote marks, and whitespace so quote matching tolerates typography."""
    text = unicodedata.normalize("NFKC", text or "")
    text = FOOTNOTE_MARK.sub("", text)
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
    """Approximate character offset of the quote's first segment in the document, or None."""
    segments = quote_segments(quote)
    if not segments:
        return None
    doc = normalize(document_text)
    pos = doc.find(normalize(segments[0]))
    if pos == -1:
        return None
    return int(pos * len(document_text) / max(len(doc), 1))


# ---------- document structure ----------

def paragraphs(text):
    """Blank-line-separated paragraphs with their character spans."""
    return [{"text": m.group(0).strip(), "start": m.start(), "end": m.end()}
            for m in re.finditer(r"\S(?:.*?)(?=\n\s*\n|\Z)", text, re.S)]


def is_heading(paragraph_text):
    if "\n" in paragraph_text.strip():
        return False
    line = paragraph_text.strip()
    if line.startswith("#"):
        return bool(HEADING_PATTERNS[0].match(line))
    if line.endswith(".") or len(line.split()) > 16:
        return False
    return any(p.match(line) for p in HEADING_PATTERNS[1:])


def heading_label(paragraph_text):
    return paragraph_text.strip().lstrip("#").strip()[:70]


def split_sections(text):
    """Split a draft into sections at its headings; drafts without headings are split into paragraph groups."""
    paras = paragraphs(text)
    heads = [p for p in paras if is_heading(p["text"])]
    sections = []
    if len(heads) >= 2:
        starts = []
        if heads[0]["start"] > 0 and text[:heads[0]["start"]].strip():
            starts.append((0, "Opening"))
        starts += [(h["start"], heading_label(h["text"])) for h in heads]
        for i, (start, label) in enumerate(starts):
            end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
            sections.append({"id": f"s{i + 1}", "label": label, "start": start, "end": end})
        return sections
    size = max(1, math.ceil(len(paras) / MAX_PARAGRAPH_SECTIONS))
    for i in range(0, len(paras), size):
        group = paras[i:i + size]
        first = " ".join(group[0]["text"].split()[:8])
        span = f"¶{i + 1}" if len(group) == 1 else f"¶{i + 1}–{i + len(group)}"
        sections.append({"id": f"p{i // size + 1}", "label": f"{span}: {first}…",
                         "start": group[0]["start"], "end": group[-1]["end"]})
    return sections


def section_for_position(sections, pos):
    if pos is None:
        return None
    for section in sections:
        if section["start"] <= pos < section["end"]:
            return section["id"]
    return sections[-1]["id"] if sections else None


def is_footnotes(section):
    return section["label"].strip().lower() in ("footnotes", "notes", "endnotes")


def first_sentence(paragraph_text):
    text = " ".join(paragraph_text.split())
    for match in SENTENCE_END.finditer(text):
        end = match.end()
        if text[match.start()] == ".":
            token = re.search(r"([A-Za-z][A-Za-z.'’]*)\.$", text[:match.start() + 1])
            if token:
                word = token.group(1).lower().replace("’", "'")
                if word in ABBREVIATIONS or len(word) == 1 or re.fullmatch(r"(?:[a-z]\.)+[a-z]", word):
                    continue
        return text[:end].strip()
    return text if len(text) <= 400 else text[:400].rsplit(" ", 1)[0] + "…"


def intro_start(text):
    """Offset of an 'Introduction' heading, or 0. Title, author note, abstract, and epigraph come before it."""
    return next((p["start"] for p in paragraphs(text)
                 if is_heading(p["text"]) and INTRO_HEADING.match(heading_label(p["text"]))), 0)


def key_sentences(text, sections=None):
    """The first sentence of each body paragraph, in order: a key-sentence (after-the-fact) outline."""
    sections = sections if sections is not None else split_sections(text)
    footnote_ids = {s["id"] for s in sections if is_footnotes(s)}
    paras = paragraphs(text)
    intro = intro_start(text)
    out = []
    for para in paras:
        body = para["text"]
        section_id = section_for_position(sections, para["start"])
        if para["start"] < intro or section_id in footnote_ids or is_heading(body):
            continue
        if re.match(r"^(>|[-*•]\s|\d+[.)]\s|\[\^\d+\]:|\|)", body) or len(body.split()) < MIN_KEY_SENTENCE_WORDS:
            continue
        out.append({"id": f"k{len(out) + 1}", "section_id": section_id, "text": first_sentence(body)})
    return out


def key_sentence_outline(text):
    """Markdown listing of the key-sentence outline, grouped by section."""
    sections = split_sections(text)
    labels = {s["id"]: s["label"] for s in sections}
    lines = ["# Key-sentence outline", "",
             "The first sentence of each body paragraph, in order. Read alone, it should tell the argument.", ""]
    current = None
    for k in key_sentences(text, sections):
        if k["section_id"] != current:
            current = k["section_id"]
            lines += ["", f"## {labels.get(current, current)} ({current})", ""]
        lines.append(f"- **{k['id']}** {k['text']}")
    return "\n".join(lines).strip() + "\n"


# ---------- findings ----------

def iter_findings(results, include_key_sentences=False):
    """Yield (finding_ref, reader_id, finding) for every reader finding (and key-sentence flag if asked)."""
    for review in results.get("persona_reviews", []):
        pid = review["persona_id"]
        for i, finding in enumerate(review["output"].get("findings", []), start=1):
            yield f"{pid}/{i}", pid, finding
    check = results.get("key_sentence_check")
    if include_key_sentences and check:
        for i, flag in enumerate(check.get("flags", []), start=1):
            yield f"key-sentences/{i}", "key-sentences", flag


# ---------- ranking ----------

def issue_readers(issue, readers_run):
    readers = {ref.split("/")[0] for ref in issue["finding_refs"]}
    readers |= {r["reader"] for r in issue.get("reasons", []) if r["reader"] in readers_run or r["reader"] in PSEUDO_READERS}
    if issue["category"] == "key_sentence":
        readers.add("key-sentences")
    return readers


def rank_issues(results, document_text):
    """Score issues with the weights in synthesis-rubric.md. Returns (ranked, priority, parked)."""
    synthesis = results.get("synthesis")
    if not synthesis:
        return [], [], []
    readers_run = {p["id"] for p in results.get("personas", [])}
    ranked = []
    for index, issue in enumerate(synthesis["output"]["issues"]):
        count = max(len(issue_readers(issue, readers_run)), 1)
        score = SEVERITY_POINTS[issue["severity"]] * 3 + min(count, 3) * 2
        score += 3 if issue["category"] == "claim_mismatch" else 0
        pos = quote_position(issue["quote"], document_text)
        ranked.append({"issue_index": index, "score": float(score), "readers": count, "convergent": count >= 2, "timing": issue["timing"],
                       "_pos": pos if pos is not None else len(document_text)})
    ranked.sort(key=lambda r: (r["timing"] != "now", -r["score"], r["_pos"]))
    for rank, item in enumerate(ranked, start=1):
        item["rank"] = rank
        del item["_pos"]
    priority = [r["issue_index"] for r in ranked if r["timing"] == "now"][:PRIORITY_LIMIT]
    parked = [r["issue_index"] for r in ranked if r["timing"] == "later"]
    return ranked, priority, parked


# ---------- quality ----------

def limitations(results, unverified_quotes):
    """The standing limitations, then the ones that apply to this run."""
    out = [{"title": t, "text": x, "scope": "standing"} for t, x in STANDING_LIMITATIONS]

    def add(title, text):
        out.append({"title": title, "text": text, "scope": "run"})
    analysis = results.get("analysis", {})
    if analysis.get("claim", {}).get("source") == "inferred":
        add("Your claim was inferred", "You didn't state your claim, so the review used the one shown at the top. "
            "If that's wrong, much of the feedback shifts.")
    stage = analysis.get("stage", {})
    if stage.get("source") == "inferred":
        add("The stage was inferred", f"The review treated this as {STAGE_NAMES.get(stage.get('id'), 'a')} draft "
            f"({stage.get('basis', '').rstrip('.')}). If that's wrong, the readers and priorities change.")
    unchecked = [i["work"] for i in (results.get("related_work_check") or {}).get("items", [])
                 if i["status"] == "not_checked"]
    if len(unchecked) == 1:
        add("1 named work not checked", f"No search was run for {unchecked[0]}. It may not exist or may not say "
            "what the reader claims. Confirm it before relying on it.")
    elif unchecked:
        add(f"{len(unchecked)} named works not checked", "No search was run for these, so they may not exist or may "
            "not say what the readers claim: " + "; ".join(unchecked) + ". Confirm each before relying on it.")
    if unverified_quotes:
        refs = ", ".join(u["finding_ref"] for u in unverified_quotes)
        add("Some quotes weren't found in your draft", f"Findings {refs} quote text that isn't word for word in your "
            "draft. Check them against the draft before acting on them.")
    return out


def related_work_counts(results):
    items = (results.get("related_work_check") or {}).get("items", [])
    counts = {status: sum(1 for i in items if i["status"] == status) for status in WORK_STATUSES}
    return {"specific": len(items), **counts}


def compute_quality(results, document_text):
    total = verified = 0
    unverified = []
    for ref, _, finding in iter_findings(results, include_key_sentences=True):
        total += 1
        if quote_in_document(finding["quote"], document_text):
            verified += 1
        else:
            unverified.append({"finding_ref": ref, "quote": finding["quote"]})
    return {
        "anchoring": {"total": total, "verified": verified, "unverified": unverified},
        "related_work": related_work_counts(results),
        "limitations": limitations(results, unverified),
    }


def main(argv):
    if len(argv) < 2 or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    with open(argv[0], encoding="utf-8") as f:
        results = json.load(f)
    with open(argv[1], encoding="utf-8") as f:
        document_text = f.read()
    print(json.dumps(compute_quality(results, document_text), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
