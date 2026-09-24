# Clause Library: Utah District Court Civil Complaints

Starter library of claim modules (called "clauses") for drafting Utah state district court complaints. Each clause file has the elements with authority, template pleading paragraphs tagged by element, prayer language, alternative-pleading notes, bars and defenses, and an authority verification log.

**Status of this library:** Claude (AI) drafted and verified it on 2026-09-21. An attorney must review it before use. Treat every clause as a starting point, not as a statement of current law.

## Index

| ID | Claim | File | Typical pairing | Verification status |
|---|---|---|---|---|
| BOC-01 | Breach of contract (express, written or oral) | `BOC-01-breach-of-contract.md` | Lead count; pair with GFD-01; UE-01 / BOC-02 / PE-01 in the alternative | Verified 2026-09-21 |
| BOC-02 | Breach of contract implied in fact | `BOC-02-implied-in-fact-contract.md` | Alternative to BOC-01 | Verified 2026-09-21 |
| GFD-01 | Breach of implied covenant of good faith and fair dealing | `GFD-01-good-faith-fair-dealing.md` | Companion to BOC-01 (needs a contract) | Verified 2026-09-21 |
| UE-01 | Unjust enrichment / quantum meruit (contract implied in law) | `UE-01-unjust-enrichment-quantum-meruit.md` | Alternative to BOC-01 / BOC-02 | Verified 2026-09-21 |
| PE-01 | Promissory estoppel | `PE-01-promissory-estoppel.md` | Alternative to BOC-01 | Verified 2026-09-21 |
| AS-01 | Account stated | `AS-01-account-stated.md` | Companion to BOC-01 in debt collection | Verified 2026-09-21 |
| JV-01 | Breach of joint venture / partnership agreement | `JV-01-joint-venture-partnership.md` | With FD-01 and ACC-01; BOC-01 in the alternative | Verified 2026-09-21 |
| FD-01 | Breach of fiduciary duty | `FD-01-breach-of-fiduciary-duty.md` | With JV-01, ACC-01, CONV-01 | Verified 2026-09-21 |
| ACC-01 | Accounting (equitable) | `ACC-01-accounting.md` | Remedy tied to JV-01 / FD-01 | Partly verified: no Utah elements case confirmed |
| CONV-01 | Conversion | `CONV-01-conversion.md` | With FD-01; alternative to BOC-01 | Partly verified: money-conversion limit [UNVERIFIED] |
| FRD-01 | Fraud (intentional misrepresentation) | `FRD-01-fraud.md` | With NM-01; watch economic loss rule next to BOC-01 | Verified 2026-09-21 |
| NM-01 | Negligent misrepresentation | `NM-01-negligent-misrepresentation.md` | Alternative to FRD-01 | Verified 2026-09-21 |
| DJ-01 | Declaratory judgment | `DJ-01-declaratory-judgment.md` | With BOC-01 or any claim about an instrument | Verified 2026-09-21 |

## How to use

1. **M2: choose clauses.** Map the client's facts to claims. For each candidate, open the clause file and confirm that every element (E1, E2, ...) has a supporting fact or a fact the client can realistically get. Record the element-to-fact map. Choose alternative theories on purpose (see each file's "Alternative-pleading notes"). Do not include a claim only because it appears in the index.
2. **M5: adapt the pleading paragraphs.** Put the operative facts once, in General Allegations. Count paragraphs then incorporate those facts and state each element conclusion tied to the defined terms ({{Agreement}}, {{Amount}}, and so on). Rewrite every template sentence in terms of the actual facts. Resolve every `[[...]]` item. Delete element tags like `[E1]` before filing.
3. **Never paste law text as fact.** Element statements, authority notes, and the logs are for the drafter. They do not go into the complaint. Firm default: no case citations in the complaint. Statutes may be cited where a statute supplies the claim or a pleading requirement (for example, contractor licensure under Utah Code § 58-55-604).
4. **Check pleading rules for every complaint.** Utah R. Civ. P. 8(a) requires a short and plain statement, a demand for specified relief, and a statement of the Rule 26(c)(3) damages tier. Rule 8(e) allows alternative, hypothetical, and inconsistent claims. Rule 9(c) requires particularity for fraud and mistake. Rule 9(h) requires special damages to be specifically stated.
5. **Check the law again.** Each file's log shows what was verified and how. Before filing, run a citator check on every case and confirm the current version of every statute. Items marked [UNVERIFIED] need research before anyone relies on them.

## Conventions

- Placeholders: `{{Plaintiff}}`, `{{Defendant}}`, `{{Agreement}}`, `{{Amount}}`, `{{Date}}`, and so on.
- `[[...]]` marks an item the drafter must confirm or choose.
- `[E#]` tags show which element a paragraph pleads.
- Utah Code citations follow the current code as checked on the verification date. Some sections have been renumbered. For example, § 78B-6-401 was rewritten effective July 1, 2024. Project notes say general venue moved from § 78B-3-307 to § 78B-3a-201 in 2024; this library did not verify that change, so confirm it before relying on it.
