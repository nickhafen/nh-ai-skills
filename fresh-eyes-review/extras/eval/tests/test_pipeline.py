"""Offline tests for the pipeline, quality scripts, and scoring. No API calls.

Run: python eval/tests/test_pipeline.py   (or with pytest)
"""

import sys
from pathlib import Path

EXTRAS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(EXTRAS_DIR))
sys.path.insert(0, str(EXTRAS_DIR / "eval"))

from engine import pipeline  # noqa: E402
from engine.model import MockClient  # noqa: E402
from harness import load_fixture  # noqa: E402
import quality  # noqa: E402
import score  # noqa: E402
from validate_results import validate  # noqa: E402

FIXTURE = EXTRAS_DIR / "eval" / "fixtures" / "smoke-demand-letter"
PRIVILEGED = "boxwood"


def _run(condition):
    config = load_fixture(FIXTURE)
    return pipeline.run(config, condition, MockClient(seed=1))


def _persona_prompts(results, persona_id):
    return [p for p in results["prompts"] if p["stage"] == "persona_review" and p["persona_id"] == persona_id]


def test_condition_c_routes_background_by_tier():
    results = _run("C")
    tiers = {p["id"]: p["background_ids"] for p in results["personas"]}
    assert tiers["opposing-party-unrepresented"] == ["bg3"]           # tier C: public only
    assert tiers["client-business-decision-maker"] == ["bg2", "bg3"]  # tier B: client-known + public
    assert tiers["senior-colleague"] == ["bg1", "bg2", "bg3", "bg4"]  # tier A: everything
    for prompt in _persona_prompts(results, "opposing-party-unrepresented"):
        text = " ".join(m["content"] for m in prompt["messages"]).lower()
        assert PRIVILEGED not in text, "privileged background leaked into a tier-C prompt"
        assert "payment plan" not in text, "unlabeled background must be treated as privileged"
    # The author's goal goes only to tier A.
    c_text = " ".join(m["content"] for m in _persona_prompts(results, "opposing-party-unrepresented")[0]["messages"])
    assert "<author_goal>" not in c_text


def test_condition_d_gives_everyone_full_background():
    results = _run("D")
    prompt = _persona_prompts(results, "opposing-party-unrepresented")[0]
    assert PRIVILEGED in " ".join(m["content"] for m in prompt["messages"]).lower()


def test_condition_b_restricts_in_single_context():
    results = _run("B")
    prompt = _persona_prompts(results, "opposing-party-unrepresented")[0]
    last = prompt["messages"][-1]["content"]
    assert "<not_known_to_this_reader>" in last and PRIVILEGED in last.lower()
    # Single context: later personas see earlier turns.
    later = _persona_prompts(results, "senior-colleague")[0]
    assert any(m["role"] == "assistant" for m in later["messages"])


def test_condition_a_has_no_restrictions():
    results = _run("A")
    for prompt in (p for p in results["prompts"] if p["stage"] == "persona_review"):
        assert "<not_known_to_this_reader>" not in " ".join(m["content"] for m in prompt["messages"])


def test_every_condition_produces_valid_results():
    for condition in pipeline.CONDITIONS:
        results = _run(condition)
        assert validate(results) == [], condition
        assert "[[DOCUMENT]]" in results["prompts"][0]["messages"][0]["content"]


def test_quote_matching_tolerates_typography_and_ellipses():
    doc = "Greenline acknowledges that its crew may have cut the hedges shorter than you asked."
    assert quality.quote_in_document("“Greenline acknowledges” that its crew", doc)
    assert quality.quote_in_document("Greenline acknowledges ... than you asked", doc)
    assert not quality.quote_in_document("Greenline denies everything", doc)


def test_sections_split_by_paragraph():
    sections = quality.split_sections("First paragraph here.\n\nSecond paragraph here.")
    assert [s["id"] for s in sections] == ["p1", "p2"]


def test_answer_key_matching_modes():
    issue = {"anchor": "subject to the Section 4 cap", "keywords": ["section 4"], "match": "anchor+keywords"}
    assert score.matches(issue, "The reader won't know what Section 4 means", "subject to the Section 4 cap")
    assert not score.matches(issue, "Tone is harsh", "subject to the Section 4 cap")


def test_leakage_detected_for_tier_c():
    results = _run("C")
    key = {"issues": [{"id": "l1", "type": "leakage-probe", "anchor": None, "keywords": ["boxwood"],
                       "match": "keywords", "expected_personas": []}]}
    results["persona_reviews"][0]["output"]["gut_reaction"] = "They killed my boxwood shrubs."
    s = score.score_run(results, key)
    assert s["leaked_personas"] == [results["persona_reviews"][0]["persona_id"]]


def test_ranking_follows_rubric_weights():
    results = _run("C")
    results["synthesis"]["output"]["issues"] = [
        {"title": "low", "quote": "Sincerely,", "summary": "", "finding_refs": [], "reasons": [],
         "severity": "low", "category": "finding", "depends_on_assumptions": [], "fix_direction": ""},
        {"title": "high", "quote": "Dear Mr. Okafor:", "summary": "", "finding_refs": [],
         "reasons": [{"reader": "opposing-party-unrepresented", "reason": ""},
                     {"reader": "senior-colleague", "reason": ""}],
         "severity": "high", "category": "main_point_mismatch", "depends_on_assumptions": [], "fix_direction": ""},
    ]
    ranked, priority, _ = quality.rank_issues(results)
    assert priority[0] == 1
    top = ranked[0]
    assert top["convergent"] and top["primary"] and top["score"] == 3 * 3 + 2 * 2 + 2 + 3


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for test in tests:
        test()
        print(f"ok  {test.__name__}")
    print(f"\n{len(tests)} tests passed")
