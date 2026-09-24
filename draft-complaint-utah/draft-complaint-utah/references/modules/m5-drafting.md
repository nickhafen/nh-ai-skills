# M5: Drafting

**Start from `assets/template-matter.json`** (its rendered version is `assets/complaint-template.docx`), and fill `matter.complaint` in the same structure.

**Build order:**
1. Parties
2. Jurisdiction and venue
3. General allegations: chronological, one fact per paragraph, defined terms, subheadings by transaction
4. Optional sections: Rule 19(c) and attorney fees
5. Counts
6. Prayer
7. Jury demand, per the profile

**Counts:**
- Adapt the element-tagged template paragraphs from `references/clauses/<ID>.md`.
- Each count incorporates only the general allegations (`{{last_general}}`, which the renderer handles automatically).
- Label alternative counts as pleaded under Rule 8(e).

**Paragraph IDs and references:**
- Every paragraph gets a stable `id`.
- Cross-references use `{{ref:id}}`. Never type a number by hand.

**Style:**
- Plain English. No "COMES NOW."
- Put unconfirmed items in `[[brackets]]`.
- Plead facts, not law. Cite case law only if the profile allows it (`cite_case_law_in_complaint`).

**Render and check:**
- Render with `node scripts/render_complaint.js matter.json "<Case> - Draft Complaint.docx"`. This also writes `.paranums.json`.
- The renderer places the bold caution language at top right, the filer block at top left, and the tier in the caption, and applies URCP 10(d) formatting.
- Convert to PDF and look at page 1 and the last page before handing off.

**Write:** `complaint`, then fill `elements[].paras`, then add a `run_log` entry.
