# fresh-eyes-review

See how your document's real readers are likely to react before it goes out: opposing counsel, the judge, your client, the adjuster, and the AI assistant the recipient will paste it into.

> **Status: pre-release (working toward v0.1).** The skill and paste-in prompt work but are still being tested on sample documents.

## What this is, and what it isn't

**It is a writing review.** It tells you how the document is likely to land with each reader: whether the ask is clear, what gets buried or skimmed, what's missing from the page, which sentences could be misread or quoted against you, and how the tone comes across. When readers want different things, it shows you the tradeoff and leaves the choice to you.

**It is not a substantive legal review.** It doesn't check whether your law is right, your citations support your points, your facts are accurate, or your document contains what a rule or statute requires. It will tell you that no standard of review is stated; it won't tell you whether the standard you stated is correct. You remain responsible for the substance.

**It doesn't rewrite your document.** It flags issues and gives you copyable prompts you can use to work on them, but the edits are yours.

**Its readers are simulations.** Treat their reactions as informed hypotheses, not predictions. Simulated readers tend to be more agreeable and more uniform than real people. This tool is a warm-up for real review, not a replacement for it.

**Don't paste in anything you aren't permitted to share with the AI service you're using.** Check your firm's or organization's policies on confidential and privileged material first.

## How it works

1. You give it a document. Everything else (your goal, background, audience, which readers to use) is optional.
2. It identifies the document type and picks three readers (more if you ask) from a library of 16 personas: judges, clerks, opposing counsel, clients, adjusters, regulators, counterparties, and others.
3. Each reader reviews the document from their own position, with only the information that reader would actually have.
4. Separately, it asks a plain AI assistant the questions a recipient would likely ask ("What are they asking me to do, and by when?") and checks whether your ask, deadline, and key point come through.
5. It combines everything into ranked priority actions, tradeoffs, what's working, coverage gaps, and suggested next steps.

## Two ways to use it

### 1. Paste-in prompt (any AI assistant)

1. Open [`extras/portable/single-prompt.md`](extras/portable/single-prompt.md) and copy all of it. If your assistant rejects a message that long, use [`extras/portable/single-prompt-lite.md`](extras/portable/single-prompt-lite.md), which includes only the most-used readers.
2. Paste it into a new chat in Claude, ChatGPT, or Gemini.
3. Paste your document. Optionally add what you want the reader to do, any background (say which parts are privileged), and who will read it.

You'll get the report in the chat. The paste-in version can't check what an AI assistant tells the recipient on its own, because that needs a fresh chat. Instead, it gives you the recipient's questions to try in a new chat yourself.

### 2. Claude skill (Claude Code or claude.ai)

The skill version checks every quote against your document, ranks the issues the same way every time, and saves a full report as a web page you can open in any browser. In Claude Code, it also runs the AI-assistant check in fresh contexts on its own.

- **claude.ai:** zip the inner [`fresh-eyes-review`](fresh-eyes-review/) folder (the one that contains `SKILL.md`), then go to **Settings > Capabilities > Skills > Upload skill** and pick the zip. Code execution must be turned on.
- **Claude Code:** copy the inner `fresh-eyes-review` folder into `~/.claude/skills/` (for all your projects) or into `.claude/skills/` in a project. Then ask Claude for a fresh-eyes review of a document.

Then ask something like "Give this demand letter a fresh-eyes review before I send it." You get a short summary in chat and a full `report.html` (with `report.md` as a plain-text copy).

**Usage.** A review runs three simulated readers plus a synthesis, which takes a meaningful share of a plan's usage. On a Claude Pro plan, expect one review to use roughly a quarter of a usage window and take about 10 minutes. Ask for fewer readers to use less.

## Customizing it for how you work

You can tailor the tool once so you don't have to explain your situation on every run. All of these files are plain text in [`fresh-eyes-review/references/`](fresh-eyes-review/references/).

- **Start with `house-settings.md`.** Set your role (outside counsel, in-house, government, legal aid, law student), who you usually write for, and default readers. For example, if you're in-house, setting your role there makes "the client" your internal business team and drops the outside-counsel-only personas.
- **Change which readers are used for a document type** in `doc-type-map.md`, or list overrides in `house-settings.md`. For example, if your client letters usually go to in-house counsel who forward them to executives, add `client-business-decision-maker` to client letters.
- **Adjust a persona's defaults** in its file under `personas/`, section 10 ("Adaptable parameters"). For example, if your trial-court practice is mostly in federal court, change the trial judge's default court type.
- **Add your own reader** by copying `personas/_template.md`. Describe the reader by role, goal, information, and incentives: no names, backstories, or demographic traits.

If you're using the paste-in prompt, rebuild it after editing (`python build/build_portable.py`, run from `extras/`).

## Roadmap

**v0.1 (in progress):** the Claude skill and the paste-in prompt, with a markdown report.

**After v0.1:**

1. **HTML report**, then a hosted viewer and a Word memo
2. **Test documents** with known issues and answer keys
3. **Validation**: whether separate runs for each reader beat a single conversation, and whether any personas overlap enough to merge
4. **Separate reader runs** in Claude Code, if validation supports them
5. **Gemini Gem and Claude/ChatGPT Project** setups
6. **Guided mode**, which asks a few questions before running

**Later: a standalone web app.** A subscription service for practitioners, also useful to law students learning to write like practitioners. One place to upload a draft, choose readers, and see results, with:

- Comments shown in the margin next to the passages they're about
- One-click follow-ups: run a revision prompt, add a reader, rerun after edits
- Comparing versions of a draft to see whether the issues were resolved
- Export as a Word document with comments, and possibly suggested edits as tracked changes (always as suggestions, never applied automatically)

It will need the confidentiality and data protections firms expect from vendors. The planned approach:

- Run the models through a cloud platform with enterprise data terms (for example, Claude on Amazon Bedrock), so documents stay in the app's own cloud account and aren't used for training
- Don't store documents by default: process each draft in memory, keep results only if the user chooses to
- Use established services for sign-in (including firm single sign-on), payments, and compliance tooling rather than building them

The earlier phases are built so they carry over to a web app: all the content lives in plain files, and every run produces one structured results file that any interface can display.

## Design notes

The persona design draws on Harrington & Stillwell, *Michael Scott Is Not a Juror* (UNT Dallas L. Rev.: On the Cusp, Mar. 2026), which compared AI-simulated mock jurors with about 1,200 human mock jurors. What we took from it:

- Personas describe the **typical reader in a role**, not a colorful character.
- Personas are defined by **role, goal, information, and incentives**, never by demographics.
- Personas describe **how people actually read** (skimming, misreading, reacting emotionally), not how they should.
- Every finding must **quote the passage** it's about, and personas are tested against a no-persona baseline to confirm they add something.
- AI simulations are **less varied than real people**; we present each persona as a typical reader and note common variants.

## License

MIT. See [LICENSE](LICENSE).
