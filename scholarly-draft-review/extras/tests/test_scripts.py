"""Offline tests for the skill's scripts: prepare, quality, finalize, and the renderers.

Uses the example working folder (written the way SKILL.md tells the model to) as the
base case and varies it. No model calls.

Run from extras/: python tests/test_scripts.py   (or with pytest)
"""

import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

EXTRAS_DIR = Path(__file__).resolve().parents[1]
SKILL_DIR = EXTRAS_DIR.parent / "scholarly-draft-review"
EXAMPLE = EXTRAS_DIR / "examples" / "workshop-article"
sys.path.insert(0, str(SKILL_DIR / "scripts"))
sys.path.insert(0, str(EXTRAS_DIR / "build"))

import build_schema  # noqa: E402
import finalize  # noqa: E402
import prepare  # noqa: E402
import quality  # noqa: E402
import render_report  # noqa: E402

WORKING_FILES = ["document.md", "source.json", "setup.json", "related-work.json", "key-sentences.json",
                 "synthesis.json"]


def working_folder():
    """A fresh copy of the example working files (no outputs)."""
    workdir = Path(tempfile.mkdtemp(prefix="sdr-test-"))
    for name in WORKING_FILES:
        shutil.copy(EXAMPLE / name, workdir / name)
    shutil.copytree(EXAMPLE / "reviews", workdir / "reviews")
    return workdir


