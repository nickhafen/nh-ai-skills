# Evaluation harness

Runs fixtures through the pipeline under the validation conditions and scores the results. See the Validation plan in the build spec for why.

| Condition | Setup |
| --- | --- |
| A | Single context, personas in sequence, no information-restriction instructions |
| B | Single context, personas in sequence, explicit "this reader does not know X" (the portable-version setup) |
| C | Isolated: one fresh context per persona, background routed by access tier |
| D | Isolated, every persona gets the full background |
| E | Baseline: one generic senior-lawyer review, no persona |

Commands below run from the `extras/` folder.

## Setup

```bash
pip install -r requirements.txt
```

Real runs need Claude API credentials: `ANTHROPIC_API_KEY` in the environment, or `ant auth login`.

## Run

```bash
python eval/harness.py --fixture eval/fixtures/smoke-demand-letter --client mock
```

`--client mock` tests every code path offline. Its reviews are meaningless, so never read quality into mock scores. Drop the flag for a real run (default model `claude-opus-5`, effort `high`). Useful flags: `--conditions B C`, `--runs 5`, `--no-ai-reader`, `--effort medium`.

The AI-reader check doesn't depend on the condition, so each run index runs it once and shares it across conditions.

## Score

```bash
python eval/score.py eval/results/smoke-demand-letter/<batch>
```

This writes `scores.json` per run and `summary.md` per batch (mean ± sd by condition). Add `--grader anthropic` to recheck string-match misses with a model and to grade main-point agreement.

Human-judged metrics (precision, blind usefulness) aren't automated. `scores.json` lists `unmatched_findings` for a human to judge.

## Tests

```bash
python eval/tests/test_pipeline.py
```

These run offline. They check tier routing (a tier-C prompt must never contain privileged background), schema validity for every condition, quote matching, answer-key matching, leakage detection, and ranking weights.

## Fixtures

Each folder in `fixtures/` has `fixture.json` (document settings, background with sensitivity labels, personas and adaptations, AI-reader recipient and batteries), the document, and `answer_key.json`.

Answer-key issue types: `convergent`, `persona-specific`, `curse-of-knowledge`, `leakage-probe`, `decoy`. Each issue has an anchor quote and keywords. `match` sets how a finding counts as catching the issue:

- `anchor`: the finding quotes the anchor passage
- `keywords`: the finding's text uses a keyword
- `anchor+keywords`: both

`smoke-demand-letter` is a small fixture for pipeline checks only. The four seeded validation fixtures come in Phase 2.
