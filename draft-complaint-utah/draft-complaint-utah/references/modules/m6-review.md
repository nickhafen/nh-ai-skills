# M6: Multi-perspective review

Run each lens as its own pass, and log every finding in `review_log` with `{lens, finding, action, status, reviewer}`.

| Lens | Focus |
|---|---|
| judge | rules compliance (use `references/rules/urcp-complaint-checklist.md` item by item), ripeness, shotgun pleading, clarity, prayer matches counts |
| opposing_counsel | motion-to-dismiss targets, overstatement, admissions, missing prerequisites (common-misses), inconsistent facts, weak "information and belief" allegations |
| client | does it seek everything the client expects? Explain each gap. Does it serve the client's stated goal (speed, cost, leverage)? |
| rules_and_law_currency | case existence and pinpoints; obvious renumbering or supersession noted in the pack. This is a sanity check, not a substitute for the attorney's own currency check. |
| math_and_consistency | output of `validate_matter.py`; defined terms; cross-references |

**Independence rule.** If `review.fresh_agent_adversarial_review` is true, the opposing_counsel lens MUST run in a fresh subagent (Agent tool) or a workflow agent.
- Give that agent only the rendered complaint text, the rules checklist, and `common-misses.md`. Do not give it your reasoning, the memo, or the claims rationale.
- Record `reviewer: "agent:<agentId>"` (or `"workflow:<runId>"`) on each finding it produced. `validate_matter.py` warns when this evidence is missing.
- If spawning agents is not permitted in the current environment, run the lens inline. Record `reviewer: "inline"` and disclose it in the memo. Never claim independence you didn't get.

After fixes, re-render the complaint and re-run `validate_matter.py`.

**Write:** `review_log` and a `run_log` entry.
