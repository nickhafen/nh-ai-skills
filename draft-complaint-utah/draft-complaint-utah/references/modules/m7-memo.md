# M7: Memo and handoff

**Memo sections, in order:**
1. **Bottom line.** Is the draft ready? List the blockers first.
2. **What was done.** A module table: module, mode, inputs, output. Take it from `run_log`.
3. **Judgment calls.** A table of decision, chosen, alternative, why. Take it from `decisions`. Mark each item as soft or flag.
4. **Problems found in the inputs.** For example, outside-tool errors and disagreements.
5. **Open questions.** Prioritized. The full list is in the workpapers.
6. **Next steps.** Cover sheet, summons, service, provisional remedies, preservation letter, early resolution.
7. **Verification performed and its limits.** Include the `review_log` reviewer types, which states honestly whether the adversarial review ran in an independent agent.

**Build the files:**
- Workpapers: `python3 scripts/build_workpapers.py matter.json "<Case> - Draft Complaint.paranums.json" "<Case> - Working Papers.xlsx"`
- Memo: build as .docx with the docx skill. Keep it to about 4 pages.

**Final check:** `validate_matter.py` must exit 0 (warnings allowed if disclosed in the memo).

**Delivery:** save to the profile's output folder next to the inputs, and never overwrite the sources.

**Hard gate:** nothing is filed or sent without attorney sign-off.
