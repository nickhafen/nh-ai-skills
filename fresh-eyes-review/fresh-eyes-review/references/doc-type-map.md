# Document-type map

This file tells the skill which readers to use for each kind of document. You don't need to read it to use the tool. It matters only if you want to know why certain readers were picked, or you want to change the defaults (see "Customizing" in the README).

Persona names below match the files in `personas/`.

## How readers are chosen

**Precedence (highest first):**

1. **Your explicit choice** in the request.
2. **Your context** in the request (e.g., "they have a lawyer," "an insurer is involved"), which triggers the swaps listed below.
3. **House settings** in `house-settings.md` (e.g., "I'm in-house").
4. **Document-type default** below.
5. **Inference from the document**, used only when nothing above decides it.

**Primary readers first, then secondary.** Each entry lists primary readers (people who will read and act on the document now) and secondary readers (people who may read it later or indirectly). Three personas run by default: primary readers fill the slots first, in the order listed, and any empty slots go to secondary readers, in order. You can ask for more; each added reader adds cost and time.

**Which three.** After applying swaps, take the first three primary readers in the order listed. Entries are ordered so the first three are the best default set. Say which readers were left out, so the user can ask for them.

**Own side.** "Own client" means whoever the author works for:

- If the author is outside counsel, pick `client-individual`, `client-business-decision-maker`, or `client-in-house-counsel` based on who will read it.
- If the author is in-house, the reader is the internal business client: use `client-business-decision-maker`, adapted to "internal client of an in-house lawyer." Don't use `client-in-house-counsel`; that's the author.

**Coverage.** Real readers skim. That's useful to know (anything important in a section everyone skims will be missed), but the run still needs someone to evaluate every part of the document. Each entry says whether its default readers include one who reads the whole document closely. Where none does, the output must report which sections no reader read closely (see `synthesis-rubric.md`).

**Every run states its choices:** the document type detected, the personas used, any swaps, and the reason for each.

## AI-reader batteries

Prompt wording lives in `ai-reader-prompts.md`.

- **Core** — always runs
- **Adversarial** — the recipient is represented or sophisticated
- **Client** — client-facing documents
- **Transactional** — contracts and deal documents

---

## Litigation

### Demand letter

- **Aliases:** demand, pre-suit letter, notice of claim, cease-and-desist
- **Primary readers:** recipient (`opposing-party-unrepresented`), own client, `senior-colleague`, `opposing-counsel`
- **Secondary readers:** `future-interpreting-court` (reading the letter as an exhibit)
- **Swaps:**
  - Recipient is represented → replace `opposing-party-unrepresented` with `opposing-counsel` in first place; `opposing-counsel` is the recipient.
  - An insurer is involved → the recipient is `insurance-claims-professional`.
  - Recipient is a business → adapt `opposing-party-unrepresented` to a small-business owner.
- **AI-reader recipient:** the recipient. **Batteries:** Core; Adversarial if represented or an insurer.
- **Coverage:** with an unrepresented recipient, no default reader reads the legal reasoning closely; add `opposing-counsel` (the lawyer they may hire) if that part matters. With a represented recipient, `opposing-counsel` reads the whole letter closely.

### Complaint

- **Aliases:** petition, statement of claim
- **Primary readers:** `opposing-counsel`, `trial-judge`, own client
- **Secondary readers:** `public-press-reader`
- **Swaps:** none by default.
- **AI-reader recipient:** the defendant. **Batteries:** Core, Adversarial.
- **Coverage:** `opposing-counsel` reads the whole complaint closely.

### Motion or response

- **Aliases:** motion, brief, memorandum in support, opposition, reply
- **Primary readers:** `trial-judge`, `opposing-counsel`, `senior-colleague`, `judicial-law-clerk`
- **Secondary readers:** `appellate-judge`
- **Swaps:**
  - On appeal → `appellate-judge` replaces `trial-judge` and `judicial-law-clerk`.
  - If Phase 3 folds the clerk into the trial judge → drop `judicial-law-clerk`.
- **AI-reader recipient:** the opposing party. **Batteries:** Core, Adversarial.
- **Coverage:** `opposing-counsel` reads the whole filing closely (as does `judicial-law-clerk`, if added).

### Client letter

- **Aliases:** advice letter, status letter, case update
- **Primary readers:** own client, `senior-colleague`
- **Secondary readers:** `future-interpreting-court` (if the advice is later disputed)
- **Swaps:** addressed to in-house counsel who will forward it → add `client-business-decision-maker`.
- **AI-reader recipient:** the client. **Batteries:** Core, Client.
- **Coverage gap:** no default reader reads the middle closely. Individual clients and business decision-makers read the opening and the numbers; the senior colleague skims the middle. Report uncovered sections.

