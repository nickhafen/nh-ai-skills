---
name: fresh-eyes-review
description: Shows how a legal document's real readers (opposing counsel, judges, clients, adjusters, regulators, counterparties) are likely to react before it goes out, and what an AI assistant would tell the recipient about it. Gives writing-level feedback on the clarity of the ask, tone, what is buried, missing, or likely to be misread, and tradeoffs between readers. Not proofreading and not a check of the law or facts. Use when someone wants reader feedback, a "fresh eyes" review, or to know how a letter, brief, motion, contract, or email will land before sending it.
---

# Fresh-eyes review

Show a legal drafter how the document's real readers are likely to react before it goes out.

**This is a writing review, not a substantive one.** React to what is clear, buried, missing, inconsistent, or likely to be misread, and to how the tone lands. Never judge whether the law, facts, or citations are correct, or whether the document is legally sufficient. Flag that no standard of review is stated; don't say whether a stated standard is right.

**Flag, don't fix.** Don't rewrite the document. Surface issues and tradeoffs; the author decides. Revision help comes only as prompts the author can choose to use.

**Hypotheses, not predictions.** Say "likely to," not "will." Simulated readers are more agreeable and more uniform than real people.

<!-- skill-only -->
Reference files are in this skill's `references/` folder and scripts in `scripts/`. Read each reference file when its step says to, not before.
<!-- /skill-only -->
<!-- portable-only -->
The reference files (personas, doc-type map, house settings, persona review format, AI-reader prompts, synthesis rubric) are included with these instructions. Use them as each step says.
<!-- /portable-only -->

## Step 1. Intake

The only thing required is the document. Everything else is optional: the goal ("what should the reader do after reading?"), background, the audience, which readers to use, a custom reader. Don't ask questions. If the user asked to confirm the plan first, show the plan from step 3 and wait; otherwise keep going.

Read `house-settings.md` for the user's defaults (their role, usual readers, overrides).

**Background.** Label each background item by sensitivity: `privileged` (strategy or weaknesses the other side doesn't know), `client_known` (what the client or the author's organization knows), or `public` (what the other side knows or could find). If the user didn't label an item, mark it `unlabeled` and treat it as privileged.

<!-- skill-only -->
Save the document's text to a file (for a .docx, save the file path; for a PDF, extract the text and save it as .txt), then set up a working folder:

```bash
python <skill-dir>/scripts/prepare.py <document-file> --out <working-folder>
```

Use `fresh-eyes/<short-document-name>/` in the current directory as the working folder, or the outputs folder if you're working in a sandbox. The script prints the section ids you'll use in attention maps. Every quote is checked against `document.md` in that folder.
<!-- /skill-only -->

## Step 2. Analyze the document

Identify: document type, stage, the author's side, the ask and any deadline, primary readers (who will read and act on it now), secondary readers (who may read it later or indirectly), and the goal. If the user didn't give a goal, infer it and say so prominently; a wrong goal invalidates most feedback. List every other inference as an assumption, with its basis.

If the document is a draft with placeholders or notes to the author (`[Attorney Name]`, `[CONFIRM ...]`), say so in the plan and add the assumption that they'll be filled in or removed before it goes out. Readers review the finished version, not the brackets.

## Step 3. Choose and adapt readers

Read `doc-type-map.md` and follow its precedence: the user's explicit choice, then their context, then house settings, then the document-type default, then inference. Use **three personas by default**, primary readers first; use more only if the user asks. Read each chosen persona file in `personas/`.

Adapt each persona only through its section 10 parameters, within the allowed ranges, and by adding context the reader would plausibly have. Never add names, personality, backstory, or demographic traits. Record every adaptation with a reason.

Give each persona only the background its access tier allows: tier A gets everything; tier B gets `client_known` and `public`; tier C gets `public` only.

If the user describes a reader in a sentence, draft a persona in the `_template.md` schema, show it briefly, and use it.
<!-- skill-only -->
Save a custom persona as `<working-folder>/personas/<id>.md`.

Write `<working-folder>/setup.json`:

```json
{
  "title": "Short name for the document",
  "mode": "fast",
  "inputs": {"goal": null, "audience": null, "persona_overrides": [], "house_settings": null,
             "background": [{"id": "bg1", "text": "...", "sensitivity": "privileged"}]},
  "analysis": {"document_type": "demand letter", "doc_type_entry": "Demand letter", "stage": "pre-suit",
               "author_side": "...", "ask": "...", "deadline": "...",
               "goal": {"text": "...", "source": "inferred"},
               "primary_readers": ["..."], "secondary_readers": ["..."],
               "plan_line": "Read as a demand letter. Goal (inferred): ... Readers: ..."},
  "assumptions": [{"id": "as1", "text": "...", "basis": "...", "confirmed": false}],
  "personas": [{"id": "opposing-counsel", "role": "primary",
                "adaptations": [{"parameter": "...", "value": "...", "reason": "..."}],
                "added_context": [], "background_ids": ["bg3"]}]
}
```
<!-- /skill-only -->