def edit_json(path, change):
    data = json.loads(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(json.dumps(data), encoding="utf-8")


def load_results(workdir):
    return json.loads((workdir / "results.json").read_text(encoding="utf-8"))


def test_finalize_assembles_valid_results_and_report():
    workdir = working_folder()
    assert finalize.main([str(workdir), "--platform", "test", "--model", "mock"]) == 0
    results = load_results(workdir)
    assert all("## 1. Role and relationship to the author" in p["adapted_text"] for p in results["personas"])
    assert not results["quality"]["anchoring"]["unverified"], results["quality"]["anchoring"]["unverified"]
    synthesis = results["synthesis"]
    issues = synthesis["output"]["issues"]
    assert synthesis["priority_actions"] and all(issues[i]["timing"] == "now" for i in synthesis["priority_actions"])
    assert synthesis["parked"] and all(issues[i]["timing"] == "later" for i in synthesis["parked"])
    assert results["document"]["key_sentences"][0]["text"].startswith("On a cold night")
    report = (workdir / "report.md").read_text(encoding="utf-8")
    assert "<summary><strong>Before you rely on this</strong></summary>" in report
    for heading in ("## Priority actions", "## What's working", "## By reader", "## Key-sentence outline", "## Method"):
        assert heading in report, heading
    for cut in ("## For a later draft", "## Tradeoffs", "## Who to ask next", "## Related work to check"):
        assert cut not in report, cut
    # Every issue, now or later, appears once in one numbered list, priority actions first.
    priorities = report[report.index("## Priority actions"):report.index("## What's working")]
    numbered = re.findall(r"^### (\d+)\. (.+)$", priorities, re.M)
    assert [int(n) for n, _ in numbered] == list(range(1, len(issues) + 1))
    first = [issues[i]["title"] for i in synthesis["priority_actions"]]
    assert [t for _, t in numbered[:len(first)]] == first
    assert (workdir / "summary.md").exists()


def test_results_and_reports_refer_to_the_draft_by_filename():
    workdir = working_folder()
    assert finalize.main([str(workdir), "--platform", "test"]) == 0
    results = load_results(workdir)
    assert "text" not in results["document"] and results["document"]["source_file"] == "document.md"
    unquoted = "Nothing was taken, and the family assumed a glitch."  # in the draft, but not quoted by any reader
    for name in ("results.json", "report.md", "report.html", "summary.md"):
        assert unquoted not in (workdir / name).read_text(encoding="utf-8"), name
    assert "**Draft:** document.md (1499 words" in (workdir / "report.md").read_text(encoding="utf-8")


def test_limitations_are_disclosed_in_summary_and_report():
    workdir = working_folder()
    edit_json(workdir / "setup.json", lambda d: d["analysis"]["claim"].update(source="inferred"))
    assert finalize.main([str(workdir), "--platform", "test"]) == 0
    summary = (workdir / "summary.md").read_text(encoding="utf-8")
    report = (workdir / "report.md").read_text(encoding="utf-8")
    assert "**Before you rely on this**" in summary
    assert report.index("Before you rely on this") < report.index("## Priority actions")
    for title, text in quality.STANDING_LIMITATIONS:
        assert f"**{title}.** {text}" in summary and f"**{title}.** {text}" in report, title
    assert "**Your claim was inferred.**" in summary
    assert summary.index("Before you rely on this") < summary.index("Full report:")


def test_standing_limitations_match_the_rubric():
    rubric = (SKILL_DIR / "references" / "synthesis-rubric.md").read_text(encoding="utf-8")
    for title, text in quality.STANDING_LIMITATIONS:
        assert f"- **{title}.** {text}" in rubric, title


def test_named_works_default_to_not_checked_and_never_to_verified():
    workdir = working_folder()
    (workdir / "related-work.json").unlink()
    edit_json(workdir / "reviews" / "skeptical-expert.json", lambda d: d["related_work"].append(
        {"work": "A. Author, Some Article, 1 J. Test 1 (2020)", "specific": True, "why": "Closest work.",
         "confidence": "low"}))
    assert finalize.main([str(workdir), "--platform", "test"]) == 0
    results = load_results(workdir)
    items = {i["ref"]: i for i in results["related_work_check"]["items"]}
    assert set(items) == {"field-expert/rw1", "skeptical-expert/rw2"}
    assert all(i["status"] == "not_checked" for i in items.values())
    assert results["quality"]["related_work"] == {"specific": 2, "verified": 0, "cited_in_draft": 0,
                                                  "not_found": 0, "not_checked": 2}
    report = (workdir / "report.md").read_text(encoding="utf-8")
    assert "Not checked: confirm it exists before relying on it" in report
    assert "**2 named works not checked.**" in (workdir / "summary.md").read_text(encoding="utf-8")


def test_works_not_found_are_left_out_and_links_need_http():
    workdir = working_folder()
    edit_json(workdir / "reviews" / "skeptical-expert.json", lambda d: d["related_work"].extend([
        {"work": "Real Work", "specific": True, "why": "Close.", "confidence": "high"},
        {"work": "Made-Up Work", "specific": True, "why": "Close.", "confidence": "high"}]))
    edit_json(workdir / "related-work.json", lambda d: d.update(method="searched", items=d["items"] + [
        {"ref": "skeptical-expert/rw2", "work": "Real Work", "status": "verified", "url": "https://example.org/real",
         "note": "Found."},
        {"ref": "skeptical-expert/rw3", "work": "Made-Up Work", "status": "not_found", "url": None,
         "note": "No match."}]))
    assert finalize.main([str(workdir), "--platform", "test"]) == 0
    report = (workdir / "report.md").read_text(encoding="utf-8")
    assert "[Real Work](https://example.org/real)" in report
    assert "Made-Up Work" not in report.split("## Method")[0]
    assert "1 not found and left out" in report
    html = (workdir / "report.html").read_text(encoding="utf-8")
    assert r"/^https?:\/\//i.test" in html  # only http(s) URLs become links


def test_missing_related_work_field_is_tolerated():
    workdir = working_folder()
    edit_json(workdir / "reviews" / "generalist-law-colleague.json", lambda d: d.pop("related_work"))
    assert finalize.main([str(workdir), "--platform", "test"]) == 0


def test_finalize_reports_schema_problems():
    workdir = working_folder()
    edit_json(workdir / "reviews" / "field-expert.json", lambda d: d["findings"][0].update(severity="severe"))
    assert finalize.main([str(workdir)]) == 1
    edit_json(workdir / "reviews" / "field-expert.json", lambda d: d["findings"][0].update(severity="high"))
    edit_json(workdir / "synthesis.json", lambda d: d["issues"][0].update(timing="soon"))
    assert finalize.main([str(workdir)]) == 1


def test_custom_persona_from_working_folder():
    workdir = working_folder()
    template = (SKILL_DIR / "references/personas/_template.md").read_text(encoding="utf-8")
    (workdir / "personas").mkdir()
    (workdir / "personas" / "tenure-letter-writer.md").write_text(
        template.replace("id: kebab-case-id", "id: tenure-letter-writer"), encoding="utf-8")
    edit_json(workdir / "setup.json", lambda d: d["personas"].append(
        {"id": "tenure-letter-writer", "adaptations": [], "added_context": []}))
    assert finalize.main([str(workdir), "--platform", "test"]) == 0
    custom = next(p for p in load_results(workdir)["personas"] if p["id"] == "tenure-letter-writer")
    assert custom["reader_type"] == "custom" and custom["briefing"] in ("briefed", "cold")


def test_html_report_embeds_results_safely():
    workdir = working_folder()
    assert finalize.main([str(workdir), "--platform", "test"]) == 0
    html = (workdir / "report.html").read_text(encoding="utf-8")
    assert "/*RESULTS_JSON*/" not in html
    results = load_results(workdir)
    results["document"]["title"] += "</script><script>alert(1)</script>"
    html = render_report.render_html(results)
    data = html.split('id="results-data">', 1)[1].split("</script>", 1)[0]
    assert json.loads(data)["document"]["title"].endswith("</script><script>alert(1)</script>")
    assert 'id="results-data">null</script>' in render_report.render_html(None)


def test_prepare_reads_docx_headings_and_footnotes():
    workdir = Path(tempfile.mkdtemp(prefix="sdr-docx-"))
    w = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
    body = (f'<w:document {w}><w:body>'
            '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Introduction</w:t></w:r></w:p>'
            '<w:p><w:r><w:t xml:space="preserve">Courts disagree about this. </w:t></w:r>'
            '<w:r><w:footnoteReference w:id="7"/></w:r><w:r><w:t>More text.</w:t></w:r></w:p>'
            '</w:body></w:document>')
    notes = (f'<w:footnotes {w}><w:footnote w:id="0"><w:p><w:r><w:t>separator</w:t></w:r></w:p></w:footnote>'
             '<w:footnote w:id="7"><w:p><w:r><w:t>See the cited case.</w:t></w:r></w:p></w:footnote></w:footnotes>')
    with zipfile.ZipFile(workdir / "draft.docx", "w") as z:
        z.writestr("word/document.xml", body)
        z.writestr("word/footnotes.xml", notes)
    prepare.main([str(workdir / "draft.docx"), "--out", str(workdir / "work")])
    text = (workdir / "work" / "document.md").read_text(encoding="utf-8")
    assert text == ("# Introduction\n\nCourts disagree about this. [^1]More text.\n\n"
                    "## Footnotes\n\n[^1]: See the cited case.\n")
    assert (workdir / "work" / "key-sentences.md").exists()


def test_key_sentences_skip_front_matter_headings_lists_and_footnotes():
    text = ("# A TITLE FOR THE ARTICLE\n\nProfessor of Law at a school, with thanks to many workshop "
            "participants for their comments.\n\n## Introduction\n\n"
            "In Hollis v. Brandt Mfg. Co., 412 F.4th 88 (12th Cir. 2022), the court got it wrong on the facts. "
            "Then more.\n\n- a bullet point that is long enough to count as a paragraph if it were prose text\n\n"
            "## I. The Problem\n\nThe rule assumes the product is fixed at sale, and software breaks that. "
            "Next sentence.\n\n## Footnotes\n\n[^1]: A footnote long enough to be a paragraph if it were counted "
            "as one by mistake.\n")
    outline = quality.key_sentences(text)
    assert [k["text"] for k in outline] == [
        "In Hollis v. Brandt Mfg. Co., 412 F.4th 88 (12th Cir. 2022), the court got it wrong on the facts.",
        "The rule assumes the product is fixed at sale, and software breaks that."]


def test_sections_group_long_drafts_without_headings():
    text = "\n\n".join(f"Paragraph {i} says something about the argument here." for i in range(1, 81))
    sections = quality.split_sections(text)
    assert len(sections) <= quality.MAX_PARAGRAPH_SECTIONS and sections[0]["label"].startswith("¶1–4")


def test_quote_matching_ignores_footnote_marks_and_typography():
    doc = "The rule is simple.[^3] It “works” — mostly."
    assert quality.quote_in_document('The rule is simple. It "works" - mostly.', doc)
    assert not quality.quote_in_document("The rule is complicated.", doc)


def test_schema_file_is_up_to_date():
    assert build_schema.main(["--check"]) == 0


if __name__ == "__main__":
    import contextlib
    import io
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for test in tests:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            test()
        print(f"ok  {test.__name__}")
    print(f"\n{len(tests)} tests passed")
