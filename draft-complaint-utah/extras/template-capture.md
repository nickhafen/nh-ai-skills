# Updating the skill after a matter (template and clause capture)

This was module M8. It lives outside the skill so that updating the skill stays separate from drafting a complaint. Run it on purpose, after the attorney approves a complaint, not as part of a drafting run. Paths below are relative to this repo folder (`draft-complaint-utah/`).

- Compare the approved complaint with `draft-complaint-utah/assets/template-matter.json`. Propose updates to the template (only generic structure, never client facts) and to the clause files in `draft-complaint-utah/references/clauses/` (better element paragraphs, new defenses, new verification-log rows).
- Add any miss discovered on the matter to `draft-complaint-utah/references/common-misses.md`, and add a matching check to `draft-complaint-utah/scripts/validate_matter.py`. Then add an eval assertion (see `extras/evals/README.md`).
- Changes to the clause library, the rules manifest, or the template are proposals that a human approves.
