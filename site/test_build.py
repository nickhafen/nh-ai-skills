"""Checks CI runs before every deploy: python -m unittest discover -s site"""

import hashlib
import json
import re
import tempfile
import unittest
import zipfile
from pathlib import Path

import build

ROOT = Path(__file__).resolve().parent.parent


def files_in(node, prefix=""):
    path = f"{prefix}{node['name']}"
    if node["type"] == "file":
        yield path
    else:
        for child in node["children"]:
            yield from files_in(child, path + "/")


class RepoBuild(unittest.TestCase):
    """Builds the real repo twice and checks the output."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out1 = Path(cls.tmp.name) / "a"
        cls.out2 = Path(cls.tmp.name) / "b"
        cls.manifest = build.build(ROOT, cls.out1)
        build.build(ROOT, cls.out2)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_zips_have_skill_md_and_no_extras(self):
        for skill in self.manifest["skills"]:
            sid = skill["id"]
            with zipfile.ZipFile(self.out1 / skill["zip"]["path"]) as zf:
                self.assertIsNone(zf.testzip(), sid)
                names = zf.namelist()
            self.assertIn(f"{sid}/SKILL.md", names)
            for name in names:
                self.assertTrue(name.startswith(f"{sid}/"), name)
                self.assertNotIn("/extras/", "/" + name, name)
                self.assertFalse(name.endswith(".zip"), name)

    def test_rebuild_gives_identical_zips(self):
        for skill in self.manifest["skills"]:
            a = (self.out1 / skill["zip"]["path"]).read_bytes()
            b = (self.out2 / skill["zip"]["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(a).hexdigest(),
                             hashlib.sha256(b).hexdigest(), skill["id"])

    def test_manifest_files_exist(self):
        for skill in self.manifest["skills"]:
            for rel in files_in(skill["tree"]):
                self.assertTrue((self.out1 / "files" / rel).is_file(), rel)

    def test_zip_sizes_match_manifest(self):
        for skill in self.manifest["skills"]:
            size = (self.out1 / skill["zip"]["path"]).stat().st_size
            self.assertEqual(size, skill["zip"]["bytes"], skill["id"])

    def test_frontmatter_has_name_and_description(self):
        for skill in self.manifest["skills"]:
            self.assertTrue(skill["name"], skill["id"])
            self.assertTrue(skill["description"], skill["id"])

    def test_viewer_files_copied(self):
        self.assertTrue((self.out1 / "index.html").is_file())
        json.loads((self.out1 / "manifest.json").read_text(encoding="utf-8"))


class Fixtures(unittest.TestCase):
    """Small fake repos for the failure cases."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.out = Path(self.tmp.name) / "dist"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_inner_folder_without_skill_md_fails(self):
        self.write("demo/demo/references/a.md", "hi")
        with self.assertRaisesRegex(build.BuildError, "no SKILL.md"):
            build.build(self.root, self.out)

    def test_missing_description_fails(self):
        self.write("demo/demo/SKILL.md", "---\nname: demo\n---\nBody\n")
        with self.assertRaisesRegex(build.BuildError, "description"):
            build.build(self.root, self.out)

    def test_extras_and_top_level_files_stay_out_of_zip(self):
        self.write("demo/demo/SKILL.md",
                   "---\nname: demo\ndescription: Does a thing.\n---\n")
        self.write("demo/extras/tool.py", "print(1)")
        self.write("demo/README.md", "guide")
        manifest = build.build(self.root, self.out)
        with zipfile.ZipFile(self.out / "downloads/demo.zip") as zf:
            self.assertEqual(zf.namelist(), ["demo/", "demo/SKILL.md"])
        self.assertTrue((self.out / "files/demo/extras/tool.py").is_file())
        roles = {c["name"]: c.get("role")
                 for c in manifest["skills"][0]["tree"]["children"]}
        self.assertEqual(roles, {"demo": "skill", "extras": "extras",
                                 "README.md": None})

    def test_failed_build_does_not_block_the_next(self):
        self.write("demo/demo/SKILL.md", "---\nname: demo\ndescription: a: b\n---\n")
        with self.assertRaises(build.BuildError):
            build.build(self.root, self.out)
        self.write("demo/demo/SKILL.md", "---\nname: demo\ndescription: 'a: b'\n---\n")
        build.build(self.root, self.out)
        self.assertTrue((self.out / "downloads/demo.zip").is_file())

    def write_skill(self, site_json=None):
        self.write("demo/demo/SKILL.md",
                   "---\nname: demo\ndescription: Does a thing.\n---\n")
        if site_json is not None:
            self.write("demo/extras/site.json", site_json)

    def test_name_must_match_folder(self):
        self.write("demo/demo/SKILL.md", "---\nname: other\ndescription: x\n---\n")
        with self.assertRaisesRegex(build.BuildError, "must match its folder"):
            build.build(self.root, self.out)

    def test_site_json_tags_reach_manifest_in_facet_order(self):
        self.write_skill('{"task": ["review", "drafting"], "status": "pre-release"}')
        manifest = build.build(self.root, self.out)
        skill = manifest["skills"][0]
        self.assertEqual(skill["tags"], {"task": ["drafting", "review"]})
        self.assertEqual(skill["status"], "pre-release")
        self.assertIn("task", [f["id"] for f in manifest["facets"]])

    def test_no_site_json_means_no_tags(self):
        self.write_skill()
        self.assertEqual(build.build(self.root, self.out)["skills"][0]["tags"], {})

    def test_unknown_tag_value_fails(self):
        self.write_skill('{"task": ["juggling"]}')
        with self.assertRaisesRegex(build.BuildError, "'juggling' isn't a task value"):
            build.build(self.root, self.out)

    def test_unknown_site_json_key_fails(self):
        self.write_skill('{"audience": ["academic"]}')
        with self.assertRaisesRegex(build.BuildError, "unknown key 'audience'"):
            build.build(self.root, self.out)

    def test_bad_status_and_non_list_tags_fail(self):
        self.write_skill('{"status": "beta", "task": "review"}')
        with self.assertRaisesRegex(build.BuildError, "'status' must be.*'task' must be a list"):
            build.build(self.root, self.out)

    def test_invalid_site_json_fails(self):
        self.write_skill('{"task": [}')
        with self.assertRaisesRegex(build.BuildError, "isn't valid JSON"):
            build.build(self.root, self.out)

    def test_refuses_to_delete_unrelated_out_folder(self):
        self.write("demo/demo/SKILL.md",
                   "---\nname: demo\ndescription: x\n---\n")
        self.out.mkdir()
        (self.out / "keep.txt").write_text("mine")
        with self.assertRaisesRegex(build.BuildError, "not deleting"):
            build.build(self.root, self.out)


