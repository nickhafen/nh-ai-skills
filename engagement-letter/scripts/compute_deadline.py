#!/usr/bin/env python3
"""Compute a Utah answer deadline and a client signing deadline.

Standard library only. Instructors: every legal assumption lives in the
CONSTANTS section below -- edit there, not in the logic.

Usage:
    python compute_deadline.py --service-date 2026-11-20 --service-method personal --event answer

Rules implemented (see references/urcp-deadlines.md for the verified text):
  * URCP 12(a)(1): answer due 21 days after in-state service, 30 days after
    out-of-state service of the summons and complaint.
  * URCP 6(a)(1): exclude the trigger day, count every day, and if the last day
    is a Saturday, Sunday, or legal holiday, run to the next day that is not.
  * URCP 6(c) adds 7 days ONLY for papers served by mail under Rule 5(b)(3)(C)(i).
    A summons and complaint is served under Rule 4, so no days are added for the
    answer. The constant ADDED_DAYS_BY_METHOD keeps that visible and editable.
"""

import argparse
import json
import sys
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# CONSTANTS -- edit these
# ---------------------------------------------------------------------------

RULES_LAST_VERIFIED = "2026-09-22"

# URCP 12(a)(1): days to answer, by where the summons and complaint were served.
ANSWER_PERIOD_IN_STATE_DAYS = 21
ANSWER_PERIOD_OUT_OF_STATE_DAYS = 30

# Days added for the method of service. All zero for an answer: URCP 6(c)
# applies only to service by mail under Rule 5(b)(3)(C)(i), not Rule 4 process.
ADDED_DAYS_BY_METHOD = {
    "personal": 0,
    "mail": 0,
    "email": 0,
    "out-of-state": 0,
}

# Firm policy: client must sign this many calendar days before the answer is due.
SIGNING_BUFFER_DAYS = 7

# Utah legal holidays (Utah Code 63G-1-301, as observed; URCP 6(a)(6)).
# Sundays are always non-business days, so Sunday holidays are not listed.
UTAH_LEGAL_HOLIDAYS = {
    # 2026 (statute version effective 5/6/2026)
    date(2026, 1, 1): "New Year's Day",
    date(2026, 1, 19): "Dr. Martin Luther King, Jr. Day",
    date(2026, 2, 16): "Presidents' Day (Washington and Lincoln Day)",
    # Good Friday (Apr 3, 2026) predates the 5/6/2026 amendment -- not listed.
    date(2026, 5, 25): "Memorial Day",
    date(2026, 6, 15): "Juneteenth National Freedom Day (observed)",
    date(2026, 7, 3): "Independence Day (observed)",
    date(2026, 7, 24): "Pioneer Day",
    date(2026, 9, 7): "Labor Day",
    date(2026, 10, 12): "Columbus Day",
    date(2026, 11, 11): "Veterans Day",
    date(2026, 11, 26): "Thanksgiving Day",
    date(2026, 12, 25): "Christmas Day",
    # 2027 (statute version effective 1/1/2027)
    date(2027, 1, 1): "New Year's Day",
    date(2027, 1, 18): "Dr. Martin Luther King, Jr. Day",
    date(2027, 2, 15): "Presidents' Day (Washington and Lincoln Day)",
    date(2027, 3, 26): "Good Friday",
    date(2027, 5, 31): "Memorial Day",
    date(2027, 6, 18): "Juneteenth National Freedom Day (observed)",
    date(2027, 7, 5): "Independence Day (observed)",
    date(2027, 7, 23): "Pioneer Day (observed)",
    date(2027, 9, 6): "Labor Day",
    date(2027, 10, 11): "Columbus Day",
    date(2027, 11, 11): "Veterans Day",
    date(2027, 11, 25): "Thanksgiving Day",
    date(2027, 12, 24): "Christmas Day (observed)",
    date(2027, 12, 31): "New Year's Day 2028 (observed)",
}

# Holidays whose treatment by the courts should be double-checked
# (recent statutory changes; URCP 6(a)(6) text lags the statute).
HOLIDAYS_TO_VERIFY = {"Good Friday", "Juneteenth National Freedom Day (observed)"}

HOLIDAY_YEARS_COVERED = {d.year for d in UTAH_LEGAL_HOLIDAYS}

METHOD_NOTES = {
    "personal": "Personal (in-state) delivery under URCP 4(d)(1); service date is the date of delivery.",
    "mail": "Mail or courier under URCP 4(d)(2); service is complete on the date the receipt is "
            "signed (4(d)(2)(C)), so the service date entered must be the signature date. "
            "URCP 6(c)'s 7 added days do not apply to a summons and complaint.",
    "email": "Electronic acceptance of service under URCP 4(d)(3) (or court-ordered service under 4(d)(5)); "
             "service is effective on the acceptance date. No days are added for email.",
    "out-of-state": "Service outside Utah; URCP 12(a)(1) gives 30 days instead of 21.",
}

# ---------------------------------------------------------------------------
# Logic
# ---------------------------------------------------------------------------


