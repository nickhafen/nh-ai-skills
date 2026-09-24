# M2: Claim selection

1. **Collect the candidate claims.**
   - MERGE: every claim any supplied memo suggested.
   - GENERATE: research with the best available legal platform. Web search only produces leads.
   - Always consult `references/clauses/README.md` for claims the facts support that no one suggested.
2. **Screen each candidate** against `references/common-misses.md`: prerequisites, bars, party issues.
3. **Assign a decision to each claim:** PLEADED / ALTERNATIVE / OMITTED / NEXT STEP / USER DECISION POINT.
   - Use the profile's `claim_posture`: `core+alternatives` (the default), `maximal`, or `lean`.
   - Strategic calls get the default decision plus a `decisions` entry with `gate: "soft"`. Strategic calls include a marginal claim, fraud, punitive damages, jury, the tier, and a gratuitous-benefit item.
   - Never drop a suggested claim silently. An OMITTED claim needs a `rationale`, and `validate_matter.py` enforces this.
4. **Record authority** by clause ID. Record where the research tools disagree; each disagreement marks a judgment call.
5. **Soft gate:** if `checkpoint_mode` is `pause` and `M2` is in `pause_points`, show the claims chart (from `build_workpapers.py`, or as a table) and wait for approval.

**Write:** `claims`, `decisions`, `open_questions`, and a `run_log` entry.
