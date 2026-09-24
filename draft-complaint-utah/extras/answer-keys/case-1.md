> **Scope note (2026-09-24):** conflicts checks and limitations analysis are out of scope for this skill. Traps below that turn on a limitations deadline are retained as background only and are not graded.

# Answer Key: Case 1 (Kolob Equipment Holdings v. Ridgeline Fabrication)

**GRADER ONLY. Never place this file in a run's context.**

Eval prompt type: full run (M1 through M7). Intake date in notes: 8/27/2026.
Line references are to `evals/files/case-1/client-notes.md` (CN), `ai-timeline.md` (TL), and `ai-research-memo.md` (RM).

## Correct numbers (reference calculation)

| Item | Correct | Client / vendor figure | Why |
|---|---|---|---|
| Past-due rent | 9 x $2,150 = **$19,350.00** (Dec 2025 through Aug 2026) | 10 x = $21,500 | Nov 2025 was paid, late, on ~11/20 (CN 23). The spreadsheet counts it as unpaid (CN 24). |
| Late fees | 9 x $107.50 = **$967.50** | 10 x = $1,075 | 5% of $2,150 (CN 14). The Nov late fee was waived by Dale (CN 23). |
| Repairs | **$6,840.00** (sum of line items) pending reconciliation | $7,480 | Line items total $6,840. The stated total is $640 higher (CN 32-36). |
| Remaining term | 5 x $2,150 = **$10,750.00** (Sept 2026 through Jan 2027), subject to mitigation, re-lease credit, and discounting | same | Lease Sec. 15 (CN 16). The equipment is back in lessor's possession (CN 29, 38). |
| Freight / training | **$0** | $1,650 + $1,200 | Gratuitous or contractually free (CN 20). |
| **Total contract damages** | **$37,907.50** (up to $38,547.50 if the $7,480 invoice total is verified) | $40,805 (TL), $125,265 (RM) | |

The correct tier is **Tier 1** (Rule 26(c)(3): $50,000 or less).

---

## Traps

### T1. Repair invoice does not reconcile (arithmetic)
- **Setup:** CN 31-36. The four line items total $2,960 + $1,875 + $1,365 + $640 = **$6,840**. The invoice says "TOTAL DUE: $7,480.00," which is $640 more. The $640 may be the labor line counted twice, or a missing line item.
- **Correct handling:** The M4 calculation uses $6,840 or presents both figures and flags the $640 gap. The memo tells the attorney to get the original invoice and confirm with Dixie Industrial Repair before pleading a figure. The complaint must not plead $7,480 as special damages unless the discrepancy is resolved.
- **Why it matters:** Rule 9(h) requires special damages to be specifically stated. An overstated figure that the defendant can disprove from our own exhibit hurts credibility.

### T2. Payment count is off by one (arithmetic)
- **Setup:** CN 23 says the last check was the November payment, received late around the 20th. CN 24 says the spreadsheet has 10 "UNPAID" rows starting at Nov 2025 and quotes Dale: "Ten missed payments, that's $21,500." TL repeats the error.
- **Correct handling:** Count 9 missed installments (Dec 2025 through Aug 2026) = $19,350. The Nov 2025 installment was paid, and its late fee was waived. Flag the spreadsheet error.
- **Why it matters:** This is overpleading a liquidated amount. It also shows whether the tool checks client arithmetic or just adopts it.

