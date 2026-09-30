# scholarly-draft-review

Feedback on a legal scholarship draft from the readers who should see it at its current stage. For anyone writing legal scholarship: articles, essays, job-talk papers, notes, comments, and seminar papers.

> **Status: pre-release (working toward v0.1).** The skill, scripts, and paste-in prompt work, and an example run is in [`extras/examples/`](extras/examples/). The six reader personas are drafts and haven't yet been reviewed by other faculty.

It's the scholarship counterpart to [fresh-eyes-review](../fresh-eyes-review/README.md), which does the same kind of review for documents going to clients, courts, and opposing counsel.

## What this is, and what it isn't

**It matches readers to the stage of the draft.** A pitch, an outline, a full draft, a workshop draft, and a submission draft need different readers. Following Tara Gray's advice in *Publish & Flourish*, it uses nonexperts early and experts later, and it saves the law review articles editor for the submission draft. It infers the stage from the draft unless you tell it, and anything you say (the stage, where it's going, which readers you want) overrides what it infers.

**It treats every author as a scholar.** A student note gets the same readers, the same severity, and the same tone as a faculty article at the same stage. Only the stage and where the piece is headed change the readers.

**It gives feedback, not drafting.** It never writes or rewrites any part of your draft: no sample sentences, thesis statements, abstracts, or titles. It tells you where each reader got lost, what they think you're arguing, what they'd object to, and what's working. Instead of rewrite prompts, it gives you questions to answer before you revise.

**Its experts engage the literature, and it checks what they name.** Like real experts, the expert readers say whether your contribution looks new and point to work you should engage. Because a model can misremember or invent sources, every specific work they name is looked up before you see it (using web search or a research connector when one is available). Works that check out are linked; works that can't be found are dropped; and if no search tool is available, named works are clearly marked as unchecked. A judgment that your claim has already been made must point to a work that checked out. It isn't a cite-check: it won't rule on whether you've described a case correctly, though an expert may flag a characterization to double-check.

**Its readers are simulations.** Treat their reactions as informed hypotheses. Simulated readers are more agreeable and more uniform than real people, and a simulated expert knows only what the model knows, which is incomplete and out of date (recent SSRN postings especially). Check what they say against real readers before you rely on it.

**Every result starts with its limitations.** The chat summary and the report open with "Before you rely on this": the readers are simulations, the AI can be wrong (including about sources), its sense of the literature is incomplete and out of date, it isn't a cite-check, and anything you act on needs checking. Items specific to the run are added, such as works that couldn't be checked or a claim the review had to infer.

**Your draft goes to an AI service.** Follow any rules that apply to your use of AI tools, such as a journal's or publisher's policy, and don't paste in anything you aren't comfortable sharing.

## How it works

