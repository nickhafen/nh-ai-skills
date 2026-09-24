# Common misses checklist (run in M2, re-check in M6)

*Out of scope: conflicts clearance and limitations analysis. The attorney handles both outside this workflow.*

AI research tools answer the question you ask. They rarely raise a prerequisite or bar you didn't ask about. Before claims are final, work through every line below. Record each hit in `decisions`, `open_questions`, or `review_log`. When a real miss is found in practice, add it here and add a check to `scripts/validate_matter.py`.

## Standing and parties
- [ ] **Real party in interest (URCP 17(a)).** Did the individual or the entity perform, pay, or own the claim? Look at whose account paid and whose name is on the invoices.
- [ ] **Exact legal names and entity types** (check the Utah Division of Corporations). Is the entity active? Who is the registered agent?
- [ ] **Needed persons not joined (URCP 19(c)).** If there are any, name them and say why they are not joined.
- [ ] **Contracting capacity.** Did the defendant act individually or for an entity? Plead in the alternative if unclear.

## Statutory prerequisites and bars
- [ ] **Contractor licensure (Utah Code § 58-55-604).** A contractor must allege and prove it was appropriately licensed when the contract was made and when the claim arose. Check every trade billed (electrical and plumbing need their own licenses). Note: the section is scheduled to be superseded on 2027-01-01, so re-verify.
- [ ] **Statute of frauds (Utah Code §§ 25-5-1, -3, -4).** Applies to land, agreements not performable within one year, guaranties, and similar agreements.
- [ ] **Pre-suit notice or demand requirements** (for example, in the contract, in a statute, or a government claim).
- [ ] **Contract clauses:** arbitration, forum selection, notice-and-cure, fee-shifting, and jury waiver.
- [ ] **Lien and bond deadlines** (construction). Check the deadlines even when no lien is pleaded.
- [ ] **Business and Chancery Court (Utah Code Title 78A, Chapter 5a).** Consider it for qualifying business disputes. Verify current thresholds.

## Pleading-rule items (see rules/urcp-complaint-checklist.md)
- [ ] **Bold caution language at the top right of the first page (URCP 8(a)).**
- [ ] **Tier in the caption (URCP 10(a)(1)) and in the body (URCP 8(a)).** Compute damages without duplicating alternative theories (URCP 26(c)(4)). Tiers 1 and 2 waive damages above the cap.
- [ ] **Fraud and mistake pleaded with particularity (URCP 9(c)).** State who, what, when, where, and how. A promise about the future is not a misrepresentation of existing fact.
- [ ] **Special damages stated specifically (URCP 9(h)).**
- [ ] **Attorney fees claimed:** state the basis, cite the law or attach the contract, and state that the fee will not be shared in violation of RPC 5.4 (URCP 73(e)).
- [ ] **Relief demanded covers everything wanted.** A default judgment cannot exceed the demand (URCP 54(c)).
- [ ] **Civil cover sheet (URCP 10(a)(4))**, and the jury demand and fee if applicable (URCP 38).

## Equitable and quasi-contract bars
- [ ] **Unjust enrichment and quantum meruit** are barred when an enforceable contract covers the same subject. Plead them in the alternative and label them as such.
- [ ] **Gratuitous benefit.** No recovery for something given with no expectation of payment. Do not plead "donations."
- [ ] **Economic loss rule** for tort claims that duplicate contract duties.
- [ ] **Accounting** requires a fiduciary or confidential relationship, or complex accounts.

## Facts and numbers
- [ ] **Every dollar figure recomputed in code.** Reconcile it to the client's totals and explain any gap.
- [ ] **Relative dates ("last year") normalized** to absolute dates, with the assumption bracketed. Check that the sequence is consistent.
- [ ] **Source typos** (wrong name in the notes) corrected and noted.
- [ ] **Facts that rest only on the client's recollection** flagged. Do not overstate them.

## Law currency (attorney's responsibility; this skill does not check for amendments)
- [ ] **Statutes not renumbered or amended** (for example, venue moved from § 78B-3-307 to § 78B-3a-201 in 2024).
- [ ] **Rule versions:** check the effective dates in rules/manifest.json.
- [ ] **Cited cases exist and state the proposition** (CourtListener plus a pinpoint quote). Caption matches the reporter cite.
