"""Set up a working folder for one review.

Usage:
    python prepare.py <document> --out <working-folder>

<document> can be .md, .txt, or .docx. For PDFs or anything else, extract the text
first and save it as a .txt or .md file.

Writes <working-folder>/document.md (the text every quote is checked against) and
prints the section ids to use in attention maps.
"""

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import quality

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def docx_text(path):
    """Plain text of a .docx, one paragraph per blank-line-separated block."""
    with zipfile.ZipFile(path) as z:
        root = ElementTree.fromstring(z.read("word/document.xml"))
    paragraphs = []
    for p in root.iter(f"{W}p"):
        text = "".join(t.text or "" for t in p.iter(f"{W}t"))
        if text.strip():
            paragraphs.append(text.strip())
    return "\n\n".join(paragraphs)


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

    sections = quality.split_sections(text.strip())
    print(f"Working folder: {out}")
    print(f"Document: {len(text.split())} words, {len(sections)} sections\n")
    print("Section ids for attention maps:")
    for s in sections:
        print(f"  {s['id']}: {s['label']}")
    print("\nNext: write setup.json, then reviews/<persona-id>.json, then (optionally) ai-reader.json,"
          " then synthesis.json, then run finalize.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
