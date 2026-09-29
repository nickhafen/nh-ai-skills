"""Build the skills site: zips, file copies, manifest, and the viewer.

Usage: python site/build.py --out dist

A skill is any top-level folder X/ that contains X/X/SKILL.md. Each one gets:
  dist/downloads/X.zip  the inner skill folder, entries under X/, byte-for-byte
                        reproducible from the same content
  dist/files/X/...      every file in X/ (extras included), copied unchanged
and an entry in dist/manifest.json. The viewer files in site/ are copied to dist/.

Files Git ignores are skipped, along with .git* files and OS clutter.
Standard library only (Python 3.12+), so CI has nothing to install.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import stat
import sys
import zipfile
from pathlib import Path

REPO_URL = "https://github.com/nickhafen/nh-ai-skills"
SITE_DIR = Path(__file__).resolve().parent
VIEWER_FILES = ["index.html", "app.js", "styles.css", "labels.json"]
CLUTTER = {".DS_Store", "Thumbs.db", "desktop.ini"}
ZIP_DATE = (1980, 1, 1, 0, 0, 0)

KINDS = {
    ".md": ("markdown", None),
    ".json": ("json", "json"),
    ".py": ("code", "python"),
    ".js": ("code", "javascript"),
    ".mjs": ("code", "javascript"),
    ".ts": ("code", "typescript"),
    ".html": ("code", "xml"),
    ".css": ("code", "css"),
    ".sh": ("code", "bash"),
    ".ps1": ("code", "powershell"),
    ".yaml": ("code", "yaml"),
    ".yml": ("code", "yaml"),
    ".toml": ("code", "ini"),
    ".txt": ("text", None),
    ".csv": ("text", None),
}
BINARY_EXTS = {".docx", ".xlsx", ".pptx", ".pdf", ".zip", ".png", ".jpg",
               ".jpeg", ".gif", ".webp", ".ico", ".woff", ".woff2", ".ttf"}


class BuildError(Exception):
    pass


# ---------------------------------------------------------------- file listing

def list_files(root):
    """Repo-relative POSIX paths of files Git would track (tracked plus
    untracked-but-not-ignored). Falls back to walking the folder without
    .gitignore support when Git isn't available."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others",
             "--exclude-standard"],
            capture_output=True, check=True).stdout
        paths = {p for p in out.decode("utf-8").split("\0") if p}
        paths = {p for p in paths if (root / p).is_file()}  # drop deleted files
    except (OSError, subprocess.CalledProcessError):
        print("note: not a Git checkout; .gitignore rules are not applied",
              file=sys.stderr)
        paths = set()
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for name in filenames:
                paths.add((Path(dirpath) / name).relative_to(root).as_posix())
    return sorted(p for p in paths if not _skipped(p))


def _skipped(path):
    return any(part.startswith(".git") or part in CLUTTER
               for part in path.split("/"))


# ---------------------------------------------------------------- frontmatter

def parse_frontmatter(text):
    """Read the simple YAML subset SKILL.md frontmatter uses: top-level
    `key: value` pairs, quoted strings, and folded or literal blocks."""
    text = text.lstrip("﻿")
    m = re.match(r"---\r?\n(.*?)\r?\n---\s*(\r?\n|$)", text, re.S)
    if not m:
        return None
    fields, key, lines, style = {}, None, [], None

    def flush():
        if key is None:
            return
        if style == "|":
            fields[key] = "\n".join(lines).strip()
        else:
            fields[key] = " ".join(l.strip() for l in lines if l.strip())

    for line in m.group(1).splitlines():
        top = re.match(r"([A-Za-z_][\w-]*):(?:\s+(.*))?$", line)
        if top and not line[0].isspace():
            flush()
            key, value = top.group(1), (top.group(2) or "").strip()
            style, lines = None, []
            if value in ("|", "|-", ">", ">-"):
                style = value[0]
            elif value.startswith('"') and value.endswith('"') and len(value) > 1:
                lines = [json.loads(value)]
            elif value.startswith("'") and value.endswith("'") and len(value) > 1:
                lines = [value[1:-1].replace("''", "'")]
            else:
                lines = [value]
        elif key is not None:
            lines.append(line)
    flush()
    return fields


# ---------------------------------------------------------------- README table