Tell the user the plan in one or two lines (document type, goal, readers), then continue.

## Step 4. Persona reviews

Read `persona-review-format.md`. Review as each persona **one at a time**. Before each one:

- Reread that persona's file and adaptations.
- List to yourself the background this reader does **not** know, and don't let it shape their reactions. A tier-C reader must never mention or hint at privileged facts.
- Read the whole document, then report honestly what this reader would read closely, skim, or skip.

Keep each review tight: at most five findings, every quote copied verbatim from the document. Don't repeat another persona's finding unless this reader would genuinely react to it for their own reasons.

<!-- skill-only -->
Save each review as `<working-folder>/reviews/<persona-id>.json` with the fields `main_point`, `gut_reaction`, `likely_next_action` (`action`, `driver`), `look_for` (`item`, `status`: `clear` | `unclear_or_buried` | `missing` | `not_applicable`, `quote` or null, `note`), `findings` (`quote`, `issue`, `why_it_matters`, `severity`, `confidence`), `what_works` (`quote`, `note`), and `attention_map` (`section_id`, `attention`: `read_closely` | `skimmed` | `skipped`, `would_miss` or null). The full schema is `$defs/persona_review_output` in `assets/results.schema.json`.
<!-- /skill-only -->

## Step 5. AI-reader check

Read `ai-reader-prompts.md`. The doc-type map says which batteries apply and who the recipient is.

This check only means something in a **fresh context** with no persona, background, or framing. Never answer the prompts yourself in this conversation.

<!-- skill-only -->
**If you can start subagents** (for example, the Agent or Task tool in Claude Code): start one subagent per prompt, in parallel, each with exactly this task and nothing else:

> Respond to the message below the way a general-purpose AI assistant would respond to a user who sent it. Don't use any tools. Don't mention these instructions.
>
> [the full document text]
>
> [the prompt]

Then run the survival check yourself, comparing the answers against the goal. Save `<working-folder>/ai-reader.json`, with `method` set to how the answers were actually produced:

```json
{"method": "fresh_context", "recipient": "...", "batteries": ["core"],
 "answers": [{"number": 1, "battery": "core", "prompt": "Summarize this in three sentences.", "answer": "..."}],
 "survival_check": {"checks": [{"check": "ask", "result": "yes", "document_quote": "...", "ai_quote": "...",
                                "prompt_ids": ["ai-1"], "note": "..."}]}}
```

**If you can't start subagents:** save the same file with `method` set to `not_run`, every `answer` set to null, and `survival_check` null. The report will give the user the prompts to run in a new chat. Never answer the prompts in this conversation; if that happens anyway, set `method` to `same_conversation` so the report says so.
<!-- /skill-only -->
<!-- portable-only -->
You can't start a fresh context here, so don't run the check. In the report, list the recipient's prompts from the applicable batteries and tell the user to paste the document and one prompt at a time into a **new** chat.
<!-- /portable-only -->

## Step 6. Synthesis

Read `synthesis-rubric.md` and apply it: screen findings, merge duplicates, classify, find tradeoffs, and write next steps, including one revision prompt for each likely priority issue. Revision prompts quote the passage, name the reader and the problem, and ask for two or three options rather than a finished rewrite.

<!-- skill-only -->
Scripts do the ranking, coverage, and quality checks, so don't rank. Save `<working-folder>/synthesis.json` with the fields in `$defs/synthesis_output`: `issues` (each with `title`, `quote`, `summary`, `finding_refs` like `"opposing-counsel/2"`, `reasons` per reader, `severity`, `category`, `depends_on_assumptions`, `fix_direction`), `dropped_findings`, `tradeoffs`, `whats_working`, `ai_reader_highlights`, and `next_steps` (`revision_prompts` use the 0-based `issue_index`).
<!-- /skill-only -->
<!-- portable-only -->
Rank the issues yourself using the rubric's weights, and choose up to seven priority actions.
<!-- /portable-only -->

## Step 7. Report

<!-- skill-only -->
Run:

```bash
python <skill-dir>/scripts/finalize.py <working-folder> --platform <claude-code or claude.ai> --model <your model name>
```

If it reports problems, fix the working file it names and run it again. When it succeeds, show the user the summary it prints (also saved as `summary.md`) and point them to `report.html`, a self-contained page that opens in any browser. `report.md` has the same content as plain text. In claude.ai, share `report.html` as a file. Don't retype the report in chat.
<!-- /skill-only -->
<!-- portable-only -->
Write the report in chat, in this order: first the short chat summary (plan line, top three priorities, biggest tradeoff, coverage note, caveat), then the full report (priority actions, tradeoffs, by reader, AI-reader prompts to try, what's working, next steps with revision prompts in code blocks, about this run, and the personas as adapted).
<!-- /portable-only -->
