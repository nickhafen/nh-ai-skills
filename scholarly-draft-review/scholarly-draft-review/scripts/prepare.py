"""Set up a working folder for one review.

Usage:
    python prepare.py <draft> --out <working-folder>

<draft> can be .md, .txt, or .docx. For PDFs or anything else, extract the text
first and save it as a .txt or .md file.

Writes <working-folder>/document.md (the text every quote is checked against),
key-sentences.md (the first sentence of each body paragraph), and source.json (the
draft's filename, so reports can refer to the draft without including it). Word headings
become markdown headings, and Word footnotes are kept: each reference becomes [^n] and the
notes follow under "## Footnotes".
"""

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import quality

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
HEADING_STYLE = re.compile(r"^(?:heading|berschrift|titre)\s*([1-6])$|^title$", re.I)


def paragraph_text(p, note_numbers=None):
    """Text of one w:p, with footnote references as [^n] when note_numbers is given."""
    parts = []
    for el in p.iter():
        if el.tag == f"{W}t":
            parts.append(el.text or "")
        elif el.tag == f"{W}tab":
            parts.append(" ")
        elif el.tag == f"{W}footnoteReference" and note_numbers is not None:
            note_id = el.get(f"{W}id")
            number = note_numbers.setdefault(note_id, len(note_numbers) + 1)
            parts.append(f"[^{number}]")
    return "".join(parts).strip()


def heading_level(p):
    style = p.find(f"{W}pPr/{W}pStyle")
    if style is None:
        return None
    match = HEADING_STYLE.match((style.get(f"{W}val") or "").replace("-", " ").strip())
    if not match:
        return None
    return int(match.group(1)) if match.group(1) else 1


def docx_text(path):
    """Plain text of a .docx: one paragraph per block, headings marked, footnotes appended."""
    with zipfile.ZipFile(path) as z:
        root = ElementTree.fromstring(z.read("word/document.xml"))
        notes_xml = z.read("word/footnotes.xml") if "word/footnotes.xml" in z.namelist() else None
    note_numbers = {}
    blocks = []
    for p in root.iter(f"{W}p"):
        text = paragraph_text(p, note_numbers)
        if not text:
            continue
        level = heading_level(p)
        blocks.append(f"{'#' * level} {text}" if level else text)
    if notes_xml and note_numbers:
        notes = {n.get(f"{W}id"): n for n in ElementTree.fromstring(notes_xml).iter(f"{W}footnote")}
        lines = []
        for note_id, number in sorted(note_numbers.items(), key=lambda item: item[1]):
            note = notes.get(note_id)
            body = " ".join(filter(None, (paragraph_text(p) for p in note.iter(f"{W}p")))) if note is not None else ""
            lines.append(f"[^{number}]: {body}")
        blocks += ["## Footnotes"] + lines
    return "\n\n".join(blocks)


def read_document(path):
    path = Path(path)
    if path.suffix.lower() == ".docx":
        return docx_text(path)
    if path.suffix.lower() in (".md", ".txt", ".markdown", ".text", ""):
        return path.read_text(encoding="utf-8-sig")
    raise SystemExit(f"Can't read {path.suffix} files directly. Extract the text, save it as .txt, and rerun.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("document")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    text = read_document(args.document).replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    out = Path(args.out)
    (out / "reviews").mkdir(parents=True, exist_ok=True)
    (out / "document.md").write_text(text, encoding="utf-8")
    (out / "key-sentences.md").write_text(quality.key_sentence_outline(text), encoding="utf-8")
    (out / "source.json").write_text(json.dumps({"source_file": Path(args.document).name}), encoding="utf-8")

    sections = quality.split_sections(text.strip())
    outline = quality.key_sentences(text.strip(), sections)
    print(f"Working folder: {out}")
    print(f"Draft: {Path(args.document).name}, {len(text.split())} words, {len(sections)} sections, "
          f"{len(outline)} body paragraphs")
    if len(outline) >= 8:
        print("Key-sentence outline written to key-sentences.md.")
    else:
        print("Fewer than 8 body paragraphs: skip the key-sentence check.")
    print("\nNext: write setup.json, reviews/<persona-id>.json, related-work.json, key-sentences.json (if the"
          " check applies), and synthesis.json, then run finalize.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
