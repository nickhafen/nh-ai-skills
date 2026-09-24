# Decisions log

Changes to the build spec agreed during the build. Where this file and the spec disagree, this file wins. Newest first.

Entries before the move into `nh-ai-skills` (2026-09-24) use the old standalone layout: `skill/fresh-eyes-review/` is now `fresh-eyes-review/`, and `engine/`, `eval/`, `build/`, `portable/`, and `docs/` are now under `extras/`.

## 2026-09-24 — Dogfood round 2 (user's claude.ai run on a draft complaint)

The user ran the skill on claude.ai (Opus 5.5) on a draft complaint. The document stays out of the repo. Changes:

- **Drafts with placeholders:** readers review the finished version, not the brackets. Findings that only point out placeholders or notes to the author are dropped (synthesis screening rule 5); a placeholder holding an unmade choice readers would notice (e.g., `[and/or]`) is still fair game. The skill notes in the plan when a document is a draft.
- **Look-for checks can be "not applicable"** when the document type doesn't call for them (the trial judge persona marked "response to the other side's argument" missing on a complaint). Schema enum extended.
- **Coverage gaps skip sections under 25 words** (was 10). Captions, attorney blocks, and jury demands were showing up as gaps.
- **The AI-reader check records how it ran:** `method` is `fresh_context`, `same_conversation`, or `not_run`, and the report warns when answers came from the same conversation. The claude.ai run had all nine answers filled in, although claude.ai normally can't start subagents, and nothing recorded how they were produced.
- **Repo:** the project moves into the user's private `nh-ai-skills` collection, following its layout (`fresh-eyes-review/fresh-eyes-review/` is the skill; `fresh-eyes-review/extras/` holds everything else). The build spec moves to `extras/docs/build-spec.md`.

## 2026-09-24 — Dogfood round 1 feedback

**Judge each document against its purpose.** A client persona reviewing a letter sent on the client's behalf asked for its own collection costs and net recovery, which belong in advice to the client, not in a demand letter. Fixed in three places: a "Judge the document against its purpose" section in `persona-review-format.md`, a scoping note in each client persona's out-of-scope section (a small edit to attorney-reviewed files), and synthesis screening rule 4, which drops findings that ask a document to do another document's job.

**HTML report moved into the MVP** (was the first post-MVP add-on). The markdown report alone was overwhelming. `report.html` is self-contained and organized as tabs (Overview, Priorities, Readers, AI reader, Next steps, Method); `report.md` is still written as a plain-text fallback. With no embedded results, the same template is a viewer for any `results.json`.

## 2026-09-24 — MVP plan

**Ship an MVP first:** a zero-config skill (fast mode) plus a paste-in prompt. Steps M1–M4 in the spec's progress table. Deferred until after the MVP: full validation, HTML report, hosted viewer, docx memo, guided mode, isolated persona subagents, Gem/Project packaging, CI.

- **Single-conversation persona reviews** everywhere for the MVP (the portable versions need this anyway). Tier routing is done by instruction, as in condition B.
- **AI-reader check runs only in a real fresh context.** In Claude Code, one subagent per prompt. Where the skill can't start a fresh context (claude.ai, portable versions), it doesn't simulate the check in the same conversation; it gives the recipient's prompts to copy into a new chat.
- **Markdown report for the MVP**, rendered by script from `results.json` in skill environments and written directly by the model in portable versions. HTML report is the first add-on.
- **Default three personas** (primary readers first) to keep usage down; users can ask for more. One full review was ~15–20% of a Pro usage window at four personas.
- **Skill working files:** the skill writes each piece (setup, one file per review, AI-reader answers, synthesis) to a working folder, and `scripts/finalize.py` assembles `results.json`, fills persona text from the library, ranks, computes quality, validates, and renders the report. This keeps the model from copying persona files into JSON and makes each piece checkable.
- **Schema change:** AI-reader `answer` is nullable, so a run that hands the prompts to the user still records which prompts apply.

## 2026-09-22 — Phase 1 live run and usage

**Validation runs through the Claude Code CLI on the user's own plan** (`--client claude-code`), not the API. No API key; calls count against plan limits. The client passes `--disable-slash-commands` (the skills listing otherwise adds ~16.7k tokens to every call) and `--strict-mcp-config`, runs outside the repo, and resumes CLI sessions so conditions A and B are real multi-turn conversations.

**Measured usage (smoke fixture, conditions B + C, one run each, Opus 5, effort high):** 15 calls, 14.5 minutes, ~$3.62 API-equivalent, Pro plan meter 3% → 35% (includes some usage by the concurrent desktop session). Roughly $0.11 API-equivalent per 1% of a Pro window. Synthesis is over half the cost (~$1 and ~4 min per condition). At this rate the spec's full Phase 3 design (~100 condition runs, ~$180) would take ~16 Pro windows; a leaner design is needed (decided at the start of Phase 3).

**Coverage gaps skip sections under 10 words** (salutations, signature blocks), which otherwise showed up as noise.

## 2026-09-22 — Phase 0 sign-off and Phase 1 design

**Phase 0 complete.** Attorney review signed off; all 16 personas marked `attorney-reviewed`.

