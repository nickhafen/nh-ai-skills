# Output spec

Every run produces one structured results file, `results.json`. Every output format (chat summary, HTML report, Word memo, hosted viewer) is rendered from it. The model writes the content once; scripts do the formatting and anything that can be computed.

The exact structure is defined in `assets/results.schema.json`. This page explains it.

## results.json at a glance

| Section | What it holds | Produced by |
| --- | --- | --- |
| `run` | Run id, time, tool version, content hash of the skill files, model, execution strategy (`isolated`, `single`, or `baseline`), validation condition if any, mode (fast or guided), token usage and estimated cost | Script |
| `document` | Full text, word count, and sections (headings, or paragraphs if there are none) with ids like `s1` or `p3` | Script |
| `inputs` | What the user gave: goal, audience, background items with sensitivity labels, persona overrides, house settings | User |
| `analysis` | Document type, stage, author's side, ask, deadline, goal (stated or inferred), primary and secondary readers, and the plan line | Model (step 2) |
| `assumptions` | Each inferred fact, its basis, and whether the user confirmed it | Model (step 2) |
| `personas` | Each persona as adapted: tier, role (primary or secondary), adaptations with reasons, added context, which background items it received, and the full adapted text | Model + script |
| `persona_reviews` | Each persona's review in the format in `persona-review-format.md` | Model (step 4) |
| `ai_reader` | Recipient, batteries run, every prompt with its full answer, and the survival check | Model (step 5) |
| `synthesis` | Issues, dropped findings, tradeoffs, what's working, AI-reader highlights, next steps (from the model); ranking, priority actions, reader-specific grouping (from script) | Model + script (step 6) |
| `quality` | Anchoring rate with unverified quotes, persona distinctiveness, stance spread, assumption load, coverage (unassessed look-for items, attention gaps, review gaps), leaks, standing caveats | Script |
| `prompts` | Every model call verbatim: system prompt, messages, response, stop reason, usage | Script |

### Conventions

- **Finding references.** A finding is referred to as `persona-id/n`, its 1-based position in that persona's findings (for example `opposing-counsel/2`). Synthesis issues point to findings this way.
- **Issue indexes.** Synthesis issues are referred to by their 0-based position in `synthesis.output.issues`. `priority_actions` is a list of these indexes, best first.
- **Document marker.** In `prompts`, the document text is replaced by `[[DOCUMENT]]` to keep the file small. Anything that shows or copies a prompt substitutes `document.text` back in, so the copied prompt is exactly what ran.
- **Quotes** are verbatim from the document. `quality.anchoring` records any that the script couldn't find.
- **Nothing is dropped silently.** Findings removed in synthesis stay in `persona_reviews` and are listed in `synthesis.output.dropped_findings` with the rule that removed them.

### When there's no file

Portable versions (paste-in prompt, Gem, Project) can't write files. They output the report as markdown in chat, in the section order below, then the same content as a JSON code block that follows the schema as closely as the platform allows. The hosted viewer accepts that JSON and shows whatever sections are present.

## Chat summary

Always shown. Short enough to read without scrolling far.

1. **Plan line:** what the document was read as, the goal (marked "inferred" if it was), and the readers used
2. **Top priority actions:** the first three, one line each
3. **Biggest tradeoff:** one, if any
4. **Coverage note:** sections no reader read closely, if any
5. **Links** to the HTML report and any other files
6. **Standing caveat**, in one sentence

## HTML report

Default in skill environments; `report.md` carries the same content as plain text. One self-contained file, rendered by `scripts/render_report.py` from `assets/report-template.html` with `results.json` embedded inline, so it opens by double-click with no server or network access, prints cleanly, and follows the system's light or dark mode. The same template with no embedded results is a viewer: `render_report.py --viewer` writes a page that opens or pastes any `results.json`. It's organized as tabs:

1. **Overview:** goal, top three priorities, survival check, biggest tradeoff, run quality, what's working
2. **Priorities:** ranked issues, each expanding to what each reader said, plus tradeoffs; filterable by severity and reader
3. **Readers:** one tab per persona with main point, gut reaction, next step, look-for checks, findings, what to keep, and a section-by-section attention strip
4. **AI reader:** the survival check and each prompt with its answer, or the prompts to copy if the check wasn't run
5. **Next steps:** revision prompts with copy buttons, assumptions to confirm, follow-up reviews, real review
6. **Method:** run details, assumptions, personas as adapted, findings set aside, every prompt with a copy button (document filled back in), and a download of `results.json`

Quoted passages are set in a serif face with a rule so they read as the document's own words.

## Word memo

On request. Built from a template with existing Word styles. Sections:

1. Summary and goal
2. Priority actions
3. Tradeoffs
4. One short paragraph per reader
5. AI-reader highlights
6. Next steps
7. Appendix (optional, off by default): prompts and adapted personas
