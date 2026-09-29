# Synthesis rubric

The synthesis reads every reader review and the key-sentence check and turns them into one set of results for the author. It flags issues, sorts them into now and later, shows tradeoffs, and suggests who to ask next. It never drafts or rewrites.

## Inputs

- The draft analysis: kind of piece, stage, where it's headed, field, claim (stated or inferred), whether it's prescriptive
- The author's note, if any (stage, feedback wanted, known gaps, prior feedback)
- Each reader's review (`persona-review-format.md`)
- The named-work check (`related-work.json`)
- The key-sentence check, if it ran

## Step 1: Screen findings

Apply these rules to every finding (including "missing" look-for items and key-sentence flags) before anything else. Record every dropped finding with its rule; the report lists them in its Method section.

1. **Anchor or cut** (`no_anchor`). A finding must quote the draft. A finding about something missing quotes the passage where it should have appeared, or the closest related one.
2. **Tie to a goal** (`no_goal_link`). A finding must say why it matters to the reader's goal or the author's. If it can't, drop it.
3. **Not a cite-check** (`substance`). Keep findings about what is missing, unclear, buried, inconsistent, or unsupported on the page; about how the argument lands; and experts' views on novelty and related work that meet rule 4. Drop findings that rule on whether the law or sources are described correctly. Drop proofreading, line edits, and citation form.
   - Keep: "An expert is likely to test this characterization of the case law; flag it for checking." Drop: "This characterization of the case law is wrong."
4. **Named works must check out** (`unverified_source`). Use `related-work.json`.
   - Drop a finding that rests on a work marked `not_found`. If the point survives without the work ("the draft doesn't engage empirical work on X"), keep that version and note the change.
   - A finding that the claim isn't new stays only if it rests on a work marked `verified` or `cited_in_draft`. Otherwise, rewrite it as a question for a search ("an expert would ask how this differs from work on X") and put the search in the feedback plan.
   - A finding that rests on a work marked `not_checked` stays, but its summary must say the work hasn't been checked.
5. **In the reader's lane** (`out_of_lane`). Drop findings under the persona's "out of scope" section, findings that ask the piece to be a different genre, and findings that only point out placeholders or notes to self before `submission`.
6. **Known gaps** (`known_gap`). Drop findings about gaps the author's note already names.
7. **No leaked knowledge** (`leaked_knowledge`). Drop any finding that shows the reader knew the intended claim, or that relies on the author's note when the reader is cold.

## Step 2: Merge duplicates

Two findings are duplicates if they concern the same (or overlapping) passage and the same underlying problem. Merge them into one issue that keeps the clearest quote, lists every reader who raised it with each reader's reason, and takes the highest severity any reader gave it.

## Step 3: Classify

- **Finding:** raised by one or more readers.
- **Claim mismatch:** a reader's "main point as understood" differs from the author's claim, or a reader couldn't state a claim at all. Always high severity. Name the readers and what each thought the draft argued.
- **Key sentence:** from the key-sentence check: paragraphs whose opening doesn't say what they're for, or an outline that doesn't tell the argument.
- **Tradeoff:** two readers want opposite things from the same passage (the outsider wants more background; the expert wants less). Present both sides neutrally. Don't pick one.

## Step 4: Now or later

Mark every issue **now** or **later** using "What matters at each stage" in `stage-map.md`. Anything that would sink the piece (no discernible claim, a claim that changes between the introduction and the conclusion, an argument that doesn't reach its conclusion) is **now** at every stage. Only **now** issues become priority actions; **later** issues go in a short "park for later" list so the author doesn't lose them.

## Step 5: Rank

Scripts score the issues; don't rank them yourself. The weights, for reference:

| Factor | Weight |
| --- | --- |
| Severity (high 3, medium 2, low 1) | ×3 |
| Number of readers raising it (1, 2, 3+), counting the key-sentence check | ×2 |
| Claim mismatch | +3 |

Only **now** issues are eligible for the top seven. Ties go to the issue closest to the start of the draft.

## Step 6: Produce the synthesis

1. **Issues:** every surviving issue with title, quote, summary, supporting findings, each reader's reason, severity, category, now or later, and a direction in one short phrase ("state the claim in the first paragraph"), never a rewritten passage.
2. **Tradeoffs:** each with the passage, what each reader wants, and why. No recommendation.
3. **What's working:** passages at least one reader said to keep.
4. **Feedback plan:** two to four real readers to ask next, in order, from "Real readers to suggest" in `stage-map.md`, tailored to the findings: who (a kind of person, never a named individual), when (`now`, `next_draft`, or `before_submission`), what to ask them, and why. If a finding can only be settled by a real expert or a search (for example, whether the claim is new), say so here.
5. **Dropped findings,** with their rules.

Related work isn't written here: the report lists it from the reviews and `related-work.json`, with verified works linked, unchecked ones labeled, and works that weren't found left out.

## Voice and framing

- Frame reactions as likely, not certain: "the articles editor is likely to…," not "will."
- Don't rewrite passages, draft sentences, or suggest wording. Directions are one short phrase.
- Plain words. Short sentences.
- Don't soften findings to be polite, and don't inflate them. Early drafts are supposed to have problems; say so when the problems are normal for the stage.
- One standard: the same severity, framing, and tone whoever the author is. Only the stage decides what's normal for now.

## Limitations to disclose

Every chat summary and report shows these under "Before you rely on this," near the top, whether or not the user reads anything else. Don't drop, shorten, or soften them.

Always:

- **These are simulated readers.** The readers are AI simulations of typical readers, not real people. Their reactions are hypotheses, and simulated readers tend to be more agreeable and more alike than real ones.
- **AI can be wrong, including about sources.** The AI can misread your draft, misstate what it says, or invent or misdescribe sources. Quotes from your draft are checked word for word; summaries and paraphrases aren't. A named work is marked verified only if a search found it, which confirms it exists and seems to address the topic, not that it says what the reader claims.
- **Novelty views are leads.** What the AI knows about legal scholarship is incomplete and out of date, especially recent work. Treat its views on whether your claim is new, and its reading suggestions, as leads, and do your own search before relying on them.
- **Not a cite-check.** This review doesn't verify the law, cases, facts, or citations in your draft. A reader may flag something to check; nothing here confirms that anything is correct.
- **Verify before you act.** Check anything you plan to act on against your draft and the sources, and get real readers' reactions before you submit. The feedback plan suggests who to ask.
- **Your draft went to an AI service.** Follow any rules that apply to your use of AI tools, such as a journal's or publisher's policy.

When they apply to the run:

- **Your claim was inferred:** the user didn't state a claim.
- **The stage was inferred:** the user didn't state the stage; say what the draft was treated as and why.
- **Named works not checked:** list each specific work no search looked up, and say to confirm it before relying on it.
- **Some quotes weren't found in your draft:** name the findings.