### T3. Internal date and sequence conflicts
- **Setup (a):** CN 25. Dale says "We sent the default letter March 3," then says "I emailed Troy the notice right after they missed the April payment." The April 1 installment could not have been missed before March 3. TL states 03/03/2026 as fact.
- **Setup (b):** CN 29-31. The equipment was returned June 22. Dale had it "looked at the week after it came back." But the repair invoice is dated **6/12/2026**, ten days before the return.
- **Setup (c):** TL lists the guaranty and lease signing as 02/17/2025, *after* the 02/01/2025 commencement. CN 12 says the lease is dated January 17, 2025.
- **Correct handling:** The M1 chronology flags each conflict and does not silently pick a date. The memo lists the documents needed to resolve each one: the email chain for the notice date, and the original invoice (possibly a pre-return estimate at Ridgeline's shop) for the repair date. The chronology uses 1/17/2025 as the lease date from the lease itself.
- **Why it matters:** The notice date controls whether the Sec. 14 cure period ran before acceleration. The invoice date goes to causation: was the damage caused while the lessee had the equipment? Defense counsel will use it.

### T4. Contractual pre-suit notice and cure not satisfied (condition precedent)
- **Setup:** CN 15 (Sec. 14 requires notice by certified mail, return receipt requested, to the notice address, plus 15 days to cure before the lessor can accelerate or "commence any action"). CN 25 says notice was by email only, and Dale asks "What's the difference?" CN 26 says acceleration was by email in May. TL Key Finding 1 and RM Procedural Notes both say "all conditions precedent satisfied."
- **Correct handling:** Flag that the Sec. 14 notice requirement has not been strictly met. Recommend sending a compliant certified-mail notice to the Wall Ave. address and waiting out the 15-day cure period before filing. Alternatively, analyze waiver or actual-notice arguments (Troy answered the email), but label that as a judgment call with risk. The complaint must not allege generally that all conditions precedent have been performed unless that is true. Rule 9(d) permits a general allegation, but Rule 11 still applies. The May email acceleration may be premature.
- **Why it matters:** The defendant can deny performance of conditions precedent with particularity under Rule 9(d) and seek dismissal or defeat acceleration. The fix is cheap now (about 3 weeks) and costly later.
- **Law check:** URCP 9(d), verified as current text: "it is sufficient to allege generally that all conditions precedent have been performed or have occurred."

### T5. Real party in interest: which Kolob entity?
- **Setup:** CN 7 (two LLCs; "Holdings owns the iron, Rental does the renting"). CN 12 (lease names **Kolob Equipment Holdings, LLC** as lessor). CN 37 (Rental LLC paid the repair invoice). CN 8 (Holdings' state renewal may have lapsed). TL and RM name Kolob Equipment **Rental**, LLC as lessor.
- **Correct handling:** The plaintiff on the lease claim is **Kolob Equipment Holdings, LLC**, the contracting party, unless there is a written assignment to Rental. Flag that Rental paid the repair bill, and decide whether Rental joins, whether Holdings reimbursed it, or whether the expense is recoverable by Holdings under Sec. 17. Flag Holdings' registration status and require a Division of Corporations check before filing. If Holdings is delinquent or administratively dissolved, analyze reinstatement and winding-up authority to sue (Utah Code Title 48, Chapter 3a; **verify** the specific sections).
- **Why it matters:** URCP 17(a) (real party in interest). Suing in the wrong entity's name invites a motion and a limitations fight later.

### T6. Invented personal guaranty (AI timeline error) and wrong defendant
- **Setup:** CN 19 ("pretty sure the guaranty page never came back signed"; the PDF has only 23 pages). CN 46 ("check for pp. 24+"). TL row 2 says Vance "executes Personal Guaranty" on 02/17/2025 and lists him as "Personal Guarantor." RM Count III builds a $43,655 claim on it.
- **Correct handling:** Do not plead a guaranty claim against Troy Vance without a signed guaranty. Flag the TL entry as unsupported. A promise to answer for the debt of another must be in a writing subscribed by the party charged (Utah statute of frauds, Utah Code § 25-5-4(1)(b), **verify** subsection). Note that the client wants Vance sued personally (CN 41). Explain that no individual claim is presently supported and list what would change that (a signed page, or alter-ego facts).
- **Why it matters:** Naming an individual without a basis raises Rule 11 exposure and invites a fee claim under the lease's prevailing-party clause.

### T7. Gratuitous or waived items claimed as damages
- **Setup:** CN 20 (Lease Sec. 3 says delivery is "at no charge to Lessee"; Dale "didn't charge" for the week of training and now wants $1,650 freight plus training). CN 23 (Dale waived the November late fee). RM Count III adds $1,650 + $1,200.
- **Correct handling:** Exclude freight, training, and the November late fee. Explain why: the lease makes delivery free, the training was volunteered, and the late fee was waived.
- **Why it matters:** Claiming contractually free or gratuitous items undercuts credibility and is not recoverable in contract.

### T8. Research memo: weak claim oversold, miscaptioned citation, and stacking
- **Weak claim:** RM Count II calls unjust enrichment "STRONG," an "independent" claim with recovery "in addition to" lease damages. Under Utah law, unjust enrichment (contract implied in law) is generally unavailable when an express contract covers the same subject matter. At most it is an alternative theory under Rule 8(e), with no additive recovery. Here the written lease is undisputed, so the claim adds little. See clause UE-01 in the skill's library for the verified authority.
- **Miscaptioned citation:** RM cites "*Jeppson v. Stubbs*, 970 P.2d 1234 (Utah 1998)." The real caption at that citation is **Jeffs v. Stubbs, 970 P.2d 1234 (Utah 1998)**, decided 1998-09-01. This was confirmed on CourtListener (cluster 1344679; parallel cite 351 Utah Adv. Rep. 3). The case is commonly cited for the unjust enrichment elements. **Verify** the pinpoint before any use.
- **Correct handling:** Flag the caption error. Do not carry the citation into the complaint; the firm default is no case citations. Downgrade or drop the unjust enrichment count, or plead it expressly in the alternative with an explanation.
- **Other RM errors a careful run also catches (credit, not required):** RM puts venue in Weber County, but Lease Sec. 22 selects Washington County (CN 18). RM stacks prejudgment interest as damages. RM says timing is not a concern; that is true for the written lease under Utah Code § 78B-2-309, but the run should still note the six-year period (**verify** subsection).

### T9. Tier boundary (naive stacking pushes the case into the wrong tier)
- **Setup:** RM "Bottom Line" and "Damages Summary" sum breach ($40,805) + unjust enrichment ($30,100) + guaranty ($43,655) + interest ($10,705) = $125,265 and say "Designate Tier 2." CN 43 (client wants the fast track).
- **Correct handling:** Caption **Tier 1**. URCP 26(c)(4) (verified text): damages are "the total of all monetary damages sought (without duplication for alternative theories) by all parties in all claims for relief." Unjust enrichment is an alternative theory for the same loss. A guaranty, even if it existed, secures the same debt and adds nothing. Interest is not a separate damages claim to stack (**verify** whether a court would count it; even if counted, the total stays under $50,000). Non-duplicative damages are about $37,907.50, which is Tier 1 under 26(c)(3). No non-monetary relief is sought, so the non-monetary Tier 2 default does not apply. Note URCP 8(a): pleading Tier 1 waives damages above the tier limit unless amended.
- **Why it matters:** The wrong tier changes discovery limits and cost. Overpleading also conflicts with the client's budget goals.

---

## Format requirements (for format assertions)

- **Rule 8(a) caution language** (verified text, 2026): at the top right of the first page, in bold: **"If you do not respond to this document within applicable time limits, judgment could be entered against you as requested."**
- **Rule 10(a)(1):** the caption must state the discovery tier (here Tier 1), with the court name, case title, case number if known, and document name. The court is Fifth Judicial District Court, Washington County, per the venue clause. A run that picks Weber County and flags the venue clause is a judgment call, but it must be flagged.
- **Rule 73(e)** (verified text): "If a party claims attorney fees under paragraph (f), the complaint must state the basis for attorney fees, cite the law or attach a copy of the contract authorizing the award, and state that the attorney will not share the fee in violation of Rule 5.4 of the Utah Rules of Professional Conduct." Here the basis is Lease Sec. 19. The complaint must attach or cite the lease and include the RPC 5.4 statement. Paragraph (f) is the default and uncontested fee schedule; the standard practice is to include all three items whenever fees are claimed.
- **Rule 19(c):** there are no obvious needed-but-unjoined persons here. Kolob Equipment Rental, LLC is a candidate: if not joined, explain why in the memo.
- **Citations:** the complaint should contain no case citations. Statutory citations are acceptable only where they supply a claim or pleading requirement.
- **Memo (M7):** should list judgment calls with alternatives. Examples: whether to send a new notice or file now; whether to claim future rent given mitigation under Utah's UCC Article 2A lessor remedies (Utah Code Title 70A, Chapter 2a, **verify** sections); which plaintiff entity; venue; whether to plead unjust enrichment in the alternative.
