# Reader review format

Every reader returns its review in this format. The synthesis depends on it.

## What each reader receives

- Its adapted persona file (including the "How to read as this persona" instruction)
- The full draft, footnotes included
- The author's note (stage, feedback wanted, known gaps, and prior feedback), if the persona is **briefed**. A **cold** reader gets none of it.
- This format

No reader is told the author's intended claim. Each reader reports what *they* think the draft argues; the synthesis compares that to the intended claim.

## Level of feedback

React to the argument and the writing: what is missing, unclear, buried, inconsistent, unsupported on the page, or likely to be misread, and how the argument lands. Expert readers also do what real experts do: say whether the contribution looks new and point to related work (see below). No reader rules on whether the law or the sources are described correctly; this isn't a cite-check.

- In scope: "The claim first appears in Part III." "The draft never states the view it argues against." "'No court has considered this' is the kind of claim an expert will test; the draft doesn't show the search behind it." "This looks close to [a work listed in related work]; the draft should say what it adds." "This characterization of the case law looks off to me; check it." "Part II's conclusion is stronger than anything Part II shows."
- Out of scope: "This misstates the holding" (a ruling, not a flag). "The claim has been made before" with no work named. "Footnote 12 is in the wrong Bluebook form." Line edits.

## Related work and novelty

A real expert says what a draft is close to and what it should engage. Expert readers (`field-expert`, `skeptical-expert`, and any reader adapted as a specialist) may do the same, with these limits:

- **Put every pointer in `related_work`,** not only in the prose of a finding: the work, whether it's specific (a particular work, author, or case) or a kind of work to search for, why it matters to this draft, and how confident the reader is.
- **Name a specific work only when confident it exists** and roughly what it argues. If the reader only half-remembers that someone wrote something relevant, describe the kind of work instead ("empirical studies of sentencing outcomes," "the standard defense of the rule").
- **A judgment that the claim isn't new must point to a specific work** in `related_work`, and say what overlaps and what might still be new. A judgment that the claim *is* new is a view: say what it rests on, and how confident the reader is.
- **Every specific work is checked** before the author sees it (SKILL.md step 5). Findings that rest on a work that can't be found are dropped.

Nonexpert and gatekeeper readers rarely name works; an empty `related_work` list is normal for them.

## One standard for every author

Hold the draft to the standard of published legal scholarship, whoever wrote it, including a student note or seminar paper. Don't lower expectations, soften a finding, lower its severity, or add encouragement because of who the author is. What counts as normal "for now" depends on the draft's stage, never on the author.

## Judge the draft against its stage

A draft is written for a stage. Flag what matters for the stage the author is in, and say plainly when something can wait (see "What matters at each stage" in `stage-map.md`). Don't ask an outline for polished transitions, or an idea-stage pitch for footnotes.

- Missing footnotes, placeholders (`[cite]`, `TK`), and notes to self are expected before `submission`. Read the draft as it will be once they're filled in, and don't make findings about them. At `submission`, visible drafting artifacts are fair game, but make one finding about them, not one per artifact.
- **Known gaps.** If the author's note says a Part is unwritten or a section will change, a briefed reader doesn't flag it. A cold reader may still react to it, since a real cold reader would.
- **Genre.** Judge a doctrinal piece as doctrinal and a short essay as an essay. Don't ask a normative article to be empirical, or a short essay to cover the literature.

## Read the whole draft

Each reader reads the whole draft, footnotes included, in good faith. If part of it was hard to get through (dense background, a Part whose purpose wasn't clear), that's a finding: quote where it happened and say why.

## What each reader returns

1. **Main point as understood.** One sentence: what this reader thinks the draft argues. If they can't tell, say so; that is itself the most important finding.
2. **Look-for checks.** For each item in the persona's "What they look for" section: status (**clear**, **unclear or buried**, **missing**, or **not applicable** when the piece or its stage doesn't call for it, such as a prescription in a purely descriptive piece), the quoted passage if there is one, and one line on why.
3. **Findings.** At most 5. Each has:
   - quoted passage (verbatim from the draft; footnote text counts)
   - issue
   - why it matters to this reader
   - severity: high, medium, or low
4. **What works.** 1–3 quoted passages this reader would want kept.
5. **Related work.** Works or kinds of work this reader would point to (see "Related work and novelty"). Often empty for nonexperts.

A missing look-for item is automatically a finding if it matters to the reader's goal; it doesn't need to be repeated in the findings list.
