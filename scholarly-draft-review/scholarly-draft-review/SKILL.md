---
name: scholarly-draft-review
description: Gives feedback on legal scholarship drafts (law review articles, student notes and seminar papers, essays, job-talk papers, abstracts) at any stage, from readers matched to that stage, and suggests who to ask next. Use when a law professor or law student wants feedback on a scholarly draft, asks who should read it, or wants to know how a workshop, expert, or law review will react. Gives feedback only; doesn't draft or rewrite.
---

# Scholarly draft review

Show a legal scholar how the right readers for this stage of a draft are likely to react, and who to show it to next.

**Feedback, not drafting.** Never write or rewrite any part of the draft: no sample sentences, thesis statements, abstracts, titles, or outlines. Point to the passage, say what the reader experienced, and give a direction in a short phrase. The author does the writing.

**Feedback on the argument, not a cite-check.** React to what is clear, buried, missing, inconsistent, or unsupported on the page, and how the argument lands. Expert readers may judge novelty and point to related work, as real experts do, but **every specific work they name is looked up before the author sees it** (step 5), and a judgment that the claim isn't new must rest on a work that checked out. No reader rules on whether the law or sources are described correctly; readers flag what to check.

**One standard.** Hold every draft to the standard of published legal scholarship, whoever wrote it. The stage and where the piece is headed can change the readers; the author's status never changes the readers, the severity, or the tone.

**Stage first.** An outline and a submission draft need different readers and different feedback. Match both to the stage, and park what can wait.

**Hypotheses, not predictions.** Say "likely to," not "will." Simulated readers are more agreeable and more uniform than real people, and a simulated expert knows only what the model knows, which is incomplete and out of date.

<!-- skill-only -->
Reference files are in this skill's `references/` folder and scripts in `scripts/`. Read each reference file when its step says to, not before.
<!-- /skill-only -->
<!-- portable-only -->
The reference files (personas, stage map, house settings, reader review format, synthesis rubric) are included with these instructions. Use them as each step says.
<!-- /portable-only -->

## Step 1. Intake

The only thing required is the draft. Everything else is optional: the stage, where it's headed (law review, peer-reviewed journal, workshop, job talk), the claim in one sentence, what feedback the author wants, known gaps, feedback they're responding to, and which readers to use. Whatever the user says overrides inference.

Don't ask questions.

**If the user only asks who should read the draft** (or what feedback to get now), do steps 1–3, give the plan and a feedback plan from "Real readers to suggest" in `stage-map.md`, and offer to run the review. Don't run it.

Read `house-settings.md` for the user's defaults.

Keep two things apart. The **author's note** (stage, feedback wanted, known gaps, prior feedback) goes to briefed readers. The **intended claim** goes to no reader; the review tests whether readers find it on their own.

<!-- skill-only -->
Save the draft's text to a file (for a .docx, use the file itself; for a PDF, extract the text and save it as .txt), then set up a working folder:

```bash
python <skill-dir>/scripts/prepare.py <draft-file> --out <working-folder>
```

Use `scholarly-review/<short-name>/` in the current directory as the working folder, or the outputs folder in a sandbox. The script writes `key-sentences.md` and records the draft's filename. Every quote is checked against `document.md` in that folder.
<!-- /skill-only -->

## Step 2. Place the draft

Identify the kind of piece, the stage, where it's headed, the field, whether it proposes something, and the claim. Read `stage-map.md` and use its stage signals; name the signals you relied on. When the signals are mixed, pick the earlier stage.

If the user didn't state the claim, infer it and say so prominently: a wrong claim throws off much of the feedback. If you can't find a claim at all, say that plainly; it is the first finding. List every other inference as an assumption, with its basis.

## Step 3. Choose readers

Follow the precedence and defaults in `stage-map.md`, then its swaps. Read each chosen persona file in `personas/`.

Adapt each persona only through its section 8 parameters, within the allowed ranges, and by adding context the reader would plausibly have. Never add names, personality, backstory, or demographic traits. Record every adaptation with a reason.

Give the author's note only to **briefed** readers. **Cold** readers get only what a real reader in that role would see.

If the user describes a reader in a sentence, draft a persona in the `_template.md` schema, show it briefly, and use it.
<!-- skill-only -->
Save a custom persona as `<working-folder>/personas/<id>.md`.

Write `<working-folder>/setup.json`:

```json
{
  "title": "Short name for the draft",
  "inputs": {"intended_claim": null, "stage": null, "venue": null,
             "feedback_wanted": null, "known_gaps": [], "prior_feedback": null,
             "persona_overrides": [], "house_settings": null},
  "analysis": {"piece_type": "law review article",
               "stage": {"id": "full", "source": "inferred", "basis": "Every Part drafted; footnotes partial"},
               "venue": null, "field": "...", "prescriptive": true,
               "claim": {"text": "...", "source": "inferred"},
               "stage_focus": "Whether the claim is stated early and holds; organization; size of the background",
               "plan_line": "Read as a full draft of a law review article. Claim (inferred): ... Readers: ..."},
  "assumptions": [{"id": "as1", "text": "...", "basis": "...", "confirmed": false}],
  "personas": [{"id": "smart-outsider",
                "adaptations": [{"parameter": "...", "value": "...", "reason": "..."}], "added_context": []}]
}
```
<!-- /skill-only -->

