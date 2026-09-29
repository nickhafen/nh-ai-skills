"""Generate the paste-in prompt from the canonical skill folder.

Usage (from extras/):
    python build/build_portable.py           # write portable/single-prompt.md
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
SKILL_DIR = EXTRAS_DIR.parent / "scholarly-draft-review"
REFS = SKILL_DIR / "references"
OUT = EXTRAS_DIR / "portable" / "single-prompt.md"

REFERENCE_ORDER = ["house-settings.md", "stage-map.md", "persona-review-format.md", "synthesis-rubric.md"]
# output-spec.md is left out: it describes results.json, which the paste-in version never produces.

HEADER = """# scholarly-draft-review: paste-in prompt

**How to use:** paste everything below into a new chat with an AI assistant (Claude, ChatGPT, or Gemini). Then paste your draft. Optionally add the stage it's at, whether you're faculty or a student, where it's headed, your claim in one sentence, what feedback you want, and anything you already know is missing.

This gives feedback only. It doesn't draft or rewrite, and it isn't a cite-check. The AI can be wrong, including about sources: verify anything you act on. Follow any rules that apply to your use of AI tools, such as a journal's or publisher's policy.

Generated from the scholarly-draft-review skill. Don't edit this file; edit the skill and rebuild.

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


def build():
    persona_files = sorted(p for p in (REFS / "personas").glob("*.md") if not p.name.startswith("_"))
    parts = [HEADER, portable_instructions(), "\n---\n\n# Reference files\n\n"]
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
    text = build()
    print(f"{OUT.relative_to(EXTRAS_DIR)}: {len(text.split())} words, ~{len(text) // 4} tokens")
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else None
        if current != text:
            print("Out of date. Run python build/build_portable.py")
            return 1
        return 0
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
