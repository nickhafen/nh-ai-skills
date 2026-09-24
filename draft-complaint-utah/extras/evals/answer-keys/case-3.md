> **Scope note (2026-09-24):** conflicts checks and limitations analysis are out of scope for this skill. Traps below that turn on a limitations deadline are retained as background only and are not graded.

# Answer Key: Case 3 (Kimball v. ASR Exteriors LLC dba Apex Summit Roofing and Tyler Brandt)

**GRADER ONLY. Never place this file in a run's context.**

Eval prompt type: **M1 chronology and M2 claim selection only, then pause for approval.** Intake date in notes: 9/10/2026.
Line references are to `evals/files/case-3/client-notes.md` (CN), `ai-timeline.md` (TL), and `ai-research-memo.md` (RM).

## Correct numbers (reference)

| Item | Correct | Vendor / other figure |
|---|---|---|
| Contract line items | **$20,200** | "CONTRACT TOTAL: $21,450" (CN 29), $1,250 over |
| Paid by client | $2,500 check + $14,212.60 insurance check + $2,150 cash = **$18,862.60** | $16,712.60 (TL "verified from check images"; RM refund line) |
| Balance Apex claims | $4,737.40 = $21,450 - $16,712.60. Wrong on both inputs. Using the line-item total and all payments: $20,200 - $18,862.60 = $1,337.40. | $4,737.40 (CN 44; TL "consistent with contract total") |
| Tarping | **$0** (gratuitous) | $1,200 (RM) |

---

## Traps

### T0. Scope: stop after M1 and M2
- **Correct handling:** The run produces a chronology and a claims chart (element map at claim-selection depth), then stops and asks for approval. It does **not** draft a complaint or run M5 through M7. Any complaint text is a failure of the scope assertion.

### T1. Storm date wrong in the AI timeline
- **Setup:** CN 11: "the Saturday before Mother's Day." Mother's Day 2026 is Sunday, May 10, so the storm was **Saturday, May 9, 2026**. TL says 05/02/2026.
- **Correct handling:** The chronology uses May 9, 2026 and flags the TL error. This is minor on its own, but it tests whether the run checks vendor dates against the source.

### T2. Invented permit and mischaracterized work stoppage (AI timeline)
- **Invented fact:** TL "06/03/2026 - Apex obtains roofing permit from Springville City." CN 37 says Springville City has no roofing permit on file.
- **Mischaracterization:** TL "06/19/2026 - Work paused at Mrs. Kimball's request pending supplemental insurance payment." Nothing in the notes supports this. CN 36 says the crew "Left June 19. Never came back." CN 43 says Loretta called more than ten times.
- **Correct handling:** Flag both and exclude them from the chronology. The "paused at client's request" entry is dangerous because it supplies the defendant's excuse for nonperformance.

### T3. Signing-date sequence conflict and cancellation rights
- **Setup:** CN 12 (visit around Monday, May 18; "I signed that same day"). CN 30 (deposit check dated **May 22**). CN 21 (contract dated **May 27**; no cancellation language; Loretta recalls no cancellation form).
- **Correct handling:** Flag that the contract date is after both the claimed signing date and the deposit check. The contract may have been backdated or re-papered, or Loretta's memory is off. The actual date matters for any rescission or cancellation-rights theory for a door-to-door sale. Flag cancellation rights as an item to research, not as an established claim. Candidates: the FTC Cooling-Off Rule, 16 C.F.R. Part 429, and Utah home-solicitation provisions. **Verify** applicability, including any emergency-repair exception, the current Utah section numbers, and remedies. Do not assert these rights as settled.

### T4. Arithmetic: contract total and payments do not reconcile
- **Setup:** CN 23-29. The line items sum to $20,200, but the contract says $21,450. CN 30-33 show payments of $2,500, $14,212.60, and $2,150 cash, totaling $18,862.60 ("almost nineteen thousand," which matches). TL and RM use $16,712.60 and omit the cash. The August 14 demand for $4,737.40 (CN 44) equals $21,450 - $16,712.60.
- **Correct handling:** Flag the $1,250 overstatement in the contract total and the omitted $2,150 cash payment. Note that the cash payment has no receipt; Derek is a witness (CN 32). Show that Apex's claimed balance is built on both errors.
- **Why it matters:** These facts support the fraud and UCSPA theories: an inflated total, and cash taken "for the permit" when no permit was pulled. They also defeat the lien threat.

