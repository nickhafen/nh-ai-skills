"""Check every persona file against the shared schema.

Usage (from extras/): python build/check_personas.py
Exits non-zero if any persona is missing a heading, a front-matter field,
or the reading-stance instruction, or has fewer than 4 or more than 7
look-for items. Word counts outside the target are reported, not failed.
"""

import re
import sys
from pathlib import Path

PERSONA_DIR = Path(__file__).resolve().parents[2] / "fresh-eyes-review" / "references" / "personas"

REQUIRED_HEADINGS = [
    "## 1. Role and relationship to the author",
    "## 2. What they want from the document",
    "## 3. What they know and don't know",
    "## 4. Information access tier",
    "## 5. What they look for",
    "## 6. Attention budget",
    "## 7. Common misreadings and friction points",
    "## 8. What earns their trust or moves them",
    "## 9. Likely next actions",
    "## 10. Adaptable parameters",
    "## 11. Out of scope for this persona",
    "## Common variant",
]
REQUIRED_FIELDS = ["id", "name", "tier", "typical_documents", "status"]
STANCE_MARKER = "**How to read as this persona.**"
WORD_RANGE = (300, 500)


def parse_front_matter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None, text
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.split("#", 1)[0].strip()
    return fields, text[match.end():]


def check(path):
    problems = []
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    fields, body = parse_front_matter(text)
    if fields is None:
        return ["missing front matter"], 0

    for field in REQUIRED_FIELDS:
        if not fields.get(field):
            problems.append(f"missing front-matter field: {field}")
    if fields.get("id") and fields["id"] != path.stem:
        problems.append(f"id '{fields['id']}' does not match file name")
    if fields.get("tier") not in {"A", "B", "C"}:
        problems.append(f"tier must be A, B, or C (got '{fields.get('tier')}')")

    if STANCE_MARKER not in body:
        problems.append("missing reading-stance instruction")

    positions = []
    for heading in REQUIRED_HEADINGS:
        pos = body.find(heading)
        if pos == -1:
            problems.append(f"missing heading: {heading}")
        positions.append(pos)
    found = [p for p in positions if p != -1]
    if found != sorted(found):
        problems.append("headings out of order")

    look_for = re.search(r"## 5\. What they look for\n(.*?)\n## ", body, re.S)
    if look_for:
        count = len(re.findall(r"^- ", look_for.group(1), re.M))
        if not 4 <= count <= 7:
            problems.append(f"look-for items: {count} (expected 4-7)")

    # Word count excludes the shared stance instruction and roster notes.
    counted = re.sub(r"^>.*$", "", body, flags=re.M)
    words = len(re.findall(r"\b\w[\w'’-]*\b", counted))
    return problems, words


def main():
    files = sorted(p for p in PERSONA_DIR.glob("*.md") if not p.name.startswith("_"))
    failed = False
    for path in files:
        problems, words = check(path)
        lo, hi = WORD_RANGE
        note = "" if lo <= words <= hi else f"  (outside {lo}-{hi} target)"
        status = "FAIL" if problems else "ok"
        print(f"{status:4}  {path.stem:34} {words:4} words{note}")
        for problem in problems:
            print(f"        - {problem}")
        failed = failed or bool(problems)
    print(f"\n{len(files)} persona files checked.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
