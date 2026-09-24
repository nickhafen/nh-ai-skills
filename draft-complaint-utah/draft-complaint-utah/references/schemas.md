# matter.json: the contract between modules

Every module reads and writes one file, `<Case> - matter.json`. The scripts depend on it, so modules never pass work to each other in prose alone. See `assets/sample-matter.json` for a complete, valid example. (It is synthetic and shows format, not drafting quality.)

| Key | Written by | Shape (required fields in **bold**) |
|---|---|---|
| `matter` | M0 | **name**, **court**{judicial_district, county}, **tier**, case_no, judge, client_stated_total, as_of_date |
| `parties` | M0/M1 | **plaintiffs**[], **defendants**[]: {**id**, **name**, **caption_desc**, short} |
| `chronology` | M1 | [{**id**, **date** (ISO, or `[[...]]` if assumed), date_basis, **event**, **source**, ai_comparison, paras[], flag}] |
| `claims` | M2 | [{**id**, clause_id, **title**, by[], against[], **decision** ∈ PLEADED/ALTERNATIVE/OMITTED/NEXT STEP/USER DECISION POINT, alt_to[], suggested_by, **rationale**, authority, risk}] |
| `elements` | M3 | [{**claim**, **element**, authority, **paras**[] (paragraph ids), note}] |
| `damages` | M4 | [{**id**, **item**, plaintiff, **amount**, due_date, claims[], alternative_group}]. Each dollar appears once (no duplication). |
| `context_amounts` | M4 | [numbers]: non-damages dollar figures that the complaint mentions on purpose (e.g., a partial payment already received) |
| `complaint` | M5 | intro, sections[{heading, paragraphs[{**id**, **text**, items[], subheading}]}], attorney_fees?, rule19c?, counts[{**claim_id**, **title**, sub, paragraphs[{id, text, elements[]}]}], **prayer**[], jury_demand, year, filed_for |
| `review_log` | M6 | [{**lens** ∈ judge/opposing_counsel/client/rules_and_law_currency/math_and_consistency, **finding**, action, **status**, reviewer ("inline" or "agent:<id>" or "workflow:<run id>")}] |
| `decisions` | all | [{**decision**, **chosen**, alternative, **why**, gate ∈ hard/soft/flag}] |
| `open_questions` | all | [{**priority**, **question**, who, affects}] |
| `run_log` | all | [{**module**, **mode** ∈ GENERATE/VALIDATE/MERGE/SKIP, inputs, tool, timestamp, notes}] |

Text conventions: `[[...]]` marks an unconfirmed fact or a fill-in (it renders in yellow). `{{ref:id}}` renders a paragraph number, and `{{range:a:b}}` renders "N through M". Never type paragraph numbers by hand.
