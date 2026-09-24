"""Validate a results.json file against assets/results.schema.json.

Usage: python validate_results.py results.json

Uses the jsonschema package if it is installed; otherwise checks only that the
required top-level sections are present.
"""

import json
import sys
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "assets" / "results.schema.json"


def validate(results):
    """Return a list of error strings (empty if valid)."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        import jsonschema
    except ImportError:
        missing = [key for key in schema["required"] if key not in results]
        return [f"missing top-level section: {key}" for key in missing]
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(str(p) for p in error.absolute_path) or '(root)'}: {error.message}"
            for error in sorted(validator.iter_errors(results), key=lambda e: list(e.absolute_path))]


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    results = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    errors = validate(results)
    for error in errors[:50]:
        print(error)
    print("valid" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