def is_business_day(d):
    """True if d is not a Saturday, Sunday, or Utah legal holiday."""
    return d.weekday() < 5 and d not in UTAH_LEGAL_HOLIDAYS


def roll_forward(d, skipped):
    """URCP 6(a)(1)(C): move to the next day that is not a weekend or holiday."""
    while not is_business_day(d):
        if d in UTAH_LEGAL_HOLIDAYS:
            skipped.append({"date": d.isoformat(), "name": UTAH_LEGAL_HOLIDAYS[d],
                            "direction": "answer deadline rolled forward"})
        d += timedelta(days=1)
    return d


def roll_back(d, skipped):
    """Move to the prior day that is not a weekend or holiday (counting backward, cf. URCP 6(a)(5))."""
    while not is_business_day(d):
        if d in UTAH_LEGAL_HOLIDAYS:
            skipped.append({"date": d.isoformat(), "name": UTAH_LEGAL_HOLIDAYS[d],
                            "direction": "signing deadline rolled back"})
        d -= timedelta(days=1)
    return d


def compute(service_date, service_method, event="answer"):
    if event != "answer":
        raise ValueError("Only --event answer is supported.")
    if service_method not in ADDED_DAYS_BY_METHOD:
        raise ValueError(f"Unknown service method: {service_method}")

    base = (ANSWER_PERIOD_OUT_OF_STATE_DAYS if service_method == "out-of-state"
            else ANSWER_PERIOD_IN_STATE_DAYS)
    period_days = base + ADDED_DAYS_BY_METHOD[service_method]

    skipped = []
    last_day = service_date + timedelta(days=period_days)  # day of service excluded
    answer = roll_forward(last_day, skipped)
    signing = roll_back(answer - timedelta(days=SIGNING_BUFFER_DAYS), skipped)

    rules = [
        f"URCP 12(a)(1): answer due {base} days after service "
        f"{'outside' if service_method == 'out-of-state' else 'within'} the state.",
        "URCP 6(a)(1)(A): day of service excluded.",
        "URCP 6(a)(1)(B): every day counted, including intermediate weekends and holidays.",
    ]
    if answer != last_day:
        rules.append(f"URCP 6(a)(1)(C): day {period_days} ({last_day.isoformat()}, "
                     f"{last_day:%A}) was not a business day; rolled forward to {answer.isoformat()}.")
    else:
        rules.append("URCP 6(a)(1)(C): last day is a business day; no roll-forward needed.")
    rules.append("URCP 6(c) not applied: it adds 7 days only for papers served by mail "
                 "under Rule 5(b)(3)(C)(i), not for service of a summons under Rule 4.")

    assumptions = [
        METHOD_NOTES[service_method],
        "Deadline is for an answer to the original complaint; a Rule 12(b) motion, a court order, "
        "or a statute providing otherwise would change it.",
        f"Signing deadline is firm policy, not a court rule: answer deadline minus "
        f"{SIGNING_BUFFER_DAYS} calendar days, rolled back to the prior business day.",
        f"Utah legal holidays applied from Utah Code 63G-1-301 (rules last verified {RULES_LAST_VERIFIED}). "
        "Governor-declared holidays and clerk's-office closures (URCP 6(a)(3)) are not included.",
    ]
    between = [f"{UTAH_LEGAL_HOLIDAYS[d]} ({d.isoformat()})" for d in sorted(UTAH_LEGAL_HOLIDAYS)
               if service_date < d < last_day]
    if between:
        assumptions.append("Holidays inside the period were counted as ordinary days per "
                           "URCP 6(a)(1)(B): " + "; ".join(between) + ".")
    for d in (service_date, last_day, answer):
        if d.year not in HOLIDAY_YEARS_COVERED:
            assumptions.append(f"WARNING: no holiday table for {d.year}; only weekends were "
                               "considered for that year. Add holidays to UTAH_LEGAL_HOLIDAYS.")
            break
    for h in skipped:
        if h["name"] in HOLIDAYS_TO_VERIFY:
            assumptions.append(f"VERIFY: a deadline moved because of {h['name']} ({h['date']}); "
                               "confirm the court treats this day as a legal holiday.")
    assumptions.append("A lawyer must verify all dates before relying on them.")

    return {
        "answer_deadline": answer.isoformat(),
        "signing_deadline": signing.isoformat(),
        "period_days": period_days,
        "rules_applied": rules,
        "assumptions": assumptions,
        "holidays_skipped": skipped,
        "service_date": service_date.isoformat(),
        "service_method": service_method,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--service-date", required=True, help="YYYY-MM-DD")
    p.add_argument("--service-method", required=True, choices=sorted(ADDED_DAYS_BY_METHOD))
    p.add_argument("--event", default="answer", choices=["answer"])
    args = p.parse_args(argv)
    try:
        served = date.fromisoformat(args.service_date)
    except ValueError:
        p.error("--service-date must be YYYY-MM-DD")
    json.dump(compute(served, args.service_method, args.event), sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
