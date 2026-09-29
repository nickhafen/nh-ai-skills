# nh-ai-skills

Agent skills for teaching law students, lawyers, and instructors how skills
work.

**Download a skill:** [nickhafen.github.io/nh-ai-skills](https://nickhafen.github.io/nh-ai-skills/)
has a one-click download for each skill, ready to upload to Claude.ai.

| Skill | What it does |
|---|---|
| [engagement-letter](engagement-letter/engagement-letter/) | Drafts a client engagement letter for a fictional Utah firm, computes Utah answer deadlines for litigation matters, and produces a Word redline with real tracked changes. See its [presenter guide](engagement-letter/engagement-letter/README.md). |
| [fresh-eyes-review](fresh-eyes-review/fresh-eyes-review/) | Shows how a legal document's real readers (opposing counsel, the judge, the client, the adjuster) are likely to react before it goes out, and what an AI assistant would tell the recipient. A writing review, not a check of the law. Pre-release. See its [README](fresh-eyes-review/README.md), which also covers a paste-in prompt for any AI assistant. |
| [scholarly-draft-review](scholarly-draft-review/scholarly-draft-review/) | Gives feedback on a legal scholarship draft (articles, essays, notes, seminar papers) from simulated readers matched to its stage, following Tara Gray's advice to show early drafts to nonexperts and later drafts to experts. Checks whether the claim comes through, builds a key-sentence outline, and suggests which real people to ask next. Feedback only: no drafting, and not a check of the law or sources. Pre-release. See its [README](scholarly-draft-review/README.md). |
| [update-dependencies](update-dependencies/update-dependencies/) | Updates pinned third-party code (CDN script URLs, vendored libraries, package manifests) safely: checks for security advisories and new versions, bumps pins, recomputes SRI hashes, reviews changelogs for breaking changes, and verifies the app still works. A developer tool for maintaining web apps, not a legal skill. |
| [draft-complaint-utah](draft-complaint-utah/draft-complaint-utah/) | Drafts a Utah district-court civil complaint from client facts in modules you can run alone: chronology, claim selection, element mapping, damages, drafting, multi-perspective review, and a drafting memo. Checks outside work product (a Harvey or CoCounsel timeline, research memos) against the sources instead of redoing it, and renders the complaint as a Word file. AI-drafted and not yet attorney-reviewed; checking rule currency, conflicts, and limitations is left to the attorney. Its [extras](draft-complaint-utah/extras/README.md) hold sample evals and the steps for updating the skill after a matter. |

## Layout

Each skill has a top-level folder. Inside it, the skill itself is in a
subfolder with the same name, next to an `extras` folder:

```
engagement-letter/
├── engagement-letter/   ← the skill (SKILL.md is here). Zip this folder.
└── extras/              ← presenter and maintainer tools. Not part of the skill.
```

The download site is built from this layout. Every push to `main` rebuilds
and republishes it (`site/build.py`, run by `.github/workflows/pages.yml`), so
nothing on the site is edited by hand. A skill's card uses its row in the table
above; "Pre-release." in that row adds the badge.

## Install a skill

**Claude.ai:**
1. Download this repo (green **Code** button > **Download ZIP**) and unzip it.
2. Open the skill's top-level folder. Right-click the inner skill folder, the
   one that contains `SKILL.md`, and zip it (Windows: **Compress to ZIP file**;
   Mac: **Compress**).
3. In Claude, go to **Settings > Capabilities > Skills** > **Upload skill** and pick that zip.

**Claude Code:** copy the inner skill folder to `~/.claude/skills/`.

All firms, people, and clients in these skills are fictional. This is teaching
material, not legal advice.
