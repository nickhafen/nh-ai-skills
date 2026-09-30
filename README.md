# nh-ai-skills

Agent skills for teaching law students, lawyers, and instructors how skills
work.

**Download a skill:** [nickhafen.github.io/nh-ai-skills](https://nickhafen.github.io/nh-ai-skills/)
has a one-click download for each skill, ready to add to Claude, ChatGPT, Gemini,
or another AI tool that supports skills. It also lets you browse and copy any
file in a skill, and explains how each platform handles skills.

| Skill | What it does |
|---|---|
| [engagement-letter](engagement-letter/engagement-letter/) | Drafts a client engagement letter for a fictional Utah firm, computes Utah answer deadlines for litigation matters, and produces a Word redline with real tracked changes. See its [presenter guide](engagement-letter/engagement-letter/README.md). |
| [fresh-eyes-review](fresh-eyes-review/fresh-eyes-review/) | Shows how a legal document's real readers (opposing counsel, the judge, the client, the adjuster) are likely to react before it goes out, and what an AI assistant would tell the recipient. A writing review, not a check of the law. Pre-release. See its [README](fresh-eyes-review/README.md), which also covers a paste-in prompt for any AI assistant. |
| [scholarly-draft-review](scholarly-draft-review/scholarly-draft-review/) | Gives feedback on a legal scholarship draft (articles, essays, notes, seminar papers) from simulated readers matched to its stage, following Tara Gray's advice to show early drafts to nonexperts and later drafts to experts. Checks whether the claim comes through and builds a key-sentence outline. Feedback only: no drafting, and not a check of the law or sources. Pre-release. See its [README](scholarly-draft-review/README.md). |
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

Use the [download site](https://nickhafen.github.io/nh-ai-skills/): click
**Download skill (.zip)** on a skill, then add the zip to your AI platform. The
site has step-by-step instructions for each platform and a table of how they
differ. In short:

- **Claude:** **Customize > Skills**, click **+**, choose **Create skill >
  Upload a skill**, and pick the zip. Code execution must be on
  (**Settings > Capabilities**).
- **Claude Code:** unzip the download and move the folder into
  `~/.claude/skills/`. Skills uploaded to your Claude account also sync to
  Claude Code when you sign in with it.
- **ChatGPT** (Business, Enterprise, Healthcare, and Edu plans): **Plugins >
  Skills > Create > Upload from your computer**, and pick the zip.
- **Gemini** (personal Google accounts): **Settings > Skills**, and upload the
  zip. Gemini doesn't accept Word or JavaScript files in a skill, so skills with
  a Word template or JavaScript scripts (today, `engagement-letter` and
  `draft-complaint-utah`) won't work there as downloaded.
- **Other tools:** unzip the download and put the folder where your tool looks
  for skills. The [Agent Skills site](https://agentskills.io/clients) links to
  each tool's setup steps.

**Without the site:** download this repo (**Code > Download ZIP**) and unzip
it. Open the skill's top-level folder, then zip the inner folder, the one that
contains `SKILL.md` (Windows: right-click > **Compress to ZIP file**; Mac:
**Compress**). That zip has the same contents as the site's download.

All firms, people, and clients in these skills are fictional. This is teaching
material, not legal advice.