### Email to opposing counsel

- **Aliases:** meet-and-confer email, negotiation email, letter to counsel
- **Primary readers:** `opposing-counsel`, own client, `senior-colleague`
- **Secondary readers:** `trial-judge` (if the email is attached to a motion)
- **Swaps:** none by default.
- **AI-reader recipient:** opposing counsel. **Batteries:** Core, Adversarial.
- **Coverage:** `opposing-counsel` reads the whole email closely.

### Regulatory submission

- **Aliases:** comment letter, self-report, response to inquiry, application
- **Primary readers:** `regulator-agency-staff`, own client, `senior-colleague`
- **Secondary readers:** `public-press-reader`
- **Swaps:** agency is investigating → adapt `regulator-agency-staff` to the enforcement variant.
- **AI-reader recipient:** agency staff. **Batteries:** Core, Adversarial.
- **Coverage:** `regulator-agency-staff` reads the whole submission closely.

### Mediation statement

- **Aliases:** mediation brief, confidential settlement statement
- **Primary readers:** `mediator`, `opposing-counsel` (if shared), own client, `senior-colleague`
- **Secondary readers:** none
- **Swaps:** confidential to the mediator → drop `opposing-counsel`.
- **AI-reader recipient:** the mediator; opposing counsel if shared. **Batteries:** Core; Adversarial if shared.
- **Coverage gap (confidential statements):** the mediator skims long legal argument, and no other default reader reads it closely. Report uncovered sections.

---

## Transactional

**Transactional posture.** In deals, the counterparty is a negotiating partner as well as an adversary, so the key question is what they will push back on, not how they will respond. The document governs a relationship for years, so implementers and later readers matter more. And a court may read it only after a dispute, when ambiguity is the main risk.

### Fee / engagement agreement

- **Aliases:** engagement letter, retainer agreement, fee agreement
- **Primary readers:** own client, `senior-colleague`
- **Secondary readers:** `future-interpreting-court`
- **Swaps:** none by default.
- **AI-reader recipient:** the client. **Batteries:** Core, Client, Transactional.
- **Coverage:** `future-interpreting-court` fills an open slot and reads the terms closely.

### Commercial contract

- **Aliases:** services agreement, supply agreement, license, MSA, SOW
- **Primary readers:** `counterparty-business-contact`, `opposing-counsel` (deal posture), own client, `implementer-operations`
- **Secondary readers:** `future-interpreting-court`
- **Swaps:** the client's in-house counsel is reviewing (author is outside counsel) → `client-in-house-counsel` as own client.
- **AI-reader recipient:** the counterparty. **Batteries:** Core, Transactional.
- **Coverage:** `opposing-counsel` reads the whole contract closely.

### Term sheet / LOI

- **Aliases:** letter of intent, heads of terms, memorandum of understanding
- **Primary readers:** `counterparty-business-contact`, `opposing-counsel` (deal posture), own client
- **Secondary readers:** none
- **Swaps:** none by default.
- **AI-reader recipient:** the counterparty. **Batteries:** Core, Transactional.
- **Coverage:** `opposing-counsel` reads the whole document closely.

### NDA

- **Aliases:** nondisclosure agreement, confidentiality agreement
- **Primary readers:** `counterparty-business-contact`, own client
- **Secondary readers:** `future-interpreting-court`
- **Swaps:** none by default.
- **AI-reader recipient:** the counterparty. **Batteries:** Core, Transactional.
- **Coverage:** `future-interpreting-court` fills an open slot and reads the terms closely.

### Settlement agreement

- **Aliases:** release, settlement and release agreement
- **Primary readers:** `opposing-counsel`, own client, opposing party (`opposing-party-unrepresented`)
- **Secondary readers:** `future-interpreting-court`
- **Swaps:** opposing party is represented → adapt the opposing party to a represented party reviewing with counsel.
- **AI-reader recipients:** own client; opposing party. **Batteries:** Core, Client, Transactional.
- **Coverage:** `opposing-counsel` reads the whole agreement closely.

### Client advice memo on a deal

- **Aliases:** deal memo, transaction advice memo, issues list
- **Primary readers:** own client, `senior-colleague`
- **Secondary readers:** none
- **Swaps:** none by default.
- **AI-reader recipient:** the client. **Batteries:** Core, Client.
- **Coverage gap:** decision-makers read the summary; the senior colleague skims the middle. Report uncovered sections.

---

## Unknown document types

1. Infer the primary readers (who will act on it) and the purpose from the content.
2. Use the closest entry, or pick three personas directly, primary readers first.
3. Include `senior-colleague` unless the user says otherwise.
4. State the assumption at the top of the output: "Treated as a [type] read mainly by [reader]. Tell me if that's wrong."
