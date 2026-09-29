# scholarly-draft-review

A skill that gives stage-appropriate reader feedback on legal scholarship drafts (articles, essays, job-talk papers, notes, comments, seminar papers) and suggests which real people to ask next. It's written for authors, and it treats every author as a scholar. It's the scholarship sibling of `../fresh-eyes-review/` and reuses its architecture: persona files, a selection map, single-conversation reviews, a fresh-context AI check, a synthesis rubric, and script-built `results.json` and reports.

`scholarly-draft-review/` (next to this file) is the skill itself, the folder users zip and install. `extras/` holds everything that isn't part of the skill. Agreed design changes go in `extras/docs/decisions.md`, newest first.

## Where things are

- `scholarly-draft-review/references/`: personas (all in the `_template.md` schema), `stage-map.md` (stages, default readers, swaps, real-reader suggestions), house settings, reader review format, cold-read prompts, synthesis rubric, output spec.
- `scholarly-draft-review/assets/results.schema.json` is **generated** by `extras/build/build_schema.py`. Edit the builder, not the JSON.
- `scholarly-draft-review/scripts/quality.py` (stdlib only): section splitting (law-review headings), the key-sentence outline, quote verification, ranking with now/later timing, coverage, run-quality metrics.
- `extras/portable/single-prompt.md` is **generated** by `extras/build/build_portable.py` from SKILL.md's `skill-only` / `portable-only` markers plus the reference files.
- `extras/fixtures/`: fictional drafts with seeded issues. `extras/examples/`: a full working folder and report from a run on the workshop fixture; the tests use it as their base case.

## Checks to run after changes

Run from `extras/`:

```bash
python build/check_personas.py
python build/build_schema.py --check
python build/build_portable.py --check
python tests/test_scripts.py
```

If you change a working-file format, rerun `finalize.py` on `extras/examples/workshop-article` so the example report stays current.

## Rules

- **Feedback only.** Nothing in the skill drafts or rewrites the author's text. Each issue gets a one-line direction, never a rewritten passage or a prompt to draft with.
- **Not a cite-check, but experts engage the literature.** Readers never rule on whether the law or sources are described correctly. Expert readers may judge novelty and name related work, but every specific work goes through the named-work check (SKILL.md step 5): verified works are linked, works not found are dropped, and without a search tool they're labeled "not checked." A "not new" finding needs a verified or already-cited work (synthesis rule `unverified_source`). `finalize.py` defaults any unlisted specific work to `not_checked`, never `verified`.
- **Written for authors, and every author is a scholar.** Nothing in the skill takes a grader's view (no assignment requirements, no grading). Author status never changes the readers, severity, or tone; only the stage and where the piece is headed do.
- **Limitations are always disclosed.** `quality.STANDING_LIMITATIONS` plus run-specific items appear under "Before you rely on this" at the top of the chat summary, `report.md`, and the HTML overview. The standing texts must match "Limitations to disclose" in `synthesis-rubric.md`; a test checks this.
- **No reader sees the intended claim.** Briefed readers get the author's note; cold readers get only what a real reader in that role would see.
- **Stage drives everything:** reader choice, what counts as "now" versus "later," and the real-reader plan. User guidance overrides inference.
- Personas describe the typical reader by role, goal, knowledge, and incentives. No names, backstories, quirks, or demographic attributes. Every persona keeps the stance instruction verbatim from `_template.md` (the checker enforces it).
- Scripts handle anything deterministic. Keep SKILL.md lean; put detail in `references/`.
- Fixtures are fictional. No real unpublished drafts in the repo.
- Install must stay "zip the inner folder." No build step on the install path.
