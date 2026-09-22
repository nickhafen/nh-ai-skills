---
name: engagement-letter
description: Drafts a client engagement letter for Canyon & Crest LLP on firm letterhead as a Word .docx, plus a second .docx redline with real tracked changes showing every deviation from the firm's standard form. Handles litigation, transactional, and flat-fee matters with matter-specific clauses. For litigation it computes the Utah answer deadline and a client signing deadline. Use whenever someone asks to draft, prepare, write, generate, or tailor an engagement letter, retention letter, retainer letter, new-client letter, or letter of engagement, or to onboard or engage a new client, even if they don't say "engagement letter" exactly.
---

<!--
FOR STUDENTS: what each part of this file demonstrates
  * The `description` above -> AUTO-TRIGGERING. Only this line is always in
    Claude's context. Claude loads the rest of this file when a request matches it.
  * "Step 1: Intake" -> STRUCTURED QUESTIONS (AskUserQuestion or the platform's equivalent).
  * "Step 2" and the file table -> PROGRESSIVE DISCLOSURE. Claude reads only
    the clause file for this matter type. The deadline rules load only for litigation.
  * "Step 3" and "Step 4" -> BUNDLED EXECUTABLE SCRIPTS. The date math, document
    assembly, and redlining are done by tested code, not by the model.
  * assets/ -> BUNDLED TEMPLATES. The firm letterhead and standard form travel with the skill.
  * "Step 5" -> RELIABLE TRACKED CHANGES. redline.py writes real Word w:ins/w:del revisions.
-->

# Engagement Letter (Canyon & Crest LLP)

Produce two Word files for the lawyer:
1. the tailored engagement letter on firm letterhead, and
2. a redline of that letter against the firm's standard form, with real tracked changes.

**Never do date math, template filling, or redlining by hand.** Use the scripts
in `scripts/`. They are tested and they apply the firm's rules consistently.
Run them from this skill's folder. They need Python 3. `fill_template.py` and
`redline.py` also need `python-docx` (`pip install python-docx` if it is missing).

## Step 1: Intake

Collect these five fields. Skip any the user already gave you.

| Field | Example |
|---|---|
| Client name | Juniper Ridge Outfitters, Inc. |
| Matter description (completes "in connection with ...") | the defense of a breach-of-contract lawsuit filed against you in the Fourth District Court |
| Matter type | litigation, transactional, or flat-fee |
| Fee terms | hourly rates of $375 for partners and $260 for associates |
| Retainer amount | $15,000 |

Use your structured-question tool: **AskUserQuestion** in Claude Code, the
ask-user / multiple-choice input in Claude.ai, or the equivalent in ChatGPT or
another platform. If none exists, ask in one short numbered list.
- Ask **matter type** as a multiple-choice question: Litigation / Transactional / Flat fee.
- Offer common choices for **fee terms** (for example: firm standard hourly rates,
  hourly with a cap, flat fee) and **retainer** (for example: $2,500 / $5,000 / $10,000).
  Let the user type their own.
- Ask for client name and matter description as free text.
  A client mailing address is optional. If it is missing, the letter shows `[Client Address]`.

## Step 2: Load only what this matter needs

| Matter type | Read | Also read |
|---|---|---|
| litigation | `references/clauses-litigation.md` | `references/urcp-deadlines.md` |
| transactional | `references/clauses-transactional.md` | nothing else |
| flat-fee | `references/clauses-flat-fee.md` | nothing else |

**Read `references/urcp-deadlines.md` and run `compute_deadline.py` ONLY for
litigation matters.** Do not open either one for transactional or flat-fee letters.

## Step 3: Litigation only: compute the deadlines

Ask two more questions (structured tool, as above):
- **Date of service** of the summons and complaint (YYYY-MM-DD). For mail
  service, this is the date the receipt was signed.
- **Service method**: personal (in Utah) / mail / email (electronic acceptance) / out-of-state.

Then run:

```
python scripts/compute_deadline.py --service-date 2026-11-20 --service-method personal --event answer > deadlines.json
```

The JSON has `answer_deadline`, `signing_deadline`, `period_days`,
`rules_applied`, `assumptions`, and `holidays_skipped`. Keep it for Steps 4 and 6.
The litigation clause file puts these dates in the Scope section automatically.

## Step 4: Fill the letterhead

Write the intake to `intake.json` in a working folder:

```json
{"client_name": "...", "client_address": "optional; use \n between lines",
 "matter_description": "...", "matter_type": "litigation",
 "fee_terms": "...", "retainer_amount": "$15,000"}
```

Then run (leave out `--deadlines` unless the matter is litigation):

```
python scripts/fill_template.py --intake intake.json --clauses references/clauses-litigation.md --deadlines deadlines.json --out "Engagement Letter - <Client>.docx"
```

If the script reports a missing field, ask the user for it. Do not invent one.

## Step 5: Produce the redline

```
python scripts/redline.py --intake intake.json --letter "Engagement Letter - <Client>.docx" --out "Redline vs Standard Form - <Client>.docx"
```

This compares the firm's standard form (`assets/standard-form.md`, filled with
the same intake) against the tailored letter. It writes tracked changes by
"Engagement Letter Skill" that the lawyer can Accept or Reject in Word.

Save both .docx files where the user can open them: the working directory in
Claude Code, or the outputs folder on Claude.ai. Give the user a link or path to each.

## Step 6: Report back

Keep the reply short:
1. The two files, and what each one is.
2. A summary of the redline counts from `redline.py`'s output (clauses added and modified).
3. **For litigation, an "Assumptions" section** built from the script's JSON:
   the service method and date assumed, the rules applied (URCP 12(a), 6(a), and
   why 6(c)'s mail extension does not apply), the holidays counted or skipped,
   and any `VERIFY` or `WARNING` lines, word for word.
4. End every litigation letter reply with: **"Verify all dates against the
   current rules and the court's calendar before sending this letter."**

Do not give legal conclusions beyond what the scripts computed. If the facts
suggest a different deadline applies (a Rule 12(b) motion already filed, an
extension order, or a government defendant), say so and tell the lawyer to
calculate that deadline themselves.
