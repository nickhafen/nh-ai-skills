"""Tests for scripts/compute_deadline.py.  Run from the skill folder:  python -m pytest tests"""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import compute_deadline as cd  # noqa: E402


def answer(service, method="personal"):
    return cd.compute(date.fromisoformat(service), method)


# --- Service on Nov 20, 2026: the period crosses Thanksgiving -----------------

def test_nov_20_2026_period_crosses_thanksgiving():
    r = answer("2026-11-20")
    # 21 calendar days; Thanksgiving (Nov 26) is counted, not skipped (URCP 6(a)(1)(B)).
    assert r["answer_deadline"] == "2026-12-11"
    assert r["signing_deadline"] == "2026-12-04"
    assert r["holidays_skipped"] == []
    assert any("Thanksgiving Day (2026-11-26)" in a for a in r["assumptions"])


def test_nov_20_2026_out_of_state_lands_on_sunday():
    r = answer("2026-11-20", "out-of-state")
    assert r["period_days"] == 30
    assert r["answer_deadline"] == "2026-12-21"  # Dec 20 is a Sunday


# --- Deadline lands on a Saturday ---------------------------------------------

def test_saturday_rolls_to_monday():
    r = answer("2026-10-03")  # + 21 = Sat Oct 24
    assert r["answer_deadline"] == "2026-10-26"
    assert any("rolled forward" in rule for rule in r["rules_applied"])


# --- Deadline lands on a Monday holiday ----------------------------------------

def test_monday_holiday_rolls_to_tuesday():
    r = answer("2026-08-17")  # + 21 = Mon Sep 7, Labor Day
    assert r["answer_deadline"] == "2026-09-08"
    assert [h["name"] for h in r["holidays_skipped"]] == ["Labor Day"]


def test_saturday_before_monday_holiday_rolls_to_tuesday():
    r = answer("2026-08-15")  # + 21 = Sat Sep 5; Sun, then Labor Day
    assert r["answer_deadline"] == "2026-09-08"


def test_good_friday_2027_is_flagged_for_verification():
    r = answer("2027-03-05")  # + 21 = Fri Mar 26, Good Friday
    assert r["answer_deadline"] == "2027-03-29"
    assert any(a.startswith("VERIFY") and "Good Friday" in a for a in r["assumptions"])


# --- Signing deadline rolls back ----------------------------------------------

def test_roll_back_from_weekend_to_friday():
    # Answer deadline minus 7 keeps the weekday, so a weekend landing only happens
    # if an instructor changes SIGNING_BUFFER_DAYS; test the helper directly.
    skipped = []
    assert cd.roll_back(date(2026, 12, 12), skipped) == date(2026, 12, 11)  # Sat -> Fri
    assert cd.roll_back(date(2026, 12, 13), skipped) == date(2026, 12, 11)  # Sun -> Fri


def test_roll_back_across_weekend_and_holiday():
    # Sun Jul 5 -> Sat Jul 4 -> Fri Jul 3 (Independence Day observed) -> Thu Jul 2
    skipped = []
    assert cd.roll_back(date(2026, 7, 5), skipped) == date(2026, 7, 2)
    assert skipped[0]["name"] == "Independence Day (observed)"


def test_signing_deadline_rolls_back_from_thanksgiving():
    r = answer("2026-11-12")  # answer Thu Dec 3; minus 7 = Thanksgiving
    assert r["answer_deadline"] == "2026-12-03"
    assert r["signing_deadline"] == "2026-11-25"
    assert r["holidays_skipped"][0]["direction"] == "signing deadline rolled back"


def test_signing_deadline_with_non_weekday_buffer(monkeypatch):
    monkeypatch.setattr(cd, "SIGNING_BUFFER_DAYS", 5)
    r = answer("2026-11-20")  # answer Fri Dec 11; minus 5 = Sun Dec 6
    assert r["signing_deadline"] == "2026-12-04"


# --- Each service method -------------------------------------------------------

@pytest.mark.parametrize("method, days, due", [
    ("personal", 21, "2026-12-11"),
    ("mail", 21, "2026-12-11"),       # URCP 6(c) +7 does not apply to Rule 4 service
    ("email", 21, "2026-12-11"),
    ("out-of-state", 30, "2026-12-21"),
])
def test_each_service_method(method, days, due):
    r = answer("2026-11-20", method)
    assert r["period_days"] == days
    assert r["answer_deadline"] == due
    assert r["service_method"] == method


def test_unknown_method_rejected():
    with pytest.raises(ValueError):
        answer("2026-11-20", "carrier-pigeon")


def test_year_outside_holiday_table_warns():
    r = answer("2028-03-01")
    assert any(a.startswith("WARNING") for a in r["assumptions"])


# --- CLI ------------------------------------------------------------------------

def test_cli_outputs_required_json_keys():
    out = subprocess.run(
        [sys.executable, str(SCRIPTS / "compute_deadline.py"), "--service-date", "2026-11-20",
         "--service-method", "mail", "--event", "answer"],
        capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    for key in ("answer_deadline", "signing_deadline", "period_days",
                "rules_applied", "assumptions", "holidays_skipped"):
        assert key in data
