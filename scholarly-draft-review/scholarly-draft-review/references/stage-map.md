# Stage map

This file tells the skill how to place a draft in a stage, which readers to use at each stage, and what feedback matters now and what can wait. You don't need to read it to use the tool. It matters if you want to know why certain readers were picked or want to change the defaults (see `house-settings.md`).

Persona names below match the files in `personas/`.

## The feedback sequence

The defaults follow Tara Gray's advice in *Publish & Flourish*: share early drafts with nonexperts and later drafts with experts. Her three kinds of readers:

- **Nonexperts:** anyone who doesn't share your training. They can't fill gaps with their own knowledge, and they have no expertise to protect, so they tell you where the draft is unclear or disorganized. Gray's timing is as soon as a full draft exists; a writing partner or writing group can react to a pitch or partial draft even earlier.
- **little-e experts:** people with your training who don't work on your question. For legal scholarship, that's other law faculty and lawyers. They test whether the argument works for the general legal reader. Show them the middle drafts.
- **Capital-E Experts:** the scholars whose work you rely on most. Their time is scarce; ask for a short read near the end, when the draft is good enough that they'll spend it on the big problems (the contribution, the literature, the objections), not on clarity a nonexpert could have caught.

Two more kinds of reader matter in law:

- **Gatekeepers:** law review and peer-review editors, and anyone else deciding whether to take the piece (a workshop or conference committee). They don't give feedback; they decide. Simulate them only when the draft is about to go to them.

## One standard

Every draft is held to the standard of published legal scholarship, whoever wrote it, including student notes and seminar papers. The author's status never changes the readers, the severity of a finding, or the tone of the feedback. Only the draft's stage and where it's headed change the readers.

**Why the order matters even for simulated readers.** A simulated expert's time costs nothing, but the order still matters for the author. Expert feedback on an early draft tends to be about literature and objections the author hasn't reached yet, and it can bury the more basic question of whether the claim is clear. Nonexpert feedback on a submission draft is still useful but rarely decisive.

## Precedence

1. **The user's explicit choice** of readers in the request.
2. **The user's stated stage, venue, or purpose** (e.g., "this is going to a faculty workshop," "it goes out to law reviews next month"), which set the stage row and trigger the swaps below.
3. **House settings** in `house-settings.md`.
4. **The stage default** below.
5. **Inference from the draft**, used only when nothing above decides it.

A user who picks readers keeps them, even readers who don't fit the stage. Their findings are sorted into now and later by the stage table, like everyone else's.

## Placing the draft in a stage

If the user states the stage, use it. Otherwise infer it from the signals below, name the signals you relied on, and mark the stage `inferred`. When the signals are mixed, pick the earlier stage: feedback meant for an earlier stage is less likely to mislead.

| Stage | What it is | Signals |
| --- | --- | --- |
| `idea` | Research question, pitch, abstract, proposal, or notes | Under about 3,000 words; no Parts drafted; states a topic or question; may be bullets |
| `early` | Outline, zero draft, or partial draft | Some Parts in prose and others as headings or bullets; placeholders (`[cite]`, `TK`, `XX`); few footnotes; introduction missing or a sketch |
| `full` | Every Part drafted | Continuous prose from introduction to conclusion; rough transitions; footnotes partial; the introduction may not match the body |
| `workshop` | Revised, footnoted, ready for experts | Complete introduction with a roadmap; full footnotes; few placeholders; marked as a draft or workshop paper |
| `submission` | Final before submission or publication | Abstract, author footnote, complete footnotes, no drafting notes; polished throughout |

**Revising after feedback** isn't a separate stage. If the user supplies comments they're responding to (a peer review, editor's comments, workshop notes, a mentor's comments), place the draft by the signals above and apply the swap below.

## What matters at each stage

Each issue in the synthesis is marked **now** or **later** using this table. A problem that would sink the piece at any stage, such as no discernible claim, is always **now**.

| Stage | Focus now | Park for later |
| --- | --- | --- |
| `idea` | The question; the claim or hypothesis; why it matters; scope | Structure, prose, footnotes, coverage of the literature |
| `early` | The claim; the order of the argument's steps; what each Part is for | Prose, transitions, footnotes, coverage of the literature, polish |
| `full` | Whether the claim is stated and holds from introduction to conclusion; organization; key sentences; the size of the background | Footnote completeness, sentence-level polish, title and abstract |
| `workshop` | The contribution and how it's positioned; objections; stakes; scope; claims about the literature | Sentence-level polish |
| `submission` | Title, abstract, and the introduction's first pages; the novelty statement; a finished look; consistency across Parts | Nothing. Flag large structural issues with a note that they're costly this late |

## Default readers

The same defaults apply to every author (see "One standard for every author").

| Stage | Readers |
| --- | --- |
| `idea` | `smart-outsider`, `generalist-law-colleague` |
| `early` | `smart-outsider`, `generalist-law-colleague` |
| `full` | `smart-outsider`, `generalist-law-colleague`, `field-expert` |
| `workshop` | `field-expert`, `skeptical-expert`, `generalist-law-colleague` |
| `submission` | `articles-editor`, `field-expert`, `skeptical-expert` |

Early stages use two readers on purpose: at that point, two nonexpert reads give the author what they need, and an expert read would be premature. Users can ask for more readers; each adds usage and time.

## Swaps

Apply after the defaults, in this order.

- **Prescriptive or doctrinal piece aimed at courts, legislatures, agencies, or practice:** at `submission`, `practitioner-judge` replaces `field-expert` (the expert read should have happened at the workshop stage). At `workshop`, run it as a fourth reader if the user asks.
- **Empirical or interdisciplinary piece:** adapt `skeptical-expert` (or `field-expert` at `full`) to the methods focus of the relevant discipline.
- **Peer-reviewed or interdisciplinary journal:** at `submission`, replace `articles-editor` with `skeptical-expert` adapted as an anonymous peer reviewer, and add `generalist-law-colleague` adapted to a reader from the journal's discipline.
- **Job-talk paper or appointments packet:** put `generalist-law-colleague`, adapted as an appointments committee member, in the first slot.
- **Symposium piece, invited essay, or book chapter:** drop `articles-editor`; use `field-expert`, `skeptical-expert`, and `generalist-law-colleague`.
- **Note or comment for a journal's notes section:** at `submission`, adapt `articles-editor` to the notes-editor variant.
- **Revising after feedback:** put the reader who gave the feedback first (`skeptical-expert` as peer reviewer, `articles-editor` as the editor, `field-expert` as a mentor, or a custom reader), with the comments as added context. That reader checks whether the draft visibly answers each comment.

## Checks that aren't readers

- **Named-work check:** every stage, whenever a reader names a specific work, author, or case the draft doesn't cite. Each one is looked up before the author sees it (SKILL.md step 5).
- **Key-sentence check:** stages `early` through `submission`, when the draft has at least eight prose paragraphs. Skip it for `idea`.

## Unknown kinds of pieces

1. Place the draft by the stage signals; treat it as the closest kind of piece (a book chapter as an article, a blog post or short essay as an `idea`-stage piece for a general legal audience).
2. Use the defaults for that stage.
3. State the assumption at the top of the output: "Treated as a [stage] draft of a [kind of piece]. Tell me if that's wrong."
