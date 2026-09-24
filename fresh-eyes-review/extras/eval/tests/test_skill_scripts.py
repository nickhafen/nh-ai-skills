"""Offline tests for the skill's own scripts: prepare.py, finalize.py, render_markdown.py.

Builds a working folder the way SKILL.md tells the model to (using mock-client output
for the model-written pieces), then checks that finalize assembles a valid results.json
and a report.

Run: python eval/tests/test_skill_scripts.py   (or with pytest)
"""

import json
import sys
import tempfile
import zipfile
from pathlib import Path

EXTRAS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(EXTRAS_DIR))
sys.path.insert(0, str(EXTRAS_DIR / "eval"))

from engine import pipeline  # noqa: E402  (puts skill scripts on the path)
from engine.model import MockClient  # noqa: E402
from harness import load_fixture  # noqa: E402
import finalize  # noqa: E402
import prepare  # noqa: E402

FIXTURE = EXTRAS_DIR / "eval" / "fixtures" / "smoke-demand-letter"


def build_working_folder(ai_answers=True):
    """Lay out the working files a skill run would write, from a mock pipeline run."""
    config = load_fixture(FIXTURE)
    results = pipeline.run(config, "B", MockClient(seed=3))
    workdir = Path(tempfile.mkdtemp(prefix="fer-test-"))
    prepare.main([str(FIXTURE / "document.md"), "--out", str(workdir)])
    setup = {
        "title": config["title"],
        "mode": "fast",
        "inputs": {"goal": config["goal"], "audience": None, "persona_overrides": [], "house_settings": None,
                   "background": config["background"]},
        "analysis": results["analysis"],
        "assumptions": config["assumptions"],
        "personas": [{"id": p["id"], "role": p["role"], "adaptations": p["adaptations"],
                      "added_context": p["added_context"], "background_ids": p["background_ids"]}
                     for p in results["personas"]],
    }
    (workdir / "setup.json").write_text(json.dumps(setup), encoding="utf-8")
    for review in results["persona_reviews"]:
        (workdir / "reviews" / f"{review['persona_id']}.json").write_text(
            json.dumps(dict(review["output"], persona_id=review["persona_id"])), encoding="utf-8")
    ai = results["ai_reader"]
    answers = [{"number": a["number"], "battery": a["battery"], "prompt": a["prompt"],
                "answer": a["answer"] if ai_answers else None} for a in ai["answers"]]
    (workdir / "ai-reader.json").write_text(json.dumps(
        {"method": "fresh_context" if ai_answers else "not_run", "recipient": ai["recipient"],
         "batteries": ai["batteries"], "answers": answers,
         "survival_check": ai["survival_check"] if ai_answers else None}), encoding="utf-8")
    (workdir / "synthesis.json").write_text(json.dumps(results["synthesis"]["output"]), encoding="utf-8")
    return workdir


def test_finalize_assembles_valid_results_and_report():
    workdir = build_working_folder()
    assert finalize.main([str(workdir), "--platform", "test", "--model", "mock"]) == 0
    results = json.loads((workdir / "results.json").read_text(encoding="utf-8"))
    assert results["run"]["execution"] == "single"
    # Persona text comes from the library, not from the model.
    assert all("## 1. Role and relationship to the author" in p["adapted_text"] for p in results["personas"])
    assert results["synthesis"]["priority_actions"]
    report = (workdir / "report.md").read_text(encoding="utf-8")
    for heading in ("## Priority actions", "## By reader", "## Next steps", "## About this run", "## Methodology"):
        assert heading in report, heading
    assert (workdir / "summary.md").exists()


def test_ai_reader_not_run_gives_copyable_prompts():
    workdir = build_working_folder(ai_answers=False)
    assert finalize.main([str(workdir), "--platform", "test", "--model", "mock"]) == 0
    report = (workdir / "report.md").read_text(encoding="utf-8")
    assert "open a **new** chat" in report
    assert "Summarize this in three sentences." in report


def test_finalize_reports_schema_problems():
    workdir = build_working_folder()
    review = next((workdir / "reviews").glob("*.json"))
    data = json.loads(review.read_text(encoding="utf-8"))
    data["findings"][0]["severity"] = "severe"  # not an allowed value
    review.write_text(json.dumps(data), encoding="utf-8")
    assert finalize.main([str(workdir)]) == 1


def test_custom_persona_from_working_folder():
    workdir = build_working_folder()
    template = (EXTRAS_DIR.parent / "fresh-eyes-review/references/personas/_template.md").read_text(encoding="utf-8")
    (workdir / "personas").mkdir()
    (workdir / "personas" / "hoa-board-member.md").write_text(
        template.replace("id: kebab-case-id", "id: hoa-board-member").replace("tier: A | B | C", "tier: C"),
        encoding="utf-8")
    setup = json.loads((workdir / "setup.json").read_text(encoding="utf-8"))
    setup["personas"].append({"id": "hoa-board-member", "role": "secondary", "adaptations": [],
                              "added_context": [], "background_ids": []})
    (workdir / "setup.json").write_text(json.dumps(setup), encoding="utf-8")
    assert finalize.main([str(workdir), "--platform", "test"]) == 0


def test_html_report_embeds_results_safely():
    import render_report
    workdir = build_working_folder()
    assert finalize.main([str(workdir), "--platform", "test"]) == 0
    html = (workdir / "report.html").read_text(encoding="utf-8")
    assert "/*RESULTS_JSON*/" not in html
    results = json.loads((workdir / "results.json").read_text(encoding="utf-8"))
    results["document"]["text"] += "\n</script><script>alert(1)</script>"
    html = render_report.render_html(results)
    data = html.split('id="results-data">', 1)[1].split("</script>", 1)[0]
    assert json.loads(data)["document"]["text"].endswith("</script><script>alert(1)</script>")
    viewer = render_report.render_html(None)
    assert 'id="results-data">null</script>' in viewer


def test_prepare_reads_docx():
    workdir = Path(tempfile.mkdtemp(prefix="fer-docx-"))
    docx = workdir / "letter.docx"
    body = ('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
            '<w:p><w:r><w:t>First paragraph of the letter.</w:t></w:r></w:p>'
            '<w:p><w:r><w:t xml:space="preserve">Second </w:t></w:r><w:r><w:t>paragraph.</w:t></w:r></w:p>'
            '</w:body></w:document>')
    with zipfile.ZipFile(docx, "w") as z:
        z.writestr("word/document.xml", body)
    prepare.main([str(docx), "--out", str(workdir / "work")])
    text = (workdir / "work" / "document.md").read_text(encoding="utf-8")
    assert text == "First paragraph of the letter.\n\nSecond paragraph.\n"


if __name__ == "__main__":
    import contextlib
    import io
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for test in tests:
        with contextlib.redirect_stdout(io.StringIO()):
            test()
        print(f"ok  {test.__name__}")
    print(f"\n{len(tests)} tests passed")
