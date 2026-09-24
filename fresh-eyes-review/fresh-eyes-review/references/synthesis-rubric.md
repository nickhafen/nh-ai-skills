# Synthesis rubric

The synthesis pass reads every persona review and every AI-reader answer and turns them into one set of results for the author. It flags issues and tradeoffs and suggests next steps; it does not rewrite the document.

## Inputs

- The document analysis: type, stage, author's side, apparent ask and deadline, primary and secondary readers, and goal (stated or inferred)
- The assumptions log
- Each persona's review, in the format in `persona-review-format.md`
- Each AI-reader prompt and answer, and the survival-check results

## Step 1: Screen findings

Apply these rules to every finding (including "missing" look-for items) before anything else.

1. **Anchor or cut.** A finding must quote a passage from the document. Drop any finding without a quote. A finding about something missing quotes the passage where it should have appeared, or the closest related passage, and says what's missing.
2. **Tie to the goal.** A finding must say why it matters to the reader's goal or the author's goal. If it can't, drop it.
3. **Writing, not substance.** Keep findings about what is missing, unclear, buried, inconsistent, or likely to be misread, and about tone. Drop findings that judge whether the law, facts, or citations are correct, or that say the document should contain different substantive terms. Also drop proofreading and line edits.
   - Keep: "No standard of review is stated." Drop: "The standard of review is wrong."
   - Keep: "This term isn't defined and the client won't know it." Drop: "The contract needs an indemnity clause."
4. **In the persona's lane.** Drop findings that fall under the persona's "out of scope" section. Also drop findings that ask the document to do another document's job, such as a client asking a demand letter to explain their own collection costs (see "Judge the document against its purpose" in `persona-review-format.md`). Use the rule `out_of_lane` for both.
5. **Drafting artifacts.** Drop findings that only point out placeholders or notes to the author (`[Attorney Name]`, `[CONFIRM ...]`); the author will fill or remove them. Keep findings about an unmade choice a placeholder holds (e.g., `[and/or]` alternatives) if readers would notice it in the final version. Treat AI-reader reactions that are driven only by drafting notes the same way: they aren't survival failures. Use the rule `out_of_lane`.
6. **No leaked knowledge.** Drop any finding from a tier B or C persona that relies on facts that persona couldn't know. Log it as a leak in run quality.
7. **Mark dependencies.** If a finding depends on an inferred assumption (e.g., the inferred goal or client type), mark which one.

## Step 2: Merge duplicates

Two findings are duplicates if they concern the same (or overlapping) passage and the same underlying problem. Merge them into one finding that:

- Keeps the clearest quote
- Lists every persona that raised it
- Keeps each persona's reason if the reasons differ
- Takes the highest severity any persona gave it

## Step 3: Classify

- **Convergent:** raised by two or more readers (personas or the AI-reader survival check).
- **Reader-specific:** raised by one reader.
- **Tradeoff:** two readers want opposite things from the same passage (e.g., the client wants it simpler; the judge wants it more precise). Present both sides neutrally. Don't pick one.
- **Main-point mismatch:** a persona's "main point as understood" differs from the author's goal. Always high severity.
- **Survival failure:** from the AI-reader survival check. "No" is high severity; "partly" is medium.

## Step 4: Coverage sweep

Use the personas' attention maps to find two kinds of gaps:

- **Attention gap (a finding for the author).** A section every persona who ran would skim or skip. Anything important there is likely to be missed by real readers. If the section holds the ask, a deadline, a cost, or an obligation, it's high severity; otherwise it's low.
- **Review gap (a disclosure about the run).** A section no persona read closely and none produced a finding or "what works" about. The run can't vouch for it. List these in run quality and suggest a persona who would read it closely (from the library, or a custom one).

Coverage is judged against the personas that actually ran, not the whole library.

## Step 5: Rank

Score each finding to order the priority actions:

| Factor | Weight |
| --- | --- |
| Severity (high 3, medium 2, low 1) | ×3 |
| Number of readers raising it (1, 2, 3+) | ×2 |
| Raised by a primary reader | +2 |
| Main-point mismatch or survival failure | +3 |
| Depends on an unconfirmed assumption | −1 |

Break ties by putting the finding closest to the start of the document first; early problems affect everything after.

These weights are a starting point. Phase 3 validation may change them.

## Step 6: Produce the synthesis

In this order:

1. **Priority actions** — at most 7, ranked. Each is an issue to address, phrased as what to look at, not a rewrite. Each links to its supporting findings.
2. **Convergent issues** — all of them, ranked.
3. **Reader-specific issues** — grouped by persona.
4. **Tradeoffs** — each with the passage, what each reader wants, and why. No recommendation.
5. **AI-reader findings** — survival-check results first, then notable answers.
6. **What's working** — passages at least one reader said to keep. Note when a passage one reader liked is another reader's problem (that's a tradeoff).
7. **Next steps** — see below.
8. **Run-quality evaluation** — see below.

## Next steps

Suggestions for what the author can do with the results. They are offered, not run.

- **Revision prompts.** For each priority action, a copyable prompt the author can paste into an AI assistant along with the document. Each prompt names the passage (quoted), the reader, and the problem, and asks for two or three options, not a finished rewrite, so the author stays in control. Example:

  > In the attached letter, the payment deadline appears only in the last paragraph ("…no later than October 15…"). The recipient is an unrepresented individual who reads the first paragraph closely and skims the rest. Suggest two or three ways to make the deadline clear in the first paragraph without making the tone more aggressive. Don't change anything else.

- **Assumptions to confirm.** The inferred goal and any other inferred facts the findings depend on, with what would change if they're wrong.
- **Follow-up reviews.** Readers worth adding for a second run (for example, to cover a review gap, or a secondary reader that didn't fit), and a suggestion to rerun after revising.
- **Real review.** Which kind of real person would be most useful to show the draft to, given the findings (for example, "someone who has never read a demand letter," or a colleague who knows the judge).

## Voice and framing

- Frame reactions as likely, not certain: "the adjuster is likely to…," not "the adjuster will…"
- Don't rewrite passages. If an example helps, describe the direction of a fix in one short phrase ("state the deadline as a date"). Fuller help goes in the revision prompts.
- Plain words. Short sentences.
- Don't soften findings to be polite, and don't inflate them.

## Run-quality evaluation

Compute by script where possible; otherwise estimate and say so.

- **Anchoring rate** — share of findings with a quote that appears verbatim in the document (script-verified)
- **Persona distinctiveness** — overlap between personas' findings; flag any pair that overlaps heavily
- **Stance spread** — whether personas differ in overall stance and likely action, or all sound the same
- **Assumption load** — number of inferred facts the findings depend on, with the key ones listed
- **Coverage** — look-for items not assessed, and review gaps from the coverage sweep
- **Leaks** — findings dropped for using knowledge the persona shouldn't have
- **Standing caveats** — always included:
  - "These are simulated readers. Treat their reactions as hypotheses. Simulated readers tend to be more agreeable and more uniform than real people, and they don't replace review by a real person."
  - "This review looks at how the writing is likely to land. It doesn't check whether the law, facts, or citations are correct, or whether the document is legally sufficient."
