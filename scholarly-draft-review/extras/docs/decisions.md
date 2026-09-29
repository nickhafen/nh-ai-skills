# Decisions log

Design choices for scholarly-draft-review, newest first.

## 2026-09-29 — Leaner reports: one issue list; no tradeoffs or feedback plan

The reports had grown sections that repeated each other or asked the author to weigh more than they could act on. In both `report.html` and `report.md`:

- **"Before you rely on this" is the whole front matter,** in a collapsible block that starts open. The stage, claim, and plan line moved out; run context and assumptions are in Method. The duplicate limitations list in Method is gone.
- **One numbered issue list.** Now and Later (in HTML), and "other issues" and "park for later" (in Markdown), merge into one list: priority actions first, then every other issue by rank. Severity tags convey priority. The severity/reader filters, the "several readers" tag, and the stage-focus sentence are removed.
- **Removed from the reports:** tradeoffs, "who to ask next" with its listening note, the stage ladder, and the related-work section. Named works still appear under the reader who named them, with their check status.
- **Reader details** show each reader's fuller finding text, without the one-line reason, the quote, or the finding number.

The chat summary drops the biggest tradeoff and who to ask next too, and the skill's description no longer promises who to ask next. The "Verify before you act" limitation no longer points to the feedback plan. Asking only who should read a draft still gets the stage, the readers, and real readers to suggest (SKILL.md, before step 1).

## 2026-09-29 — Simplified for authors: no cold read, next actions, attention maps, or next-steps tab

The skill carried over tooling from fresh-eyes-review that serves a practitioner's document or that project's validation work, not an author revising scholarship. Removed:

