# Tool routing

| Task | Prefer | Why / caution |
|---|---|---|
| Authority discovery; jurisdiction-specific elements | Westlaw/CoCounsel, Lexis+ AI/Protégé, vLex/Vincent, Harvey | Curated databases and citators. Their memos are leads: Stanford RegLab (Magesh et al., J. Empirical Legal Stud. 2025) found roughly 17–33% hallucinated or misgrounded answers. |
| Reconciling many inputs; structured work product; drafting; review | Claude with this skill | Long-context synthesis, code for numbers, file generation |
| Math, dates, tier, interest | `scripts/` (code) | Deterministic |
| Case existence | CourtListener MCP (`analyze_citations`, then `search_document` for the pinpoint) | Existence is not the same as good law. Use a citator before filing. |
| Rule and statute currency | The attorney, against official sources (utcourts.gov, le.utah.gov) | Out of scope for this skill; `references/rules/manifest.json` records when the pack was last verified |
| Independent critique | Fresh subagent or a second vendor | Errors that are independent are less likely to coincide |

Put confidential client facts only into tools approved in the profile (`approved_tools`).
