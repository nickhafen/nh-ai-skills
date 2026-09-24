# M3: Fact-to-element mapping

1. For each PLEADED or ALTERNATIVE claim, copy the elements from its clause file (E1…En) into `matter.elements`.
2. After M5 drafts the paragraphs, fill in `paras` with the paragraph IDs that plead each element.
   - An element with no paragraph is a GAP.
   - Fix a GAP by getting the fact, pleading it on information and belief with a stated basis, or dropping the count.
3. **Verify authority:**
   - Run CourtListener `analyze_citations` on every case you cite anywhere, including in the memo.
   - Run `search_document` to confirm the element language in the key case, and record the pinpoint.
   - Flag caption mismatches.
   - Existence is not the same as good law. List a citator check as a pre-filing step.
4. Run `python3 scripts/validate_matter.py` and fix every error.

**Write:** `elements`, `review_log` entries for citation findings (lens `rules_and_law_currency`), and a `run_log` entry.
