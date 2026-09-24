# Evals: draft-complaint-utah

This folder is a maintainer tool, not part of the skill. It holds three synthetic Utah matters. Each one has seeded "traps": problems a careful lawyer would catch and a careless AI would miss. The evals test whether the skill (M1 chronology through M7 memo) catches them.

```
evals/
  evals.json          # prompts, input files, and assertions (skill-creator format)
  files/case-N/       # run inputs: the ONLY material a run may see
  answer-keys/        # grader-only: correct handling, reasons, and source lines for each trap
  run-evals.js        # optional multi-agent runner: with-skill vs. baseline, then grading
  README.md
```

| Case | Matter | Prompt style | Inputs |
|---|---|---|---|
| 1 | Equipment lease default between two Utah LLCs | Full run, M1-M7 | notes, AI timeline, AI research memo |
| 2 | Unpaid commissions plus an oral profit-share side deal | "Validate this AI timeline, then draft" | notes, AI timeline |
| 3 | Door-to-door roofing job with a fraud flavor | "Chronology and claims chart only; pause for approval" | notes, AI timeline, AI research memo |

All names, entities, vendors ("LegalQuick," "ChronoBrief," "CaseSpark"), addresses, and figures are fictional. Each research memo contains exactly one real Utah case, deliberately miscaptioned. The answer key gives the correct caption, confirmed on CourtListener.

## Running with skill-creator

1. **Load the skill-creator skill** and point it at the skill folder (`draft-complaint-utah/draft-complaint-utah/`) and this `extras/evals/evals.json`.
2. **Set up an iteration workspace** (for example `draft-complaint-utah-workspace/iteration-1/`), with one directory per eval.
3. **Spawn paired runs for each eval in the same batch:**
   - **with_skill:** the eval `prompt`, with the skill available, and the files listed in `files` copied into the run's working directory. Nothing else.
   - **baseline (without_skill):** the same prompt and files, without the skill. For an improvement iteration, use the previous skill version as the baseline instead.
   - Save each run's outputs (complaint, memo, chronology, working papers) to its `outputs/` directory. Record timing and token usage for the benchmark.
4. **Grade** each run against the eval's `assertions`. Give the grader the run outputs, the assertions, and `answer-keys/case-N.md`. Mark each assertion pass or fail with evidence quoted from the output. `trap` assertions test legal judgment. `format` assertions test Utah pleading mechanics (Rule 8(a) caution language, Rule 10(a)(1) tier, Rule 73(e), Rule 19(c), no unverified citations) and process (for example, case 3 must stop before drafting).
5. **Aggregate and review.** Compare pass rates for with_skill and baseline by case and by assertion type. Open the viewer and read the actual outputs, not just the numbers. A pass with thin evidence is a fail waiting to happen. Feed failures back into SKILL.md and the module workflows, then rerun as `iteration-2`.

Run each eval at least 3 times per configuration if you can. Outputs vary, and one lucky catch proves little.

## Why the answer keys stay out of the run context

The answer keys name every trap, the correct numbers, and the source lines. If a run can see them, directly or through a directory listing, it can "catch" traps it would never find on its own, and the eval measures nothing. So:

- Copy **only** `files/case-N/` into a run's working directory. Never mount or reference `evals/`, `answer-keys/`, or `evals.json` in a run.
- The run prompts deliberately say nothing about the traps. Do not add hints when rerunning.
- Only the grader (human or model) gets the answer key.
- Do not describe specific traps in SKILL.md or its references. Teach the general check instead ("reconcile every invoice to its line items"), not "the Dixie invoice is off by $640." Otherwise the skill overfits these three cases.

## Adding a new case

The best traps come from real misses. Whenever the skill (or a human reviewer) misses something on a real matter, turn it into a trap:

1. Write a fictional `files/case-N/` with realistic, messy `client-notes.md` (700-1,200 words, relative dates, client quotes, Utah counties). Add an AI timeline and research memo if the scenario calls for them.
2. Seed 5-7 traps across different types: arithmetic, date conflict, statutory prerequisite or bar, gratuitous benefit, real party in interest, tier boundary, fees, and caption format. Change the facts enough that the case does not resemble a real client matter.
3. Write `answer-keys/case-N.md`. For each trap, give the setup line numbers, the correct handling, why it matters, and the governing rule. Mark anything you have not confirmed against current Utah law as **verify**. Any real case citation must be confirmed on CourtListener, with the true caption recorded.
4. Add the eval to `evals.json` with 8-12 objectively checkable assertions. Log every real-world miss as a new assertion, even on an existing case, so the regression stays covered.
5. Run the case against the current skill and the baseline before relying on it. A trap that no run ever catches may be unfair, and a trap every baseline catches is not testing the skill.

## Legal-accuracy notes (as of September 2026)

- These were checked against the Utah courts' rule text on 2026-09-21: URCP 8(a), 9(c)-(d), 10(a)(1), 19(c), 26(c)(3)-(4), and 73(e).
- These were checked against le.utah.gov: Utah Code §§ 34-27-1, 34-28-9.5, 58-55-604, and 13-11-19. Note that § 58-55-604's current text is marked superseded as of 1/1/2027. Re-verify it and all "verify" items in the answer keys before reusing these evals after the 2027 legislative session.
