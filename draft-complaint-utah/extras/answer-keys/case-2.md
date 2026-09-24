> **Scope note (2026-09-24):** conflicts checks and limitations analysis are out of scope for this skill. Traps below that turn on a limitations deadline are retained as background only and are not graded.

# Answer Key: Case 2 (Holt v. Summit Ridge Medical Supply, Pehrson, and Pehrson Mobile Imaging)

**GRADER ONLY. Never place this file in a run's context.**

Eval prompt type: validate the AI timeline, then draft. Intake date in notes: 9/14/2026.
Line references are to `evals/files/case-2/client-notes.md` (CN) and `ai-timeline.md` (TL).

## Correct numbers (reference calculation)

| Item | Correct | Client / vendor figure |
|---|---|---|
| Q1 2026 commission | 8% x $187,400 = **$14,992.00** | $16,992.00 (CN 13, TL) |
| Q1 balance after $5,000 advance | **$9,992.00** | $11,992.00 |
| Q2 commission, if separation 4/30 | 8% x $41,250 = **$3,300.00** | $3,300 (TL) |
| Q2 commission, if separation 5/8 | + 8% x $22,500 = $1,800 -> **$5,100.00** | not considered |
| Wage total | **$13,292 to $15,092**, plus any Wage Act penalty | $15,292 (TL) |
| Side deal (estimate) | 16 missed quarterly installments (due 10/15/2022 through 7/15/2026) x ~$2,640 = **~$42,240**, subject to accounting | 15 x $2,640 = $39,600 (TL, from the wrong start date) |
| Software help | **$0** (gratuitous) | $4,200 (TL) |

The correct tier is **Tier 2**. Monetary damages are about $55,500 to $57,300. The complaint also seeks an accounting, which is non-monetary relief; under URCP 26(c)(3) (verified) that is Tier 2 absent a claim over $300,000.

---

## Traps

### T1. AI timeline errors (validation task)
- **(a) Mischaracterization:** TL says Holt "resigned effective April 30, 2026." CN 18 and CN 21 say she was terminated ("my position was gone"; "I did not quit").
- **(b) Invented fact:** TL says Holt and Pehrson Mobile Imaging "sign a Referral Profit-Sharing Agreement," citing "image 6." CN 26 says "Nothing signed." The only writing is Garrett's text screenshot (CN 27).
- **(c) Wrong date:** TL says "January 15, 2023: First missed profit-share payment." CN 29-30 show the Q2 2022 check dated 7/15/2022 and the next payment due **October 15, 2022**. TL also sequences the December 2022 party after the "January 2023" miss.
- **Correct handling:** The validation output lists each error with the contradicting source line and a corrected entry. The complaint uses none of the TL errors.
- **Why it matters:** Error (b) turns an oral deal into a written one. Error (c) moves the first breach three months later. Together they make the limitations problem in T4 invisible.

### T2. Commission arithmetic
- **Setup:** CN 11 ($187,400 Net Collected Revenue). CN 10 (8% rate). CN 13 ("$16,992.00 less $5,000 advance = $11,992.00").
- **Correct handling:** 8% x $187,400 = $14,992. The balance is $9,992. Flag the $2,000 error, and do not plead $11,992.
- **Why it matters:** The error feeds into T3 and T9.

### T3. Wage-claim prerequisites: fee demand and the $10,000 threshold
- **Setup:** CN 14 (the 7/20 written demand for "$11,992.00," no Q2 demand). CN 42 ("Check the demand letter against the Wage Act fee statute").
- **Law (verified 2026 against le.utah.gov):**
  - Utah Code § 34-27-1 (amended 2024) allows the employee a reasonable attorney fee only if a written demand for payment was made at least 15 days before suit, **for a sum not exceeding the amount found due**.
  - Utah Code § 34-28-9.5 (effective 7/1/2024) requires exhaustion of administrative remedies (a Labor Commission wage claim) for wage claims of $10,000 or less, with stated exceptions. For larger claims, it provides actual damages plus a penalty of 2.5% of unpaid wages per day, capped at 20 days, and any § 34-28-5(1)(c) penalty.
  - 2026 S.B. 213 proposed adding limitations periods to § 34-28-9.5. **Verify** whether it was enacted and its effective date.
- **Correct handling:**
  - Flag that the 7/20 demand ($11,992) exceeds the Q1 amount actually due ($9,992). That puts § 34-27-1 fees at risk.
  - Recommend a corrected written demand covering Q1 and Q2 that does not exceed the correct figure, then wait at least 15 days before filing the wage claim.
  - Flag the § 34-28-9.5 threshold. Q1 alone ($9,992) is under $10,000. Q1 plus Q2 is over. Explain how the aggregation exception applies (**verify**).
  - The side-deal money is not "wages" from the employer and cannot be used to clear the threshold.
- **Judgment call:** The 15-day wait conflicts with the October 15 limitations date in T4. Options: send the demand immediately (a filing around 10/6 still beats 10/15); file the side-deal claims first and add the wage claims by amendment; or file everything now and forgo § 34-27-1 fees. The memo should present the alternatives.
- **Rule 73(e):** If fees are claimed, the complaint must cite § 34-27-1 as the basis and include the RPC 5.4 statement. The comp plan has no fee clause (CN 10).