def readme_rows(root):
    """Map skill id -> 'What it does' cell from the README table."""
    readme = root / "README.md"
    rows = {}
    if not readme.is_file():
        return rows
    for line in readme.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*\[([^\]]+)\]\([^)]*\)\s*\|(.*)\|\s*$", line)
        if m:
            rows[m.group(1).strip()] = m.group(2).strip()
    return rows


def summarize_row(cell):
    """Turn a README cell into a card summary and a pre-release flag. Drops
    links (keeping their text) and the sentences that point to other docs."""
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", cell)
    text = re.sub(r"[`*_]", "", text)
    sentences = re.split(r"(?<=\.)\s+(?=[A-Z])", text)
    pre = any(s.strip().rstrip(".").lower() == "pre-release" for s in sentences)
    keep = [s for s in sentences
            if s.strip().rstrip(".").lower() != "pre-release"
            and not re.match(r"(See its|Its)\b", s.strip())]
    return " ".join(keep).strip(), pre


# ---------------------------------------------------------------- tree + kinds

def file_kind(path):
    ext = path.suffix.lower()
    with open(path, "rb") as f:
        head = f.read(8192)
    if ext in BINARY_EXTS or b"\0" in head:
        return "binary", None
    if ext in KINDS:
        return KINDS[ext]
    try:
        head.decode("utf-8")
    except UnicodeDecodeError:
        # A multibyte character cut off at the 8 KB boundary still counts as text.
        try:
            head[:-3].decode("utf-8")
        except UnicodeDecodeError:
            return "binary", None
    return "text", None


def build_tree(root, skill_id, paths):
    """Nested dir/file nodes for everything under skill_id/. Folders first,
    then files, each alphabetical."""
    top = {"type": "dir", "name": skill_id, "role": "skill-root", "children": []}
    for rel in paths:
        parts = rel.split("/")[1:]
        node = top
        for depth, part in enumerate(parts[:-1]):
            child = next((c for c in node["children"]
                          if c["type"] == "dir" and c["name"] == part), None)
            if child is None:
                child = {"type": "dir", "name": part, "children": []}
                if depth == 0 and part == skill_id:
                    child["role"] = "skill"
                elif depth == 0 and part == "extras":
                    child["role"] = "extras"
                node["children"].append(child)
            node = child
        full = root / rel
        kind, lang = file_kind(full)
        leaf = {"type": "file", "name": parts[-1], "bytes": full.stat().st_size,
                "kind": kind}
        if lang:
            leaf["lang"] = lang
        node["children"].append(leaf)
    _sort(top)
    return top


def _sort(node):
    node["children"].sort(key=lambda c: (c["type"] != "dir", c["name"].lower(),
                                         c["name"]))
    for c in node["children"]:
        if c["type"] == "dir":
            _sort(c)


# ---------------------------------------------------------------- zips

def write_zip(root, skill_id, paths, dest):
    """Zip the inner skill folder with entries under skill_id/, the same shape
    a right-click compress makes. Fixed timestamps, sorted entries, and fixed
    attributes make it reproducible."""
    inner = f"{skill_id}/{skill_id}/"
    files = [p for p in paths if p.startswith(inner)]
    names = {p[len(skill_id) + 1:]: p for p in files}  # entry name -> repo path
    dirs = set()
    for name in names:
        parts = name.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            dirs.add("/".join(parts[:i]) + "/")
    with zipfile.ZipFile(dest, "w") as zf:
        for entry in sorted(dirs | set(names)):
            info = zipfile.ZipInfo(entry, date_time=ZIP_DATE)
            info.create_system = 3  # Unix, so attributes read the same everywhere
            if entry.endswith("/"):
                info.external_attr = (0o40755 << 16) | 0x10
                zf.writestr(info, b"")
            else:
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                data = (root / names[entry]).read_bytes()
                zf.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED,
                            compresslevel=9)
    check_zip(dest, skill_id)


def check_zip(path, skill_id):
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        bad = zf.testzip()
    if bad:
        raise BuildError(f"{path.name}: corrupt entry {bad}")
    if f"{skill_id}/SKILL.md" not in names:
        raise BuildError(f"{path.name}: no {skill_id}/SKILL.md in the zip")
    stray = [n for n in names if not n.startswith(f"{skill_id}/")
             or n.startswith(f"{skill_id}/extras/")]
    if stray:
        raise BuildError(f"{path.name}: entries outside the skill: {stray[:5]}")


