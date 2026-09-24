# fresh-eyes-review

A tool that shows a legal drafter how a document's real readers are likely to react before it goes out. It reviews the writing, not the substance: it flags what's missing, unclear, buried, or likely to be misread, never whether the law or facts are correct.

This project lives in the `nh-ai-skills` collection. `fresh-eyes-review/` (next to this file) is the skill itself, the folder users zip and install. `extras/` holds everything that isn't part of the skill.

The full build spec is `extras/docs/build-spec.md`. Its **Build progress** table is the place to track status: update it whenever a phase moves. `extras/docs/decisions.md` records agreed changes to the spec and wins where they disagree. Read both before starting a new phase.

## Where things are

- `fresh-eyes-review/` is the canonical source. Everything substantive lives here once; `extras/portable/` is generated from it and never edited by hand.
  - `references/` holds the content: personas (all in the `_template.md` schema), doc-type map, house settings, persona review format, AI-reader prompts, synthesis rubric, output spec.
  - `assets/results.schema.json` defines `results.json`. Its model-output `$defs` are also sent to the API as structured-output formats, so they must follow the API's schema limits (closed objects, all fields required, nullable via `anyOf`, no min/max).
  - `scripts/quality.py` (stdlib only) does quote verification, ranking, coverage, and run-quality metrics for every environment.
- `extras/engine/` is the pipeline (prompts, model clients, conditions A–E). It reads content from the skill folder; it never duplicates it.
- `extras/eval/` has the harness, scoring, fixtures, dogfood runs, and offline tests. See `extras/eval/README.md`.
- `extras/build/check_personas.py` checks every persona against the schema; `extras/build/build_portable.py` generates the paste-in prompts.

## Checks to run after changes

Run from `extras/`:

```bash
python build/check_personas.py
python eval/tests/test_pipeline.py
python eval/tests/test_skill_scripts.py
python build/build_portable.py --check
python eval/harness.py --fixture eval/fixtures/smoke-demand-letter --client mock
```

## Rules for the build

- Build in phases (see the spec's Build phases table). Finish and verify one before starting the next. Stop where the spec marks attorney review.
- Personas describe the modal reader by role, goal, information, and incentives. No names, backstories, quirks, or demographic attributes.
- Every persona file keeps the "How to read as this persona" stance instruction verbatim.
- Scripts handle anything deterministic (quote verification, overlap metrics, ranking, rendering, portable build).
- Tier-C prompts must never contain privileged background; the tests enforce this.
- Never judge quality from mock-client output.
- No real client documents in the repo. Fixtures are fictional.
- Keep SKILL.md lean; put detail in `references/`.
