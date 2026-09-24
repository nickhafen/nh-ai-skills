"""Generate the portable (paste-in) versions of the skill from the canonical skill folder.

Usage (from extras/):
    python build/build_portable.py           # write portable/
    python build/build_portable.py --check   # exit 1 if portable/ is out of date

SKILL.md passages wrapped in <!-- skill-only --> ... <!-- /skill-only --> are removed;
passages wrapped in <!-- portable-only --> ... <!-- /portable-only --> are kept (markers
stripped). Reference files are appended unchanged. Nothing in portable/ is edited by hand.
"""

import argparse
import re
import sys
from pathlib import Path

EXTRAS_DIR = Path(__file__).resolve().parent.parent
SKILL_DIR = EXTRAS_DIR.parent / "fresh-eyes-review"
REFS = SKILL_DIR / "references"
OUT = EXTRAS_DIR / "portable"

REFERENCE_ORDER = ["house-settings.md", "doc-type-map.md", "persona-review-format.md",
                   "ai-reader-prompts.md", "synthesis-rubric.md"]
# output-spec.md is left out: it mostly describes results.json, which portable versions never produce.
# The personas most default document types use. The lite prompt includes only these.
LITE_PERSONAS = ["senior-colleague", "client-individual", "client-business-decision-maker",
                 "opposing-counsel", "opposing-party-unrepresented", "trial-judge",
                 "counterparty-business-contact", "future-interpreting-court"]

HEADER = """# fresh-eyes-review: paste-in prompt{variant}

**How to use:** paste everything below into a new chat with an AI assistant (Claude, ChatGPT, or Gemini). Then paste your document, and add anything optional: what you want the reader to do, background (say what's privileged), and who will read it.

This is a writing review, not a legal review. It doesn't check whether the law, facts, or citations are correct. Don't paste anything you aren't permitted to share with the AI service you're using.

Generated from the fresh-eyes-review skill{content_note}. Don't edit this file; edit the skill and rebuild.

---

"""


def portable_instructions():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"<!-- skill-only -->.*?<!-- /skill-only -->\n?", "", text, flags=re.S)
    text = re.sub(r"<!-- /?portable-only -->\n?", "", text)
    if "<!--" in text:
        raise SystemExit("Unmatched marker left in SKILL.md after processing")
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def reference_block(name, path):
    body = path.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    body = re.sub(r"^---\n.*?\n---\n", "", body, flags=re.S).strip()
    # Demote headings so each file sits under its own "File:" heading.
    body = re.sub(r"^(#{1,5}) ", lambda m: "#" * (len(m.group(1)) + 2) + " ", body, flags=re.M)
    return f"## File: {name}\n\n{body}\n"


def build(lite):
    persona_files = sorted(p for p in (REFS / "personas").glob("*.md") if not p.name.startswith("_"))
    if lite:
        persona_files = [p for p in persona_files if p.stem in LITE_PERSONAS]
    parts = [HEADER.format(variant=" (lite)" if lite else "",
                           content_note=", lite version with the most-used personas" if lite else ""),
             portable_instructions(), "\n---\n\n# Reference files\n\n"]
    if lite:
        omitted = sorted(p.stem for p in (REFS / "personas").glob("*.md")
                         if not p.name.startswith("_") and p.stem not in LITE_PERSONAS)
        parts.append("This lite version includes only some personas. If the document-type map calls for one that "
                     "isn't included (" + ", ".join(omitted) + "), use the closest included persona and say so.\n\n")
    for name in REFERENCE_ORDER:
        parts.append(reference_block(name, REFS / name) + "\n")
    parts.append(reference_block("personas/_template.md", REFS / "personas" / "_template.md") + "\n")
    for path in persona_files:
        parts.append(reference_block(f"personas/{path.name}", path) + "\n")
    return "".join(parts).rstrip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    outputs = {OUT / "single-prompt.md": build(lite=False), OUT / "single-prompt-lite.md": build(lite=True)}
    stale = []
    for path, text in outputs.items():
        words = len(text.split())
        print(f"{path.relative_to(EXTRAS_DIR)}: {words} words, ~{len(text) // 4} tokens")
        if args.check:
            current = path.read_text(encoding="utf-8") if path.exists() else None
            if current != text:
                stale.append(path.name)
        else:
            path.parent.mkdir(exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
    if stale:
        print("Out of date: " + ", ".join(stale) + ". Run python build/build_portable.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
