"""Load the canonical reference files from the skill folder."""

import copy
import hashlib
import json
import re
import subprocess

from . import REFERENCES_DIR, EXTRAS_DIR, SCHEMA_PATH, SKILL_DIR

PERSONA_DIR = REFERENCES_DIR / "personas"


def read_reference(name):
    return (REFERENCES_DIR / name).read_text(encoding="utf-8")


def load_persona(persona_id):
    """Return (front_matter dict, body text without front matter)."""
    path = PERSONA_DIR / f"{persona_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"No persona file for '{persona_id}' in {PERSONA_DIR}")
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fields = {}
    body = text
    if match:
        body = text[match.end():]
        for line in match.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                fields[key.strip()] = value.split("#", 1)[0].strip()
    return fields, body.strip()


def adapt_persona(persona_id, adaptations=(), added_context=()):
    """Apply per-document adaptations within the schema's bounds and return the adapted text.

    Adaptations only set values for the persona's adaptable parameters and add context
    the reader would plausibly have. They never add personality, names, or traits.
    """
    fields, body = load_persona(persona_id)
    lines = []
    for a in adaptations:
        lines.append(f"- {a['parameter']}: {a['value']} ({a['reason']})")
    for c in added_context:
        lines.append(f"- Context this reader would have: {c}")
    if lines:
        body += "\n\n## Adaptations for this document\n\n" + "\n".join(lines)
    return fields, body


def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def model_schema(def_name):
    """Return a $defs entry with $refs inlined, ready to send as a structured-output format."""
    schema = load_schema()
    defs = schema["$defs"]

    def resolve(node):
        if isinstance(node, dict):
            if "$ref" in node:
                return resolve(copy.deepcopy(defs[node["$ref"].split("/")[-1]]))
            return {k: resolve(v) for k, v in node.items() if k != "description"}
        if isinstance(node, list):
            return [resolve(v) for v in node]
        return node

    return resolve(copy.deepcopy(defs[def_name]))


def content_hash():
    """Hash of every file in the skill folder, so results can be tied to the exact content used."""
    digest = hashlib.sha256()
    for path in sorted(SKILL_DIR.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            digest.update(str(path.relative_to(SKILL_DIR)).replace("\\", "/").encode())
            digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()[:16]


def git_commit():
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=EXTRAS_DIR,
                             capture_output=True, text=True, timeout=10)
        commit = out.stdout.strip()
        if out.returncode != 0 or not commit:
            return None
        dirty = subprocess.run(["git", "status", "--porcelain", "--", str(SKILL_DIR)], cwd=EXTRAS_DIR,
                               capture_output=True, text=True, timeout=10).stdout.strip()
        return commit + ("-dirty" if dirty else "")
    except (OSError, subprocess.SubprocessError):
        return None