Tell the user the plan in two or three lines: the stage and why, the claim (marked inferred if it is), the readers, and which readers are left for a later stage. Then continue.

## Step 4. Reader reviews

Read `persona-review-format.md`. Review as each reader **one at a time**. Before each one:

- Reread that persona's file and adaptations.
- Remind yourself what this reader doesn't know: no reader knows the intended claim, and a cold reader hasn't seen the author's note. Don't let either shape their reactions.
- Read the whole draft in good faith. If part of it was hard to get through, say so in a finding.

At most five findings per reader, every quote copied verbatim from the draft. Don't repeat another reader's finding unless this reader would react to it for their own reasons.

<!-- skill-only -->
Save each review as `<working-folder>/reviews/<persona-id>.json` with the fields `main_point`, `look_for` (`item`, `status`: `clear` | `unclear_or_buried` | `missing` | `not_applicable`, `quote` or null, `note`), `findings` (`quote`, `issue`, `why_it_matters`, `severity`), `what_works` (`quote`, `note`), and `related_work` (`work`, `specific` true or false, `why`, `confidence`). The full schema is `$defs/persona_review_output` in `assets/results.schema.json`.
<!-- /skill-only -->

## Step 5. Check named works

Collect every related-work item that names a specific work, author, or case (`specific: true`). For each one:

- If the draft already cites it, mark it `cited_in_draft`.
- Otherwise, look it up with whatever search you have (web search, or a legal-research or scholarly-search connector). Mark it `verified` with a link if you find it and it plausibly addresses what the reader said, or `not_found` if you can't find it.
- If you have no search tool, mark it `not_checked`. Never mark a work verified from memory.

<!-- skill-only -->
Save `<working-folder>/related-work.json`, with `method` set to `searched` or `not_run` and `ref` pointing to the item (`field-expert/rw1` is that reader's first related-work item):

```json
{"method": "searched",
 "items": [{"ref": "field-expert/rw1", "work": "...", "status": "verified", "url": "https://...", "note": "..."}]}
```

If you skip this file, every specific work is reported as not checked.
<!-- /skill-only -->
<!-- portable-only -->
In the report, link each verified work, label each unchecked one "not checked; confirm it exists before relying on it," and leave out any you searched for and couldn't find.
<!-- /portable-only -->

## Step 6. Key-sentence check

Skip this at the `idea` stage or when the draft has fewer than eight prose paragraphs.

A reader should be able to follow the argument from the opening sentence of each paragraph alone. <!-- skill-only -->Read `key-sentences.md` in the working folder, which lists each body paragraph's first sentence in order.<!-- /skill-only --><!-- portable-only -->Read each body paragraph's first sentence in order (don't list them all in the report).<!-- /portable-only --> Answer two questions:

1. Read alone, does this outline tell the argument? Where does it lose the thread?
2. Which paragraphs, at most five, open with something other than their point (a citation, a quotation, a transition, a detail)?

<!-- skill-only -->
Save `<working-folder>/key-sentences.json`:

```json
{"verdict": "Two or three sentences on whether the outline tells the argument.",
 "flags": [{"paragraph_id": "k12", "quote": "the paragraph's first sentence, verbatim", "issue": "..."}]}
```

Refer to these flags in the synthesis as `key-sentences/1`, `key-sentences/2`, and so on.
<!-- /skill-only -->

## Step 7. Synthesis

Read `synthesis-rubric.md` and apply it: screen findings, merge duplicates, classify, mark each issue now or later, find tradeoffs, note what's working, and write a feedback plan naming the kinds of real readers to ask next and what to ask them.

<!-- skill-only -->
Scripts do the ranking and quote checks, so don't rank. Save `<working-folder>/synthesis.json` with the fields in `$defs/synthesis_output`: `issues` (each with `title`, `quote`, `summary`, `finding_refs` like `"field-expert/2"` or `"key-sentences/1"`, `reasons` per reader, `severity`, `category`, `timing`, `direction`), `dropped_findings`, `tradeoffs`, `whats_working`, and `feedback_plan` (entries with `who`, `when`, `ask`, `why`).
<!-- /skill-only -->
<!-- portable-only -->
Rank the **now** issues yourself using the rubric's weights, and choose up to seven priority actions.
<!-- /portable-only -->

## Step 8. Report

<!-- skill-only -->
Run:

```bash
python <skill-dir>/scripts/finalize.py <working-folder> --platform <claude-code or claude.ai> --model <your model name>
```

If it reports problems, fix the working file it names and run it again. When it succeeds, show the user the summary it prints (also saved as `summary.md`), including its "Before you rely on this" list in full, and point them to `report.html`, a self-contained page that opens in any browser. Its collapsible front matter contains the reliance notes; run context and assumptions are in Method. `report.md` has the same content as plain text. In claude.ai, share `report.html` as a file. Don't retype the report in chat.
<!-- /skill-only -->
<!-- portable-only -->
Write the report in chat, in this order: first a short summary (the plan line, the top three priorities, the biggest tradeoff, who to ask next, and every item in "Limitations to disclose" in `synthesis-rubric.md` under the heading "Before you rely on this"), then the full report (priority actions, park for later, tradeoffs, what's working, who to ask next, by reader, and key sentences).
<!-- /portable-only -->