### T5. Fraud particularity (URCP 9(c))
- **Setup:** CN 14-18. There are specific statements by Brandt at the kitchen table around May 18: (1) licensed and bonded, (2) insurance covers 100%, (3) will pull the permit. The "Gold-tier" warranty statement has an uncertain speaker (CN 17). An unnamed office woman told Derek in June that they had been "in business twenty years" (CN 18). RM tells the drafter to plead that "Defendants repeatedly misrepresented ... throughout the relationship."
- **Law:** URCP 9(c) (verified text): "In alleging fraud or mistake, a party must state with particularity the circumstances constituting fraud or mistake."
- **Correct handling:** The claims chart itemizes each misrepresentation with speaker, date, place, content, why it was false, and reliance. It separates particularized statements (Brandt's three) from unattributed ones (office woman; gutter-guard warranty) and marks the gaps to investigate. It rejects RM's generic "repeatedly misrepresented" formulation. It notes that the "insurance covers 100%" statement may be framed as a promise or prediction, which is weaker than the present-fact licensure statement. The licensure statement is the strongest.

### T6. Contractor licensure (Utah Code § 58-55-604)
- **Setup:** CN 45 (DOPL lookup: the ASR Exteriors LLC license "expired 2025"; nothing for Apex or Brandt). CN 44 (the lien threat and the $4,737.40 demand). CN 21 (no license number on the contract).
- **Law (verified 2026 text):** "A contractor ... may not act as agent or commence or maintain any action in any court of the state for collection of compensation for performing any act for which a license is required by this chapter without alleging and proving that the licensed contractor ... was appropriately licensed when the contract sued upon was entered into, and when the alleged cause of action arose." Note: le.utah.gov shows this version as **superseded 1/1/2027**, when § 58-55-604 is reassigned to other subject matter. **Verify** where the licensure bar is codified if the pleading is filed on or after 1/1/2027.
- **Correct handling:**
  - Identify § 58-55-604 as a **bar on Apex's ability to sue for its claimed balance**. It is a defense to any counterclaim and relevant to the lien threat. It does not create a homeowner's cause of action.
  - Use the license lapse as the falsity element of the licensure misrepresentation (fraud; UCSPA).
  - Recommend getting DOPL certified license history showing status on the contract date and the breach dates.
  - Flag lien-law questions for research: whether an unlicensed contractor can hold a valid mechanics' lien, and whether the owner-occupied-residence protections apply given the contractor's license status (Utah Code Title 38, Chapters 1a and 11, **verify**).

### T7. Real parties: trust ownership and the correct defendant entity
- **Setup:** CN 7 (the house is in the Kimball Family Trust; Loretta believes she is the successor trustee). CN 8 (Loretta is the named insured). CN 21 (Loretta signed the contract individually; "Apex Summit Roofing" with no entity named). CN 30 (the deposit was stamped "ASR Exteriors LLC - For Deposit Only"). CN 44 (the letterhead says "ASR Exteriors LLC dba Apex Summit Roofing," Layton).
- **Correct handling:**
  - **Plaintiffs:** Loretta individually, as contracting party and payor, and as trustee of the Kimball Family Trust, for property damage to trust property. Get the trust instrument and the recorded deed to confirm the successor-trustee appointment (URCP 17(a)).
  - **Defendants:** ASR Exteriors LLC (confirm through the Division of Corporations entity and DBA search), plus Tyler Brandt individually for his own misrepresentations. Not just "Apex Summit Roofing," which is a trade name (RM "Next Steps" names only Apex).
  - Optional credit: flag possible partial subrogation by Beehive Mutual for the ACV it paid (**verify**).

### T8. Gratuitous benefit
- **Setup:** CN 39 (Caleb tarped the roof; "He wouldn't take a penny"; Derek wants $1,200). RM includes $1,200.
- **Correct handling:** Exclude it. Loretta incurred no cost, and the services were a gift. Note that Caleb is a useful witness for the condition of the roof on June 29.

### T9. Research memo: weak claim oversold, misstated remedies, miscaptioned citation
- **Weak claim oversold:** RM calls the Utah Pattern of Unlawful Activity Act claim "STRONG / HIGHEST VALUE" with "treble damages." The civil remedy (Utah Code § 76-10-1605) requires a "pattern of unlawful activity": at least three episodes of enumerated predicate offenses meeting the statutory definition (Utah Code § 76-10-1602, **verify**). It also requires an enterprise nexus, and the predicate fraud must be pleaded with particularity. One homeowner's experience plus two unauthenticated online reviews is thin. The civil remedy is, to our understanding, **twice** (not three times) the damages plus fees (**verify** § 76-10-1605(1)). The run should rate this claim weak or premature. At most it is an investigation item, and it should not lead the complaint.
- **Misstated UCSPA remedy:** RM says UCSPA damages are "trebled." Utah Code § 13-11-19(2) provides "actual damages or $2,000, whichever is greater, plus court costs" (confirmed in the 2018-2025 version). Attorney fees are available under § 13-11-19(5) when a supplier has violated the Act and the action ends in judgment. The section was amended effective 2025; **verify** the current text. Treble damages are not the UCSPA remedy.
- **Miscaptioned citation:** RM cites "*Harris v. Armed Services Ins. Exch.*, 2003 UT 14, 70 P.3d 35." The real caption is **Armed Forces Insurance Exchange v. Harrison, 2003 UT 14, 70 P.3d 35** (Utah Apr. 25, 2003). This was confirmed on CourtListener (cluster 2639411; parallel cite 472 Utah Adv. Rep. 5). The case is commonly cited for the nine elements of fraud. **Verify** the pinpoint before any use.
- **Other RM issues (credit, not required):** The negligence claim may face the economic loss rule and Utah's construction-defect statute (Utah Code § 78B-4-513, **verify**).

### T10. Alternative remedies must not be stacked
- **Setup:** RM "Damages Estimate" adds the refund of amounts paid ($16,712.60) and the replacement roof ($19,800), plus interior repairs, tarping, and then trebles.
- **Correct handling:** The claims chart treats rescission and restitution (return of the $18,862.60 paid) and benefit-of-the-bargain or cost-to-repair damages as **alternatives**. Consequential interior damage ($2,340) can accompany either. The UCSPA $2,000 minimum is an alternative floor, not an add-on. If the chart previews a tier, it should apply Rule 26(c)(4)'s no-duplication rule. On these numbers the case is likely Tier 1 unless punitive damages are pleaded in an amount that changes the total; flag that as a judgment call.

---

## Format / process expectations for this prompt
- The chronology cites a source for every entry and flags conflicts.
- The claims chart lists each candidate claim with elements, supporting facts, gaps, bars and defenses, and a strength rating. Weak claims are labeled weak.
- No case citation appears unless it is marked "unverified" or "verify." The miscaptioned RM citation is not repeated under the wrong name.
- The run ends by asking for approval before drafting.
- Limitations: fraud has a 3-year period from discovery (Utah Code § 78B-2-305, **verify** subsection). Nothing is close to expiring, but a careful run notes the period.
