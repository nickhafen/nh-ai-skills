---
name: draft-complaint-utah
description: "Draft a Utah state-court civil complaint from client facts in modules (chronology, claims, element map, damages, draft, multi-perspective review, memo). Runs fully or per module and validates outside timelines and research from Harvey, CoCounsel, Lexis, and similar tools."
---

# Draft Complaint (Utah) — workflow hub

This file is the orchestrator. Read a module's instructions in `references/modules/` **only when you run that module**. All modules share one data file, `<Case> - matter.json` (schema: `references/schemas.md`). The scripts read and check that file, so work never passes between modules as prose alone.

## Principles
1. **Primary sources over AI summaries.** Outside timelines and research memos are leads to check. They are never the source.
2. **Intermediate work product before prose:** chronology → claims chart → element map → damages → draft.
3. **Code for anything deterministic.** Numbering, cross-references, arithmetic, tier, format, and checks all run through `scripts/`. Never do arithmetic or type paragraph numbers by hand.
4. **Default and disclose.** Make judgment calls, log them in `decisions`, and stop only at the gates below.
5. **Verify what can be verified.** Cases must exist (CourtListener) and support the proposition cited (pinpoint).
6. **Out of scope.** This skill does not run a conflicts check, does not analyze limitations periods, and does not check whether rules or statutes have been amended. The attorney is responsible for all three. The rules pack in `references/rules/` is a snapshot with the date it was verified; confirm it is current before relying on it.
7. **Honest process record.** Log every module in `run_log`. Never claim a step, tool, or independent agent that did not run.

## Gates
- **Hard (always stop):**
  - client identity or role unclear;
  - a fact that decides whether a claim exists at all is missing;
  - any filing or sending;
  - changes to the rules pack, clause library, or template.
- **Soft (stop only in `pause` mode, at the profile's `pause_points`):** claim posture, marginal claims, party structure, tier, jury.
- **Flag and disclose:** everything else.

## Run order
| Step | Module file | Main output | Script |
|---|---|---|---|
| 0 | `m0-intake.md` | plan, profile, `matter.json` skeleton | — |
| 1 | `m1-chronology.md` | `chronology` (GENERATE or VALIDATE) | — |
| 2 | `m2-claims.md` | `claims`, `decisions` (MERGE memos; screen with `common-misses.md`) | — |
| 3 | `m3-elements.md` | `elements` + citation verification | `validate_matter.py` |
| 4 | `m4-calculations.md` | `damages`, tier | `validate_matter.py` |
| 5 | `m5-drafting.md` | `complaint` → .docx (start from `assets/template-matter.json`; clauses from `references/clauses/`) | `render_complaint.js` |
| 6 | `m6-review.md` | `review_log` (independent opposing-counsel lens if the profile requires it) | `workflows/complaint-review.js` (optional) |
| 7 | `m7-memo.md` | memo + working papers | `build_workpapers.py`, `validate_matter.py` |
| 8 | `m8-template-capture.md` | proposed template, clause, and checklist updates | — |

**Entry points:**
- Full run: steps 0–7.
- "Just the chronology": 0 and 1.
- "Here's my Harvey timeline": 1 in VALIDATE mode, then continue.
- "Review my draft": convert the draft into `matter.complaint`, then run 3, 4, 6, and 7.
- After approval: 8.

## Commands
```bash
node scripts/render_complaint.js "<Case> - matter.json" "<Case> - Draft Complaint.docx" [--profile profiles/default.json]
python3 scripts/validate_matter.py "<Case> - matter.json"          # must exit 0 before handoff
python3 scripts/build_workpapers.py "<Case> - matter.json" "<Case> - Draft Complaint.paranums.json" "<Case> - Working Papers.xlsx"
```
Requires `docx` (npm) and `openpyxl`. Install either if missing.

## Resources
- `profiles/default.json` sets defaults: pause at M2, core+alternatives, jury demand on, no case law in complaints, fresh-agent adversarial review, rules pack max age 90 days.
- `references/rules/`: `urcp-complaint-checklist.md` (verbatim rule text), `manifest.json` (sources, effective dates, date last verified), and `README.md` (**rule currency is the attorney's responsibility**). Keep the full URCP text there as an optional search file and do not load it by default.
- `references/common-misses.md`: prerequisites and bars that research tools miss. Grows with every real miss.
- `references/clauses/`: element-tagged pleading clauses with verification logs (index in `README.md`).
- `references/tool-routing.md`: which tool to use for what.
- `assets/`: `complaint-template.docx`, `template-matter.json`, `sample-matter.json` (a schema example only).
- `workflows/`: optional multi-agent scripts for review and evals.
- `evals/`: trap-based test cases. Answer keys live outside the skill, in `extras/answer-keys/`. **Never read them during a drafting run.**