1. You give it a draft. Everything else is optional: the stage, where it's headed, your claim in one sentence, what feedback you want, and gaps you already know about.
2. It places the draft in one of five stages (idea, early draft, full draft, workshop draft, submission draft) and says why.
3. It picks readers for that stage (see below), adapted to your field and venue.
4. Each reader reads the whole draft in good faith and reviews it from their own position. None of them is told your intended claim; comparing what each thinks you argue with what you meant is the main test of whether your claim comes through. Expert readers also point to related work.
5. Every specific work a reader named is looked up, so you see only works that exist, or works clearly marked as unchecked.
6. A key-sentence check lists the first sentence of every paragraph, in order, and asks whether that outline alone tells your argument (one of Gray's revision techniques).
7. It combines everything into one ranked list of issues, with the priority actions for this stage first and issues for a later draft after them, each with a one-line direction. It also notes what's working.

### The readers

| Reader | Kind | Default stages |
| --- | --- | --- |
| Smart reader outside law | Nonexpert | Idea through full draft |
| Law colleague outside the subfield | Law-trained, outside the specialty | Idea through workshop |
| Expert in the field | Specialist | Full draft through submission |
| Skeptical expert (workshop commentator or peer reviewer) | Specialist | Workshop and submission |
| Law review articles editor | Gatekeeper | Submission |
| Judge or practitioner | Law-trained, outside the academy | Submission, for pieces that propose something |

For example, an early draft gets the smart outsider and the law colleague; a workshop draft gets the field expert, the skeptical expert, and the law colleague; a submission draft gets the articles editor and both experts. Those defaults are the same for every author. The full table, with swaps for job-talk papers, peer-reviewed journals, symposium pieces, and revisions after feedback, is in [`stage-map.md`](scholarly-draft-review/references/stage-map.md).

## Two ways to use it

### 1. Paste-in prompt (any AI assistant)

1. Open [`extras/portable/single-prompt.md`](extras/portable/single-prompt.md) and copy all of it.
2. Paste it into a new chat in Claude, ChatGPT, or Gemini.
3. Paste your draft. Optionally add the stage, where it's going, your claim, and what feedback you want.

You'll get the report in the chat. If your assistant can search the web, it looks up any works the readers name; otherwise it labels them as unchecked.

### 2. Skill (Claude, Claude Code, or another platform that supports skills)

The skill version checks every quote against your draft, builds the key-sentence outline by script, ranks issues the same way every time, and saves a full report as a web page you can open in any browser. The report refers to your draft by filename and doesn't include its text, so you can share it without sharing the draft.

- **Install:** click **Download skill (.zip)** on the scholarly-draft-review card on the [skills site](https://nickhafen.github.io/nh-ai-skills/), then add the zip to your AI platform. The site has the steps for Claude, Claude Code, ChatGPT, Gemini, and other tools.
- **Needs code execution:** the skill runs Python scripts (standard library only), so the platform must be able to run code. On Claude, turn on code execution under **Settings > Capabilities**.
- **Claude Code:** you can also copy the inner [`scholarly-draft-review`](scholarly-draft-review/) folder into `.claude/skills/` in one project instead of `~/.claude/skills/`.

Then ask something like "Here's my draft for our faculty workshop; how will it land?" or "Can you give feedback on my note draft? My thesis is that…" You get a short summary in chat and a full `report.html` (with `report.md` as a plain-text copy).

**Usage.** A review runs two or three simulated readers plus a synthesis. Expect it to use a meaningful share of a plan's usage window, more for long articles. Ask for fewer readers to use less.

## Customizing it

All of these are plain text in [`scholarly-draft-review/references/`](scholarly-draft-review/references/).

- **Start with `house-settings.md`.** Give your fields, where you usually publish, and what you usually write, so you don't have to repeat it on every run.
- **Change which readers are used at a stage** in `stage-map.md`, or list overrides in `house-settings.md`.
- **Adjust a reader** in its file under `personas/`, section 8 ("Adaptable parameters"). For example, set the expert's default field.
- **Add your own reader** by copying `personas/_template.md` (for example, a tenure-letter writer or a specific journal's peer reviewer). Describe the reader by role, goal, knowledge, and incentives: no names, backstories, or demographic traits.

If you're using the paste-in prompt, rebuild it after editing (`python build/build_portable.py`, run from `extras/`).

## Design notes

**Who reads when.** The stage map follows Tara Gray, *Publish & Flourish: Become a Prolific Scholar* (New Mexico State University Teaching Academy). Gray sorts readers into nonexperts (anyone without your training, best at spotting what's unclear or disorganized), little-e experts (people with your training outside your specialty), and Capital-E Experts (the scholars you cite most), and advises sharing early drafts with nonexperts and later drafts with experts, asking Capital-E Experts for a short read shortly before submission: to spot major problems, suggest citations, and recommend journals. That's why the expert readers here point to related work, with a lookup step added because a model's citations can't be taken on trust. The key-sentence check follows her advice to organize paragraphs around key sentences and to use them as an after-the-fact outline.

**What readers look for.** The personas' checklists draw on standard advice for legal and academic writers:

- Eugene Volokh, *Academic Legal Writing* (Foundation Press): a claim that is novel, nonobvious, useful, and sound, stated early.
- Elizabeth Fajans & Mary R. Falk, *Scholarly Writing for Law Students* (West Academic): a thesis rather than a topic, and analysis over description.
- Wendy Laura Belcher, *Writing Your Journal Article in Twelve Weeks* (University of Chicago Press): an argument stated up front, and positioning against the existing conversation.
- Wayne C. Booth et al., *The Craft of Research* (University of Chicago Press): the problem and its significance, and acknowledging and responding to objections.
- Gerald Graff & Cathy Birkenstein, *They Say / I Say* (W. W. Norton): naming the view you respond to.

**How the personas are built.** Like fresh-eyes-review, the personas follow Harrington & Stillwell, *Michael Scott Is Not a Juror* (UNT Dallas L. Rev.: On the Cusp, Mar. 2026): each describes the typical reader in a role by goal, knowledge, and incentives, never by demographics; each describes how people actually react (getting lost, losing patience, doubting the argument); and every finding must quote the passage it's about.

These attributions were compiled from general familiarity with the works and from secondary summaries of Gray's steps, not from a fresh reading of each book. Check them, and editions and pin cites, before relying on them in your own work.

## License

MIT. See [LICENSE](../LICENSE).