class Frontmatter(unittest.TestCase):

    def test_quoted_and_folded_values(self):
        fm = build.parse_frontmatter(
            '---\nname: x\ndescription: "Says \\"hi\\": twice"\n'
            'other: >\n  one\n  two\n---\n')
        self.assertEqual(fm["description"], 'Says "hi": twice')
        self.assertEqual(fm["other"], "one two")

    def test_no_frontmatter(self):
        self.assertIsNone(build.parse_frontmatter("# Title\n"))


class UploadRules(unittest.TestCase):
    """frontmatter_problems() mirrors what Claude.ai's upload rejects."""

    def problems(self, body):
        return build.frontmatter_problems(f"---\n{body}\n---\n# Skill\n")

    def test_valid_frontmatter_passes(self):
        self.assertEqual(self.problems(
            "name: my-skill\ndescription: 'Does this: a thing, \"well\".'\n"
            "license: MIT\nmetadata:\n  status: pre-release"), [])

    def test_unquoted_colon_space_fails(self):
        # The mistake update-dependencies had.
        found = self.problems("name: x\ndescription: Updates code safely: checks it.")
        self.assertEqual(len(found), 1)
        self.assertIn("line 3", found[0])
        self.assertIn("colon followed by a space", found[0])

    def test_colon_in_continuation_line_fails(self):
        found = self.problems("name: x\ndescription: Does a thing\n  and then: more.")
        self.assertIn("line 4", found[0])

    def test_colon_without_space_is_fine(self):
        self.assertEqual(self.problems("name: x\ndescription: See https://example.com."), [])

    def test_unknown_key_fails(self):
        found = self.problems("name: x\ndescription: y\nstatus: pre-release")
        self.assertIn("status", found[0])

    def test_name_rules(self):
        for name in ("My-Skill", "my_skill", "my--skill", "-skill", "claude-helper",
                     "x" * 65):
            self.assertTrue(self.problems(f"name: {name}\ndescription: y"), name)

    def test_description_rules(self):
        self.assertTrue(self.problems("name: x\ndescription: Uses <tags>."))
        self.assertTrue(self.problems(f"name: x\ndescription: {'a' * 1025}"))
        self.assertTrue(self.problems("name: x"))


class Viewer(unittest.TestCase):

    def test_cdn_scripts_are_pinned_with_sri(self):
        html = (build.SITE_DIR / "index.html").read_text(encoding="utf-8")
        scripts = re.findall(r"<script\b[^>]*>", html)
        remote = [s for s in scripts if "https://" in s]
        self.assertEqual(len(remote), 3)
        for tag in remote:
            self.assertIn("https://cdnjs.cloudflare.com/", tag)
            self.assertRegex(tag, r'integrity="sha(384|512)-[A-Za-z0-9+/=]+"')
            self.assertIn('crossorigin="anonymous"', tag)
            self.assertRegex(tag, r"/\d+\.\d+\.\d+/")  # exact version

    def test_facets_json_is_valid(self):
        facets = build.load_facets()
        self.assertIn("users", facets)
        for facet in facets.values():
            self.assertTrue(all(isinstance(v, str) and v for v in facet["values"].values()))

    def test_labels_json_is_valid(self):
        labels = json.loads((build.SITE_DIR / "labels.json").read_text(encoding="utf-8"))
        self.assertIn("SKILL.md", labels)


class ReadmeSummary(unittest.TestCase):

    def test_drops_links_pointers_and_status(self):
        summary, pre = build.summarize_row(
            "Does a thing. Pre-release. See its [README](x/README.md).")
        self.assertEqual(summary, "Does a thing.")
        self.assertTrue(pre)


if __name__ == "__main__":
    unittest.main()
