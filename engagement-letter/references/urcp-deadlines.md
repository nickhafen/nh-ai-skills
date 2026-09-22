# Utah Answer Deadlines: Rules Summary

**Last verified:** September 22, 2026, against the rule text on utcourts.gov
(URCP 4, 5, 6, and 12) and le.utah.gov (Utah Code 63G-1-301).
**Read this file only for litigation matters.**

`scripts/compute_deadline.py` does the actual date math. This file tells you
what the script does and why, so you can explain the result to the lawyer.

## 1. Time to answer: URCP 12(a)(1) (effective 5/1/2024)

- A defendant must file and serve an answer **within 21 days** after service of
  the summons and complaint **within the state**.
- The period is **30 days** if the summons and complaint are served
  **outside the state**.
- These periods apply "unless otherwise provided by statute or order of the
  court." A Rule 12(b) motion also changes the timing. Under 12(a)(1)(A), if
  the motion is denied, the responsive pleading is due 14 days after notice of
  the court's action.

## 2. Counting days: URCP 6(a)(1) (effective 5/1/2024)

When a period is stated in days:

- **(A)** Exclude the day of the triggering event (the day of service).
- **(B)** Count every day, **including intermediate Saturdays, Sundays, and
  legal holidays**.
- **(C)** Include the last day. If the last day is a Saturday, Sunday, or legal
  holiday, the period runs to the end of the next day that is not.

Related provisions:

- **6(a)(3):** If the clerk's office is inaccessible on the last day, the time
  extends to the next accessible business day. The script does not model this.
- **6(a)(4):** An electronic filing is due before midnight. Other filings are
  due before the clerk's office closes.
- **6(a)(5):** The "next day" is found by counting forward for periods measured
  after an event and backward for periods measured before one. The script uses
  the backward count for the firm's signing deadline.
- **6(a)(6):** "Legal holiday" is defined by a list of named days, plus any
  day the Governor or Legislature designates. See Section 5.

## 3. Additional time for the service method: URCP 6(c)

> "When a party may or must act within a specified time after service and
> service is made exclusively by mail under Rule 5(b)(3)(C)(i), 7 days are
> added after the period would otherwise expire under paragraph (a)."

**This does not extend the time to answer a complaint.** Rule 5 governs
service of papers *after* the complaint. A summons and complaint are served
under **Rule 4**. So `ADDED_DAYS_BY_METHOD` is 0 for every method. It stays in
the script as a named constant so students can see the rule was considered.

(Federal practice is different. FRCP 6(d) adds 3 days for some service
methods. A chat without this skill often mixes the two systems up.)

## 4. When service is complete, by method (URCP 4)

| Method (script flag) | Rule | Service date to enter | Period |
|---|---|---|---|
| `personal` | 4(d)(1) | Date of delivery | 21 days |
| `mail` | 4(d)(2) | **Date the receipt is signed.** "Service by mail or commercial courier service shall be complete on the date the receipt is signed" (4(d)(2)(C)). | 21 days |
| `email` | 4(d)(3) acceptance (or 4(d)(5) court order) | Date of electronic acceptance, or the date the court's order sets | 21 days |
| `out-of-state` | 12(a)(1) | Date of service outside Utah | 30 days |

## 5. Utah legal holidays: Utah Code 63G-1-301

In the statute, a fixed-date holiday that falls on a Saturday is observed the
preceding Friday. One that falls on a Sunday is observed the following Monday.
Every Sunday is a legal holiday.

**Recent changes (flagged `VERIFY` by the script):**
- **Good Friday** became a legal holiday in the version effective **5/6/2026**
  (2026 Gen. Sess. ch. 124). Good Friday 2026 (Apr 3) came before that date,
  so the first one that counts is **Mar 26, 2027**.
- **Juneteenth:** Through 2026, the statute says it is observed on a Monday.
  Starting **1/1/2027** (ch. 126), it is June 19, with the usual
  Saturday-to-Friday and Sunday-to-Monday shifts. URCP 6(a)(6)(E) still
  describes it as "the third Monday of June."

| 2026 | Holiday | 2027 | Holiday |
|---|---|---|---|
| Thu Jan 1 | New Year's Day | Fri Jan 1 | New Year's Day |
| Mon Jan 19 | Dr. Martin Luther King, Jr. Day | Mon Jan 18 | Dr. Martin Luther King, Jr. Day |
| Mon Feb 16 | Presidents' Day | Mon Feb 15 | Presidents' Day |
| n/a | (Good Friday not yet effective) | Fri Mar 26 | Good Friday |
| Mon May 25 | Memorial Day | Mon May 31 | Memorial Day |
| Mon Jun 15 | Juneteenth (observed) | Fri Jun 18 | Juneteenth (observed) |
| Fri Jul 3 | Independence Day (observed) | Mon Jul 5 | Independence Day (observed) |
| Fri Jul 24 | Pioneer Day | Fri Jul 23 | Pioneer Day (observed) |
| Mon Sep 7 | Labor Day | Mon Sep 6 | Labor Day |
| Mon Oct 12 | Columbus Day | Mon Oct 11 | Columbus Day |
| Wed Nov 11 | Veterans Day | Thu Nov 11 | Veterans Day |
| Thu Nov 26 | Thanksgiving Day | Thu Nov 25 | Thanksgiving Day |
| Fri Dec 25 | Christmas Day | Fri Dec 24 | Christmas Day (observed) |
| | | Fri Dec 31 | New Year's Day 2028 (observed) |

Not included: days the Governor declares by proclamation (63G-1-301(5)), and
any closure of a particular court.

## 6. Firm policy: client signing deadline

The signing deadline is **not a court rule**. It is the answer deadline minus
7 calendar days, rolled **back** to the prior business day. That leaves the
firm a week to prepare and file the answer.

## 7. What to tell the lawyer

Always report the service method assumed, the holidays applied or skipped, the
rules cited, and any `VERIFY` or `WARNING` lines from the script. Then tell the
lawyer to **verify every date before sending the letter.**
