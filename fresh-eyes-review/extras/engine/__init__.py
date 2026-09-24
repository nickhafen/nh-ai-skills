"""fresh-eyes-review pipeline engine.

Runs persona reviews, the AI-reader check, and synthesis through a model client,
and produces a results.json. The eval harness uses it now; a web app can reuse it
later. Content (personas, prompts, rubric) lives in the skill folder (../fresh-eyes-review/) and is
read from there, never duplicated here.
"""

import sys
from pathlib import Path

# Layout: <project>/fresh-eyes-review/ is the skill; <project>/extras/ holds this package and the tools.
EXTRAS_DIR = Path(__file__).resolve().parent.parent
SKILL_DIR = EXTRAS_DIR.parent / "fresh-eyes-review"
REFERENCES_DIR = SKILL_DIR / "references"
SCRIPTS_DIR = SKILL_DIR / "scripts"
SCHEMA_PATH = SKILL_DIR / "assets" / "results.schema.json"

TOOL_VERSION = "0.1.0-dev"

# The skill's deterministic scripts are the single implementation of quality checks.
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
