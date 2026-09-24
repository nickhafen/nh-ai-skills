# Phase 0 review checklist

**Status: complete.** Attorney review signed off 2026-09-22.

Phase 0 is done when every file follows the schema and an attorney has reviewed the content. Run `python build/check_personas.py` for the schema check. This page covers the attorney review. Decisions made so far are in `decisions.md`.

## What to review

For each persona in `fresh-eyes-review/references/personas/`:

- [x] Describes the typical member of the group, not an ideal or unusual one
- [x] No names, backstories, quirks, or demographic attributes
- [x] "What they look for" items are writing-level checks (present, clear, findable), not substantive ones
- [x] "Attention budget" and "misreadings" match how this reader actually behaves
- [x] Adaptable parameters and ranges are the right dimensions
- [x] Out-of-scope section keeps the persona in its lane
- [x] Common variant is the one users would most likely want
- [x] When approved, change `status: draft` to `status: attorney-reviewed`

| Persona | Tier | Reviewed | Roster flag |
| --- | --- | --- | --- |
| senior-colleague | A | [x] | |
| client-individual | B | [x] | |
| client-business-decision-maker | B | [x] | vs. in-house counsel |
| client-in-house-counsel | B | [x] | vs. business decision-maker |
| opposing-counsel | C | [x] | |
| opposing-party-unrepresented | C | [x] | vs. insurance claims professional |
| insurance-claims-professional | C | [x] | vs. unrepresented party |
| trial-judge | C | [x] | vs. clerk; vs. future interpreting court |
| judicial-law-clerk | C | [x] | vs. trial judge (tested first) |
| appellate-judge | C | [x] | |
| regulator-agency-staff | C | [x] | |
| mediator | C | [x] | possibly unnecessary |
| counterparty-business-contact | C | [x] | |
| implementer-operations | B | [x] | |
| future-interpreting-court | C | [x] | vs. trial judge |
| public-press-reader | C | [x] | |

Also review:

- [x] `doc-type-map.md` — primary and secondary readers, swaps, and coverage notes for each document type
- [x] `house-settings.md` — roles and what each changes
- [x] `persona-review-format.md` — what each persona returns, and the in/out-of-scope examples
- [x] `ai-reader-prompts.md` — prompt wording and survival-check questions
- [x] `synthesis-rubric.md` — screening rules, coverage sweep, ranking weights, next steps

## Open items at sign-off (all resolved; see `decisions.md`)

- Validation fixtures: four.
- `output-spec.md` and the `results.json` schema: moved to Phase 1.
- Web app: practitioners (and students), subscription, firm-grade confidentiality.