**Four seeded fixtures** in Phase 2 (demand letter, client letter, motion, short commercial services agreement), not three.

**`output-spec.md` and the `results.json` schema are Phase 1.**

**Web app direction.** Built for practitioners and also used by students learning to write like practitioners. Subscription model. Must meet the confidentiality, data, and privacy expectations firms apply to vendors. See the README roadmap for the approach (hosted models on a cloud platform, no stored documents by default, outsourced auth/payments/compliance tooling).

**Phase 1 design choices:**
- **Schema location:** `skill/fresh-eyes-review/assets/results.schema.json` (the skill must be self-contained). Its `$defs` for model-produced objects double as structured-output formats for API calls, so they follow the API's schema limits (every object closed, every field required, nullable fields as `anyOf` with null, no numeric or length limits). Caps like "at most 5 findings" are enforced by prompt and checked by script.
- **Division of labor:** the model screens, merges, and classifies; scripts (`scripts/quality.py`) score and rank issues with the rubric weights, compute attention and review gaps, verify quotes, and compute run quality. The same script serves the skill, the harness, and a future web app.
- **Engine package** (`engine/`) at the repo root holds the pipeline; it reads all content from the skill folder and never duplicates it. `results.json` is the only contract between the engine and any interface.
- **Harness defaults:** model `claude-opus-5`, effort `high`, adaptive thinking, streaming, and the server-side refusal fallback (`fallbacks: "default"`) on by default (`--no-fallbacks` to disable). The AI-reader check runs once per run index and is shared across conditions, so conditions differ only in the persona reviews. Condition E uses the same output schema with no persona file.
- **Background routing:** tier A sees everything; tier B sees `client_known` and `public`; tier C sees `public` only. Unlabeled background is privileged. The author's goal goes to tier A personas only in isolated runs.
- **Mock client** for offline end-to-end checks; its output is never used to judge quality. Mock batches are git-ignored.

## 2026-09-22 — Phase 0 review, round 1

**Scope: writing, not substance.** Personas react to the writing (what is clear, buried, missing, inconsistent, or likely to be misread, and how the tone lands), not to whether the law, facts, or citations are correct. Example: flag that no standard of review is stated; don't judge whether the stated standard is correct. Enforced in the persona stance instruction, `persona-review-format.md`, and synthesis screening rule 3. The README says this up front.

**Persona schema simplified.** "What they scan for" (5) and "Review questions" (11) were near-duplicates. Merged into one section, **5. What they look for**: 4–7 writing-level checks, each marked clear / unclear or buried / missing in the review. "Out of scope" is now section 11.

**Renamed** `supervising-partner` → `senior-colleague`, covering a supervisor, a trusted peer, or the head of a legal department, so the tool is useful to senior lawyers with no one above them.

**Cut** `diligence-reviewer`. It read for substantive issues (change-of-control clauses, uncapped liabilities), which is outside the writing-review scope and overlaps the contract-review plugin. The clarity checks it would have made (ambiguity, inconsistent terms) are covered by `future-interpreting-court`. Library is now 16 personas.

**Appellate judge:** removed the intermediate-vs-highest-court parameter. How far the rule would reach is now something every appellate judge looks for.

**Not just law firms.** Personas refer to "the author's side," not "the author's client." A new `house-settings.md` sets the author's role (outside counsel, in-house, government, legal aid, law student) and changes who "own client" means. The README explains one-time customization.

**Legal terms of art.** Personas who may not understand them say so in section 3 (individual client, business decision-maker, unrepresented party, counterparty, implementer, public/press).

**Reader selection simplified.** Replaced the "downstream reader" mechanism: each doc type lists primary readers (who read and act now) and secondary readers (later or indirect). Primary readers fill slots first; empty slots go to secondary readers.

**Coverage.** Real readers skim, and personas report that honestly, but the run must still evaluate every part. Each persona reads the whole document and returns an attention map. Synthesis reports:
- *attention gaps* (sections every reader would skim), which are findings for the author
- *review gaps* (sections no persona read closely or commented on), which are disclosed in run quality with a suggested reader.
The doc-type map marks entries whose defaults include no close reader (client letter, confidential mediation statement, deal memo).

**Next steps in the output.** Synthesis now ends with next steps: copyable revision prompts per priority action (asking for options, not a finished rewrite), assumptions to confirm, follow-up reviews, and suggestions for real review.

**Flagged for Phase 3 roster tests** (in addition to the spec's clerk vs. trial judge):
- `future-interpreting-court` vs. `trial-judge`: possible duplicate; the difference is posture (ruling now vs. interpreting later)
- `mediator` vs. judge personas: possibly unnecessary; the expected difference is that mediators reward candor about weak points and judges reward confident advocacy

**Web app on the roadmap** (README). Implication for the build now: keep content in plain files and make `results.json` the only contract between the pipeline and any interface, so a web app can reuse both.

## 2026-09-22 — Phase 0 draft

- Mediation statement added to the doc-type map so the mediator persona has a home.
- Persona files carry YAML front matter (`id`, `name`, `tier`, `typical_documents`, `status`).
- Ranking weights in the synthesis rubric are a starting point, subject to Phase 3.
- AI-reader survival check: "no" → high severity, "partly" → medium.
