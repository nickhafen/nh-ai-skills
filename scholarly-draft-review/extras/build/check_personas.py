"""Check every persona file against the shared schema in personas/_template.md.

Usage (from extras/): python build/check_personas.py
Exits non-zero if any persona is missing a heading or a front-matter field, has an
invalid reader_type, briefing, or stage, changes the reading-stance instruction, or has
fewer than 4 or more than 7 look-for items. Word counts outside the target are reported,
not failed. Also checks that every persona the stage map names exists.
"""

import re
import sys
from pathlib import Path

REFS = Path(__file__).resolve().parents[2] / "scholarly-draft-review" / "references"
PERSONA_DIR = REFS / "personas"

REQUIRED_HEADINGS = [
    "## 1. Role and relationship to the author",
    "## 2. What they want from the draft",
    "## 3. What they know and don't know",
    "## 4. Briefing",
    "## 5. What they look for",
    "## 6. Common misreadings and friction points",
    "## 7. What earns their trust or moves them",
    "## 8. Adaptable parameters",
    "## 9. Out of scope for this persona",
    "## Common variant",
]
REQUIRED_FIELDS = ["id", "name", "reader_type", "briefing", "status"]
READER_TYPES = {"nonexpert", "expert", "Expert", "gatekeeper"}
STANCE = re.compile(r"^> \*\*How to read as this persona\.\*\*.*$", re.M)
WORD_RANGE = (250, 550)


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


def stance(text):
    match = STANCE.search(text)
    return match.group(0) if match else None


def check(path, template_stance):
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
    if fields.get("reader_type") not in READER_TYPES:
        problems.append(f"reader_type must be one of {sorted(READER_TYPES)} (got '{fields.get('reader_type')}')")
    if fields.get("briefing") not in ("briefed", "cold"):
        problems.append(f"briefing must be briefed or cold (got '{fields.get('briefing')}')")

    if stance(body) != template_stance:
        problems.append("reading-stance instruction missing or not verbatim from _template.md")

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

    counted = re.sub(r"^>.*$", "", body, flags=re.M)  # the shared stance instruction isn't counted
    words = len(re.findall(r"\b\w[\w'’-]*\b", counted))
    return problems, words


def stage_map_ids():
    text = (REFS / "stage-map.md").read_text(encoding="utf-8")
    return set(re.findall(r"`([a-z]+(?:-[a-z]+)+)`", text))


def main():
    template_stance = stance((PERSONA_DIR / "_template.md").read_text(encoding="utf-8").replace("\r\n", "\n"))
    files = sorted(p for p in PERSONA_DIR.glob("*.md") if not p.name.startswith("_"))
    failed = False
    for path in files:
        problems, words = check(path, template_stance)
        lo, hi = WORD_RANGE
        note = "" if lo <= words <= hi else f"  (outside {lo}-{hi} target)"
        print(f"{'FAIL' if problems else 'ok':4}  {path.stem:26} {words:4} words{note}")
        for problem in problems:
            print(f"        - {problem}")
        failed = failed or bool(problems)
    missing = sorted(i for i in stage_map_ids() if i not in {p.stem for p in files} and "-" in i
                     and i != "key-sentence")
    for persona_id in missing:
        print(f"FAIL  stage-map.md names '{persona_id}', which has no persona file")
        failed = True
    print(f"\n{len(files)} persona files checked.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