- **Cold-read check** (fresh-context AI summaries plus a claim check). Whether the claim comes through is already tested by comparing each reader's "what I think it argues" with the author's claim (`claim_mismatch`) and by the key-sentence outline. Dropping it also removes the only step that needed subagents, the `cold_read` and `prompts` blocks, and `cold-read-prompts.md`.
- **Likely next action** in reviews and section 9 of the personas. Next actions matter when a reader will do something with a document (rule, respond, sign); here they added little.
- **Attention maps and "attention budget"** (read closely / skimmed / skipped, what they'd miss), and with them attention and review gaps. Every reader now reads the whole draft in good faith and may flag, in a finding, where it was hard to get through. The personas' reading instruction and friction bullets were reworded to match.
- **Next steps tab.** The feedback plan and related work moved to the Overview; revision questions were dropped because each issue already has a one-line direction; assumptions to confirm and follow-up reviews were dropped because the limitations and plan line cover them.
- **Validation-era metrics:** reader distinctiveness, stance spread, assumption load, coverage, leaks, `depends_on_assumptions` and its ranking factor, per-finding confidence, and reader-specific groupings.
- **The draft's text in results and reports.** `results.json`, `report.md`, and `report.html` refer to the draft by filename (`source.json`, written by `prepare.py`) and the working copy `document.md`. Quote checks and ranking read `document.md` directly. Reports can now be shared without the draft.

Personas now have nine sections (1–5 unchanged; 6 friction points, 7 trust, 8 adaptable parameters, 9 out of scope). Schema version 0.2.

Also removed in the same pass: the **gut reaction** in reviews, and **look-ahead readers** (the `stage`/`look_ahead` role, the personas' `stages` field, and the ranking bonus for readers the stage calls for). A reader the user picks is simply a reader; the stage table sorts every finding into now or later.

## 2026-09-29 — Written for authors; faculty advisor removed; limitations always disclosed; examples folder

**Written for authors, and every author is a scholar.** Like draft-complaint-utah, which is written for practitioners and is valuable to students for that reason, this skill is written for scholars. Nothing takes a grader's view.
- `faculty-advisor` is removed. It existed to check assignment requirements, which scholars aren't evaluated on. Its two checks that apply to any scholarship moved to `generalist-law-colleague`: a claim someone could dispute (not a topic or a description of the law), and the author's own argument carrying the piece rather than a survey. Six personas remain.
- Removed: the supervised/graded swap, the `supervised` and `assignment` fields, the write-on/graded-work question at intake, and "grading" in the stage definitions. A mentor's comments are handled by the revising-after-feedback swap (`field-expert` adapted as a mentor, or a custom reader).
- The one-standard rule stays as a guard: a student note or seminar paper is held to the standard of published scholarship.

**Limitations are always disclosed.** Users may never open the reference files, so every chat summary and report opens with "Before you rely on this": six standing limitations (simulated readers; AI errors including about sources; novelty views are leads; not a cite-check; verify before acting; the draft went to an AI service) plus run-specific ones (inferred claim or stage, unchecked named works, cold read not run or contaminated, quotes not found, parts no reader read closely). Replaces `quality.caveats` with `quality.limitations`. The standing text lives in `quality.py` and in "Limitations to disclose" in `synthesis-rubric.md` (for the paste-in version); a test keeps them in sync.

**`dogfood/` renamed `examples/`** (`extras/examples/workshop-article/`), the common repo convention for sample output.

## 2026-09-29 — Named works checked, not banned; one standard for every author; shorter description

**Experts may judge novelty and name related work.** Replaces the ban on naming works the draft doesn't cite (and the rule `invented_source`). The ban guarded against fabricated or misattributed citations, but it also removed what real experts are most useful for, including what Gray asks Capital-E Experts for (major problems, citations, venues). Safeguards now:
- Readers put every pointer in a `related_work` list (`work`, `specific`, `why`, `confidence`) and name a specific work only when confident it exists; otherwise they describe the kind of work.
- New step 5, the named-work check: each specific work is marked `cited_in_draft`, looked up and marked `verified` (with a link) or `not_found`, or marked `not_checked` when no search tool is available. Never verified from memory. `finalize.py` fills in any unlisted specific work as `not_checked`.
- Reports link verified works, label unchecked ones "confirm it exists before relying on it," and leave out works not found (listed in the Method tab).
- Synthesis rule `unverified_source`: findings resting on a `not_found` work are dropped or rewritten; a "not new" finding needs a `verified` or `cited_in_draft` work, or it becomes a question for a search.
- Still not a cite-check: no reader rules on whether the law or sources are described correctly; experts may flag a characterization to double-check.
- The standing caveat now says the model's knowledge of the literature is incomplete and out of date, so novelty views and reading lists are leads.

**One standard for every author** (the faculty-advisor swap described here was later removed; see the entry above). Students' drafts get the same readers, severity, and tone as faculty drafts at the same stage. Removed: the separate student column in the stage map (which left out the field expert for students at the full-draft and workshop stages), the author-type field in the schema and setup (replaced by `supervised`), and the status-based house setting. Supervised or graded work *adds* `faculty-advisor` to check requirements; a student journal's notes editor stands in for the articles editor at submission, the same place the articles editor sits for everyone. The advisor persona now states that it applies the standard of published scholarship, and all review guidance forbids softening by status.

**Description cut from 960 to 431 characters**, keeping only what triggers the skill.

## 2026-09-29 — Initial build

**Scope.** A sibling of fresh-eyes-review for legal scholarship: faculty articles and essays, and student seminar papers, notes, and comments, at any stage of drafting. Same architecture (personas, a selection map, single-conversation reviews, a fresh-context AI check, synthesis rubric, script-built results and reports), adapted as below.

**Stage is the organizing idea.** Five stages (`idea`, `early`, `full`, `workshop`, `submission`). The stage decides the readers, what feedback counts as "now" versus "later," and the real-reader plan. The skill infers the stage from signals in the draft (placeholders, footnote completeness, whether every Part is drafted) and states the basis; anything the user says overrides it. Mixed signals resolve to the earlier stage. "Revising after feedback" is a swap, not a stage.

**Reader sequence follows Tara Gray.** Nonexperts early, little-e experts (law-trained, outside the specialty) in the middle, Capital-E Experts (specialists) late, with law-specific additions: the articles editor as a gatekeeper at submission only, and the faculty advisor at every stage for students (superseded: see the entry above). Faculty early-stage runs use two readers on purpose.

**Seven personas:** smart outsider, law colleague outside the subfield, field expert, skeptical expert, articles editor, faculty advisor, judge or practitioner. Each carries `reader_type`, `briefing` (briefed or cold), and `stages` in front matter. A reader chosen for a draft earlier than its first stage is a `look_ahead` reader, and its findings default to "later."

**No reader sees the intended claim.** Readers report what they think the draft argues; the synthesis compares that to the claim (category `claim_mismatch`). The author's note (stage, feedback wanted, known gaps, prior feedback, assignment) goes only to briefed readers.

**Feedback only, and no rewrite prompts.** fresh-eyes-review offers revision prompts that ask an AI for options. This skill replaces them with revision questions the author answers, because the user asked for no drafting and because student work is often graded or subject to competition rules.

**No invented sources** (superseded by the named-work check above). Simulated experts could say what kind of work a draft should engage but never name a work, author, or case the draft doesn't cite, and novelty was never decided.

**Now and later.** Every issue is marked `now` or `later` by the stage map. Only `now` issues can be priority actions; `later` issues are listed so they aren't lost. Anything that would sink the piece is always `now`.

**Two checks that aren't readers.**
- *Key-sentence check* (Gray's after-the-fact outline): `prepare.py` extracts each body paragraph's first sentence, skipping front matter before an Introduction heading, headings, lists, block quotes, and footnotes, with legal-citation abbreviations handled. The model judges whether the outline tells the argument and flags up to five paragraphs.
- *Cold-read check*: the fresh-context AI check from fresh-eyes-review, retargeted to "does the claim come through?" (claim, contribution, stakes, structure, prescription).

**Real-reader feedback plan** in every report: two to four kinds of real readers, when to ask, and what to ask, plus Gray's advice on listening to feedback.

**Word support.** `prepare.py` keeps Word heading styles as markdown headings and Word footnotes as `[^n]` markers with the notes under "## Footnotes," since footnotes matter to several readers. Quote matching ignores footnote markers.

**Schema is generated** from `extras/build/build_schema.py` rather than hand-maintained. Run metadata is slimmer than fresh-eyes-review's (no harness conditions or token usage), since there's no engine or eval harness yet.

## Open questions

- Faculty review of the seven personas (all `status: draft`).
- Whether two readers is enough for faculty early-stage runs, or a third (a mentor-style field expert) is worth the cost.
- Whether the key-sentence check should run on shorter pieces (essays, student notes under eight paragraphs).
- Live runs on real drafts at each stage, then an eval with seeded fixtures like fresh-eyes-review's.