# ---------------------------------------------------------------- skills

def find_skills(root, paths):
    """Top-level folders X with X/X/SKILL.md. A same-named inner folder
    without SKILL.md is an error, since it looks like a broken skill."""
    tops = sorted({p.split("/")[0] for p in paths if "/" in p})
    skills = []
    for top in tops:
        if f"{top}/{top}/SKILL.md" in paths:
            skills.append(top)
        elif any(p.startswith(f"{top}/{top}/") for p in paths):
            raise BuildError(f"{top}/{top}/ has no SKILL.md")
    if not skills:
        raise BuildError("no skills found")
    return skills


def skill_meta(root, skill_id, rows):
    fm = parse_frontmatter(
        (root / skill_id / skill_id / "SKILL.md").read_text(encoding="utf-8"))
    if fm is None:
        raise BuildError(f"{skill_id}/{skill_id}/SKILL.md has no frontmatter")
    for field in ("name", "description"):
        if not fm.get(field):
            raise BuildError(
                f"{skill_id}/{skill_id}/SKILL.md frontmatter is missing '{field}'")

    summary, pre = fm["description"], False
    if skill_id in rows:
        summary, pre = summarize_row(rows[skill_id])
    site_json = root / skill_id / "extras" / "site.json"
    if site_json.is_file():
        extra = json.loads(site_json.read_text(encoding="utf-8"))
        summary = extra.get("summary", summary)
        if "status" in extra:
            pre = extra["status"] == "pre-release"
    return {"name": fm["name"], "description": fm["description"],
            "summary": summary, "status": "pre-release" if pre else "stable"}


def commit_id(root):
    sha = os.environ.get("GITHUB_SHA")
    if sha:
        return sha[:7]
    try:
        return subprocess.run(["git", "-C", str(root), "rev-parse", "--short",
                               "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _remove_tree(path):
    # OneDrive marks synced folders read-only, which blocks rmtree on Windows.
    def clear_readonly(func, target, _exc):
        os.chmod(target, stat.S_IWRITE)
        func(target)
    shutil.rmtree(path, onexc=clear_readonly)


def build(root, out):
    root, out = Path(root).resolve(), Path(out).resolve()
    if out.exists():
        if any(out.iterdir()) and not (out / "manifest.json").exists():
            raise BuildError(f"{out} exists and isn't a previous build; "
                             "not deleting it")
        _remove_tree(out)
    (out / "downloads").mkdir(parents=True)

    paths = list_files(root)
    rows = readme_rows(root)
    skills = []
    # Cards follow the README table's order; skills not in it go last.
    order = list(rows)
    found = sorted(find_skills(root, set(paths)),
                   key=lambda s: (order.index(s) if s in order else len(order), s))
    for skill_id in found:
        mine = [p for p in paths if p.startswith(skill_id + "/")]
        meta = skill_meta(root, skill_id, rows)

        zip_path = out / "downloads" / f"{skill_id}.zip"
        write_zip(root, skill_id, mine, zip_path)
        data = zip_path.read_bytes()

        for rel in mine:
            dest = out / "files" / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / rel, dest)

        skills.append({
            "id": skill_id,
            **meta,
            "zip": {"path": f"downloads/{skill_id}.zip", "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest()},
            "tree": build_tree(root, skill_id, mine),
        })
        print(f"  {skill_id}: {len(mine)} files, zip {len(data):,} bytes")

    manifest = {
        "generated": datetime.datetime.now(datetime.timezone.utc)
                     .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": commit_id(root),
        "repo": REPO_URL,
        "skills": skills,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1),
                                       encoding="utf-8")
    for name in VIEWER_FILES:
        if not (SITE_DIR / name).is_file():
            raise BuildError(f"site/{name} is missing")
        shutil.copyfile(SITE_DIR / name, out / name)
    return manifest


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="dist", help="output folder (default: dist)")
    ap.add_argument("--root", default=SITE_DIR.parent,
                    help="repo root (default: the folder above site/)")
    args = ap.parse_args()
    try:
        manifest = build(args.root, args.out)
    except BuildError as e:
        sys.exit(f"build failed: {e}")
    print(f"Built {len(manifest['skills'])} skills into {args.out}")


if __name__ == "__main__":
    main()
