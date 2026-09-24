# M4: Calculations

- Put every amount in `matter.damages`, one row per item.
  - Alternative theories share the same rows through `claims[]`, so no dollar is counted twice (URCP 26(c)(4)).
- Never do arithmetic in prose. Two tools do it for you:
  - `validate_matter.py` recomputes the total and the tier, and flags any dollar figure in the complaint that is not derivable from the table.
  - `build_workpapers.py` writes live formulas.
- Reconcile to `matter.client_stated_total`. Explain every gap in `open_questions`.
- **Interest.** Prejudgment interest runs on amounts that are fixed when due. The legal rate is 10% if no rate is agreed (Utah Code § 15-1-1(2)). The Damages tab computes it from due dates you enter. Amounts with no due date get no interest calculation.
- **Tier.** Set `matter.tier` to the computed tier. Tiers 1 and 2 waive damages above the cap. When the client wants speed and the total is near $50,000, list the tier as a `decisions` item with `gate: "soft"`.

**Write:** `damages`, `matter.tier`, and a `run_log` entry.