### T4. Limitations: the oral side deal is about to expire
- **Setup:** CN 24-30 (oral deal made spring 2022; first missed installment due **10/15/2022**). The intake date is 9/14/2026. TL "Deadlines" says: "written contract, 6-year limitations period. Earliest deadline: January 2029."
- **Law:** Utah Code § 78B-2-307: 4 years for a contract, obligation, or liability not founded on an instrument in writing (**verify** subsection, believed (1)(a)). Utah Code § 78B-2-309: 6 years for a written contract (**verify** subsection). A text confirming a percentage is unlikely to make this a contract "founded upon an instrument in writing," because the essential terms (15% of *what*, whose accounts, payment timing) are not in the writing. Each missed installment is generally treated as accruing separately (**verify** Utah authority before relying on it).
- **Correct handling:** Treat the claim as oral, with a 4-year period. The earliest installment's claim expires on about **October 15, 2026**, 31 days after intake. Flag this as urgent and put it at the top of the memo. Later installments survive on a rolling basis. Garrett's statement at the December 2022 party ("he'd true it up," CN 30) may be argued as an acknowledgment. Utah requires an acknowledgment or promise to be in writing and signed to extend the period (Utah Code § 78B-2-113, **verify**), and this one was oral.
- **Why it matters:** This is a malpractice-grade miss if the tool adopts TL's "January 2029."

### T5. Statute of frauds: the five-year term
- **Setup:** CN 26 ("Fifteen percent of the net for five years"). CN 27 (text: "Yep 15% for 5 yrs like we said. Don't tell Kyle his number. -G").
- **Law:** Utah Code § 25-5-4(1)(a): an agreement that by its terms cannot be performed within one year is void unless it, or a note or memorandum of it, is in writing and subscribed by the party to be charged (**verify** current subsection). Electronic records and signatures can satisfy a writing requirement under Utah's Uniform Electronic Transactions Act (Utah Code § 46-4-201, **verify**).
- **Correct handling:** Identify the issue. A fixed five-year term cannot be fully performed within a year. Analyze whether the "-G" text is a sufficient memorandum: it is signed by Garrett, but it is thin on essential terms. Consider whether it binds Pehrson Mobile Imaging, LLC if the LLC is the party to be charged. Consider part performance and promissory estoppel as fallbacks, and label them as judgment calls. Do not declare the claim barred, and do not ignore the issue.

### T6. Separation date conflict
- **Setup:** CN 18 (fired Friday, May 8). CN 19 (HR letter dated May 11 says "effective April 30"). CN 20 (final paycheck May 15). CN 15 ($22,500 collected May 1-8). CN 10 (comp plan Sec. 7: commissions are earned only on revenue collected on or before the "Separation Date").
- **Correct handling:** Flag the conflict. Plead the May 8 separation date, which is supported by the client's testimony and presumably by pay records; check what period the final pay stub covers. Calculate Q2 both ways ($3,300 vs. $5,100). The separation date also sets the timing for final-wage obligations and penalties under Utah Code § 34-28-5 (**verify** the current timing and penalty subsections).

### T7. Real party in interest and counterparty on the side deal
- **Setup:** CN 24-25 (Garrett "started" Pehrson Mobile Imaging, LLC and made the deal personally). CN 29 (the check came from the LLC, payable to "Holt Consulting LLC"; Garrett: "make it to your LLC, it's cleaner"). CN 7 (Holt Consulting LLC is Brenna's single-member LLC). CN 44 (attorney flagged both questions).
- **Correct handling:** Flag both ambiguities.
  - **Plaintiff side:** Brenna individually, Holt Consulting LLC, or both. Payment to the LLC suggests the LLC may be the payee or assignee, but Brenna made the deal and did the referral work. Consider joining both, or confirm the entity's status and intent.
  - **Defendant side:** Garrett individually, Pehrson Mobile Imaging, LLC, or both.
  - A profit-sharing arrangement may raise a partnership or joint-venture theory. Under the Utah Uniform Partnership Act, a person who receives a share of business profits is presumed to be a partner, subject to exceptions (Utah Code § 48-1d-202, **verify**). That presumption would change the claims (accounting, fiduciary duty) and the analysis. Present it as a judgment call.
  - URCP 17(a) (real party in interest).

### T8. Gratuitous services
- **Setup:** CN 32 (60 hours of weekend help; "I told Garrett don't worry about it, happy to help, it's my deal too"). TL adds $4,200.
- **Correct handling:** Do not plead quantum meruit or unjust enrichment for the $4,200. Services volunteered without an expectation of payment are not recoverable. The client's own words negate any expectation of payment. Explain this to the attorney.

### T9. Rule 19(c): needed person not joined
- **Setup:** CN 28 (Kyle Mabey, another rep who gets about 10% "of the same pool," now in Boise, Idaho). CN 45 ("Kyle may matter if we ask for an accounting of the pool"). CN 35 (the client wants "a full accounting").
- **Correct handling:** If the complaint seeks an accounting or declaratory relief about the profit pool, analyze whether Mabey is a person described in Rule 19(a). If he is not joined, the complaint must include a Rule 19(c) statement naming him and the reasons he is not joined: for example, he resides in Idaho, no claim is asserted against him, and his share is separately computed. Accept either a 19(c) statement, or a memo explanation that the relief is limited to Holt's share so Mabey is not a Rule 19(a) person.
- **Law (verified text):** URCP 19(c): "A pleading asserting a claim for relief shall state the names, if known to the pleader, of any persons as described in Subdivision (a)(1)-(2) hereof who are not joined, and the reasons why they are not joined."

---

## Format requirements

- Rule 8(a) bold caution language at the top right of page 1 (see case-1 key for the verified text).
- The caption states **Tier 2** (Rule 10(a)(1)).
- Rule 73(e) statements for § 34-27-1 fees (cite the statute; include the RPC 5.4 statement).
- Rule 19(c) statement or memo analysis (T9).
- No case citations in the complaint.
- Venue: Salt Lake County (Third District) is proper for the employer. The Davis County defendants are joined on related claims. **Verify** the current venue statute; see the library README note on § 78B-3-307 vs. § 78B-3a-201.
