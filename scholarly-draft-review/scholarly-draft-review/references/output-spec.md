# Output spec

Every run produces one structured results file, `results.json`. The chat summary, `report.md`, and `report.html` are all rendered from it. The model writes the content once; scripts do the formatting and anything that can be computed.

The exact structure is in `assets/results.schema.json` (generated; edit `extras/build/build_schema.py` instead). This page explains it.

## results.json at a glance

| Section | What it holds | Produced by |
| --- | --- | --- |
| `run` | Run id, time, tool version, content hash of the skill files, model, platform | Script |
| `document` | The draft's filename, the working copy's filename (`document.md`), word count, section labels, and the key-sentence outline. Not the draft's text: the results and reports refer to the draft by filename, so they can be shared without it. | Script |
| `inputs` | What the user gave: intended claim, stage, venue, feedback wanted, known gaps, prior feedback, reader overrides, house settings | User |
| `analysis` | Kind of piece; stage with source and basis; venue; field; whether it proposes something; the claim (stated or inferred); what matters at this stage; the plan line | Model (step 2) |
| `assumptions` | Each inferred fact, its basis, and whether the user confirmed it | Model (step 2) |
| `personas` | Each reader as adapted: reader type, briefing, adaptations, added context, full adapted text | Model + script |
| `persona_reviews` | Each reader's review, in the format in `persona-review-format.md`, including its related-work pointers | Model (step 4) |
| `related_work_check` | Each specific work a reader named, with its status (`verified` with a link, `cited_in_draft`, `not_found`, or `not_checked`), and whether a search ran | Model (step 5), completed by script |
| `key_sentence_check` | Verdict and up to five flagged paragraphs, or null if the check didn't run | Model (step 6) |
| `synthesis` | Issues (each now or later), dropped findings, and what's working (from the model); ranking, priority actions, and parked issues (from script) | Model + script (step 7) |
| `quality` | Quote verification, named-work counts, and the limitations to disclose (standing ones plus any that apply to this run) | Script |

### Conventions

- **Related-work references.** A reader's related-work item is `persona-id/rwN` (for example `field-expert/rw1`).
- **Finding references.** A reader finding is `persona-id/n`, its 1-based position in that reader's findings (for example `field-expert/2`). A key-sentence flag is `key-sentences/n`.
- **Issue indexes.** Issues are referred to by their 0-based position in `synthesis.output.issues`. `priority_actions` (now issues, best first, at most seven) and `parked` (later issues) are lists of these indexes.
- **Quotes** are verbatim from the draft; footnote text counts. `quality.anchoring` records any quote the script couldn't find.
- **Nothing is dropped silently.** Findings removed in synthesis stay in `persona_reviews` and are listed in `synthesis.output.dropped_findings` with the rule that removed them.

## Chat summary

1. **Plan line**, the stage (marked inferred if it was), and the claim (marked inferred if it was)
2. **Top priorities now:** the first three, one line each, plus how many issues were parked for later
3. **Before you rely on this:** every limitation in `quality.limitations`, in full (see "Limitations to disclose" in `synthesis-rubric.md`)
4. **Link** to the HTML report

## HTML report

One self-contained file, rendered by `scripts/render_report.py` from `assets/report-template.html` with `results.json` embedded inline. It opens by double-click with no server or network access, prints cleanly, and follows the system's light or dark mode. With no embedded results, the same template is a viewer (`render_report.py --viewer`). Its collapsible header contains every "Before you rely on this" limitation. Tabs:

1. **Overview:** top priorities and what's working.
2. **Priorities:** priority actions followed by the remaining issues in one continuously numbered list. Issue cards show severity and readers, without filters or convergence tags.
3. **Readers:** one tab per reader with what they think the draft argues, look-for checks, findings, what to keep, and the work they'd point to; reader-tab buttons show names only.
4. **Key sentences:** the verdict, and the full outline with flagged paragraphs highlighted
5. **Method:** the draft's filename, run details, assumptions, readers as adapted, findings set aside, named works that couldn't be found, and a download of `results.json`

## Markdown report

`report.md`, rendered by `scripts/render_markdown.py`, has the HTML report's content on one page, in this order:

1. **Before you rely on this:** every limitation, in a collapsible block that starts open
2. **Priority actions:** priority actions followed by the remaining issues (now and later, by rank) in one continuously numbered list, each with severity, readers, quote, summary, and direction
3. **What's working**
4. **By reader:** what each thinks the draft argues, look-for checks, findings, what to keep, and the work they'd point to
5. **Key-sentence outline:** the verdict, flagged paragraphs, and the full outline in a collapsible block
6. **Method:** as in the HTML report, with each reader as adapted in a collapsible block
