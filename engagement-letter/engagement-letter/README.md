# Engagement Letter Skill: Presenter Guide

*This file is for presenters. Claude does not load it.*

This skill drafts a client engagement letter for a fictional Utah firm,
Canyon & Crest LLP. It is built to show five things a skill can do that a
plain prompt, a Gem, or a Project cannot do reliably:

- **Auto-triggering:** it activates on its own when someone asks for an engagement letter.
- **Progressive disclosure:** it loads only the files the current matter needs.
- **Bundled scripts:** tested code computes court deadlines instead of the model guessing.
- **Bundled templates:** the firm's real letterhead and standard form travel with it.
- **Real tracked changes:** it produces a Word redline you can Accept or Reject.

Everything is short and plain so students can open each file and see how it works.

## Which file shows which capability

| Capability | File(s) | What to point out |
|---|---|---|
| Auto-triggering | `SKILL.md` (the `description` line) | Only this one line is always in Claude's context. The rest loads on a match. |
| Structured intake | `SKILL.md` Step 1 | Multiple-choice questions through AskUserQuestion or the platform's equivalent. |
| Progressive disclosure | `SKILL.md` Step 2, `references/` | Transactional letters never open `urcp-deadlines.md` or the litigation clauses. |
| Bundled executable script | `scripts/compute_deadline.py` | Holidays and rule periods are named constants at the top. Instructors can edit them. |
| Tested behavior | `tests/test_compute_deadline.py` | Run `python -m pytest tests` (17 tests). |
| Bundled assets/templates | `assets/letterhead-template.docx`, `assets/standard-form.md` | Firm branding and the baseline text, kept outside the prompt. |
| Template filling | `scripts/fill_template.py` | Clause sections replace or extend the standard form. |
| Real tracked changes | `scripts/redline.py` | Writes `<w:ins>`/`<w:del>` XML. Reject All gives the standard form. Accept All gives the letter. |

**A legal teaching point built into the script:** URCP 6(c) adds 7 days for
*mail* service, but only for papers served under Rule 5. A summons and
complaint are served under Rule 4, so no days are added to the answer deadline.
A chat without the skill often adds 3 days, which is the federal FRCP 6(d)
rule, or 7 days from 6(c). The script's `rules_applied` output explains why it
adds none. Utah also made Good Friday a legal holiday in 2026. See
`references/urcp-deadlines.md`.

## Demo script

**Before you start:** install the skill (see below). Start a new chat for each demo.

### (a) Litigation letter: shows triggering, intake, the deadline script, and the redline

> I need an engagement letter for a new client, Juniper Ridge Outfitters, Inc. They were personally served with a breach-of-contract complaint in Fourth District Court on November 20, 2026. We'll bill hourly at $375 partner / $260 associate and want a $15,000 retainer.

What to point out:
- The skill triggers on its own, and the intake questions fill in anything the prompt left out.
- Claude reads `clauses-litigation.md` and `urcp-deadlines.md`, then runs `compute_deadline.py`.
- Answer due **Friday, December 11, 2026**. Client must sign by **Friday, December 4, 2026**.
  Thanksgiving (Nov 26) falls inside the period but is **counted**, not skipped (URCP 6(a)(1)(B)).
- Open the redline in Word: Review > Tracking. The added Preservation of Evidence
  and No Guarantee clauses are whole-paragraph insertions. Click **Reject All**
  and the text returns to the firm's standard form.
- The reply ends with the assumptions and a reminder to verify every date.

Variation: say "served by mail, receipt signed November 20" or "served in Idaho"
(30 days, due **Monday, December 21, 2026**, because Dec 20 is a Sunday).

### (b) Transactional letter: shows the deadline files never load

> Draft a retention letter for Maple Hollow Bakery LLC for their purchase of the assets of a second bakery location in Lehi. Hourly at $350/$240 capped at $18,000, $7,500 retainer.

What to point out:
- Claude reads only `clauses-transactional.md`. No deadline questions, no
  `urcp-deadlines.md`, no `compute_deadline.py`. In Claude Code, show the tool
  calls. In Claude.ai, expand the "thinking/tool use" view.
- The redline shows different changes: a new "Identity of Client; Other Parties"
  clause, and file retention changed from five years to seven.

### (c) Same litigation request with no skill, for comparison

Turn the skill off (Settings > Capabilities > Skills), or use another assistant,
and paste prompt (a) again. Discuss:
- Did it know the firm's letterhead and standard clauses? (No. It made them up.)
- What answer deadline did it give? Did it add 3 or 7 days for mail, or skip
  Thanksgiving as if it were a business-day count?
- Can you Accept or Reject its "redline" in Word? (Usually it's colored text,
  strikethrough formatting, or no redline at all.)
- Would you get the same answer twice?

## Install

**Claude.ai (web or desktop):**
1. Find this folder, the `engagement-letter` folder that contains `SKILL.md`.
2. Right-click it and zip it. On Windows, choose **Compress to ZIP file** (or
   **Send to > Compressed (zipped) folder**). On a Mac, choose **Compress**.
3. In Claude, go to **Settings > Capabilities > Skills**, choose **Upload skill**,
   and pick the zip. Code execution must be turned on.

**Claude Code:** copy this folder to `~/.claude/skills/engagement-letter/` (all
your projects) or to `.claude/skills/engagement-letter/` inside one project.

**Other platforms:** `SKILL.md` follows the open Agent Skills format. The
scripts are plain Python 3, and `compute_deadline.py` uses only the standard
library. On platforms without skill support, you can paste `SKILL.md` in as
instructions and run the scripts yourself.

Requirements: Python 3.9+ and `python-docx` for the two document scripts
(`pip install python-docx`). The tests need `pytest`.

## For instructors

- **Change holidays or periods:** edit the constants at the top of
  `scripts/compute_deadline.py`, then run `python -m pytest tests`.
- **Change firm language:** edit `assets/standard-form.md` (the baseline) or a
  `references/clauses-*.md` file. A `## Heading` that matches a standard section
  replaces it. A new heading adds a clause.
- **Change the letterhead:** edit `assets/letterhead-template.docx` in Word and
  keep the `{{placeholders}}` and the `{{BODY}}` paragraph. You can also change
  and rerun `build_letterhead.py`. It is in the `extras` folder next to this
  skill folder, so it is not part of the skill. It is a one-time build step:
  Claude uses the finished template and never needs to rebuild it.
- Rule text was last verified on **September 22, 2026**. Check it again before each term.

*Canyon & Crest LLP, its address, its attorneys, and all clients are fictional.
This skill is a teaching demo, not legal advice.*
