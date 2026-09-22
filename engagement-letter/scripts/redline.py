#!/usr/bin/env python3
"""Redline a tailored engagement letter against the firm's standard form.

Usage:
    python redline.py --intake intake.json --letter "Engagement Letter.docx" --out "Redline.docx"

The output uses REAL Word tracked changes (<w:ins> and <w:del> revisions by
"Engagement Letter Skill"), so Review > Accept / Reject works in Word. It does
not just color text or format it as strikethrough.

  * Paragraphs that match: copied as-is.
  * Paragraphs that are similar: word-level insertions and deletions.
  * Paragraphs added or removed: the whole paragraph is inserted or deleted,
    including its paragraph mark.

Rejecting all changes gives the standard form. Accepting all gives the tailored letter.
Requires python-docx.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fill_template import (BODY_STYLE, HEADING_STYLE, build_fields,  # noqa: E402
                           open_letterhead, set_text, standard_paragraphs)

AUTHOR = "Engagement Letter Skill"
SIMILARITY = 0.5  # word-overlap ratio above which two paragraphs are diffed word by word
MIN_KEEP = 3      # unchanged runs shorter than this many words, between edits, are folded into the edit


class Revisions:
    """Creates <w:ins>/<w:del> elements with unique ids and one timestamp."""

    def __init__(self):
        self.next_id = 1
        self.date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def mark(self, tag):
        el = OxmlElement(tag)
        el.set(qn("w:id"), str(self.next_id))
        el.set(qn("w:author"), AUTHOR)
        el.set(qn("w:date"), self.date)
        self.next_id += 1
        return el


def make_run(text, deleted=False):
    """A <w:r> for text; deleted text must use <w:delText>. '\\n' becomes <w:br/>."""
    r = OxmlElement("w:r")
    for i, line in enumerate(text.split("\n")):
        if i:
            r.append(OxmlElement("w:br"))
        if line:
            t = OxmlElement("w:delText" if deleted else "w:t")
            t.set(qn("xml:space"), "preserve")
            t.text = line
            r.append(t)
    return r


def add_segment(p, kind, text, revs):
    """Append text to paragraph p as plain ('equal'), inserted ('ins') or deleted ('del')."""
    if not text:
        return
    if kind == "equal":
        p._p.append(make_run(text))
    else:
        wrapper = revs.mark("w:ins" if kind == "ins" else "w:del")
        wrapper.append(make_run(text, deleted=(kind == "del")))
        p._p.append(wrapper)


def mark_paragraph(p, kind, revs):
    """Track the paragraph mark itself, so Reject/Accept removes the whole paragraph."""
    rpr = OxmlElement("w:rPr")
    rpr.append(revs.mark("w:ins" if kind == "ins" else "w:del"))
    p._p.get_or_add_pPr().append(rpr)


def tokens(text):
    return re.findall(r"\w+|\s+|[^\w\s]", text)


def word_diff(old, new):
    """[(kind, text)] turning old into new, word by word.

    Short unchanged stretches (fewer than MIN_KEEP words) between two edits are
    folded into the edit, so a rewritten sentence reads as one deletion followed by
    one insertion rather than alternating single words.
    """
    a, b = tokens(old), tokens(new)
    ops = SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
    out, dels, ins = [], [], []
    for n, (op, i1, i2, j1, j2) in enumerate(ops):
        same = "".join(a[i1:i2])
        between_edits = 0 < n < len(ops) - 1
        if op == "equal" and not (between_edits and len(same.split()) < MIN_KEEP):
            if dels or ins:
                out += [("del", "".join(dels)), ("ins", "".join(ins))]
                dels, ins = [], []
            out.append(("equal", same))
            continue
        dels.append(same)
        ins.append("".join(b[j1:j2]))
    if dels or ins:
        out += [("del", "".join(dels)), ("ins", "".join(ins))]
    return [(k, t) for k, t in out if t]


def similarity(a, b):
    return SequenceMatcher(None, a.split(), b.split(), autojunk=False).ratio()


def align(standard, tailored):
    """Yield ('equal'|'modify'|'delete'|'insert', std_para, new_para) in document order."""
    std_text, new_text = [t for _, t in standard], [t for _, t in tailored]
    for op, i1, i2, j1, j2 in SequenceMatcher(None, std_text, new_text, autojunk=False).get_opcodes():
        if op == "equal":
            for k in range(i2 - i1):
                yield "equal", standard[i1 + k], tailored[j1 + k]
            continue
        # Within a changed block, pair each new paragraph with the next similar old one.
        i = i1
        for j in range(j1, j2):
            match = next((k for k in range(i, i2)
                          if similarity(std_text[k], new_text[j]) >= SIMILARITY), None)
            if match is None:
                yield "insert", None, tailored[j]
                continue
            for k in range(i, match):
                yield "delete", standard[k], None
            yield "modify", standard[match], tailored[j]
            i = match + 1
        for k in range(i, i2):
            yield "delete", standard[k], None


def read_letter(path):
    """The body paragraphs of a letter written by fill_template.py, as [(style, text)]."""
    return [(p.style.name, p.text) for p in Document(str(path)).paragraphs
            if p.style.name in (BODY_STYLE, HEADING_STYLE)]


def enable_track_changes(doc):
    """Turn Track Changes on so the lawyer's further edits are tracked too."""
    settings = doc.settings.element
    if settings.find(qn("w:trackRevisions")) is None:
        settings.insert(0, OxmlElement("w:trackRevisions"))


def build_redline(intake, letter_path, out_path):
    standard, tailored = standard_paragraphs(intake), read_letter(letter_path)
    doc, body = open_letterhead(build_fields(intake))
    revs = Revisions()
    counts = {"equal": 0, "modify": 0, "insert": 0, "delete": 0}

    for kind, old, new in align(standard, tailored):
        counts[kind] += 1
        style = (new or old)[0]
        p = body.insert_paragraph_before(style=style)
        if kind == "equal":
            set_text(p, new[1])
        elif kind == "modify":
            for seg_kind, text in word_diff(old[1], new[1]):
                add_segment(p, seg_kind, text, revs)
        else:
            seg = "ins" if kind == "insert" else "del"
            add_segment(p, seg, (new or old)[1], revs)
            mark_paragraph(p, seg, revs)

    body._p.getparent().remove(body._p)
    enable_track_changes(doc)
    doc.save(str(out_path))
    return counts, revs.next_id - 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--intake", required=True, help="the same intake JSON given to fill_template.py")
    ap.add_argument("--letter", required=True, help="tailored letter .docx from fill_template.py")
    ap.add_argument("--out", required=True, help="output redline .docx path")
    args = ap.parse_args(argv)

    intake = json.loads(Path(args.intake).read_text(encoding="utf-8"))
    counts, n = build_redline(intake, args.letter, args.out)
    print(json.dumps({"redline": args.out, "tracked_revisions": n,
                      "paragraphs_unchanged": counts["equal"], "paragraphs_modified": counts["modify"],
                      "paragraphs_inserted": counts["insert"], "paragraphs_deleted": counts["delete"]},
                     indent=2))


if __name__ == "__main__":
    main()
