# nh-ai-skills

Agent skills for teaching law students, lawyers, and instructors how skills
work.

**Download a skill:** [nickhafen.github.io/nh-ai-skills](https://nickhafen.github.io/nh-ai-skills/)
has a one-click download for each skill, ready to add to Claude, ChatGPT, Gemini,
or another AI tool that supports skills. It also lets you browse and copy any
file in a skill, find skills by user, practice area, and task, and see how each
platform handles skills.

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
nothing on the site is edited by hand. Any top-level folder `X/` with
`X/X/SKILL.md` becomes a skill on the site. What the site shows comes from:

| On the site | Comes from |
|---|---|
| Card title | `name` in `SKILL.md` |
| Card text, card order, and the Pre-release badge | The skill's row in the table above. The text before any "See its…" pointer becomes the card text; "Pre-release." adds the badge; cards follow the table's order. |
| Tags and filters | `extras/site.json` (see [Tags](#tags)) |
| "Includes Python scripts…" and the Gemini warning | The files in the inner skill folder, read automatically |
| Download (.zip) | The inner skill folder, exactly as it is |

### Tags

Each skill's `extras/site.json` tags it for the site's filters. Each key is a
category from [site/facets.json](site/facets.json), which also lists the
allowed values, and takes a list of those values. Leave out a category that
doesn't apply.

```json
{
  "users": ["practitioner"],
  "area": ["litigation"],
  "task": ["drafting"],
  "jurisdiction": ["utah"]
}
```

| Category | Values |
|---|---|
| `users` | `academic`, `practitioner` |
| `area` | `litigation`, `transactional`, `scholarship` |
| `task` | `drafting`, `review`, `research`, `coding` |
| `jurisdiction` | `utah` |

To add a value or a whole category, add it to `site/facets.json` first (and to
the table above). The build fails on a value that file doesn't list, so a typo
can't create a stray filter. The site also adds two filters on its own:
whether a skill includes scripts, and its status.

`site.json` can also set `"summary"` (card text) and `"status"` (`"stable"` or
`"pre-release"`), which override the README row. It lives in `extras/`, so it
never goes into the skill's download.

Search and filters appear on the site once it lists 8 or more skills
(`FILTER_MIN` in `site/app.js`). Before then, a link with filters in it, such
as `…/#/?task=review`, still shows them.

## Add a skill

1. **Make the folders.** Create `my-skill/my-skill/SKILL.md`. Put
   maintainer-only material (evals, build scripts, presenter notes) in
   `my-skill/extras/`, not in the inner folder, because everything in the
   inner folder goes into the download.
2. **Check the frontmatter.** `name` must match the folder name exactly
   (at most 64 lowercase letters, digits, and single hyphens, with no "claude"
   or "anthropic"). `description` is required, at most 1024 characters, with no
   `<` or `>`. Quote any value that contains `: `. The build checks all of this
   against Claude.ai's upload rules.
3. **Add a row to the table** at the top of this README, in the order you want
   the card to appear: `| [my-skill](my-skill/my-skill/) | What it does. |`.
   Write the "What it does" text for people choosing a skill, not for the AI.
   Add "Pre-release." if it isn't ready for general use.
4. **Tag it** in `my-skill/extras/site.json` (see [Tags](#tags)).
5. **Build and test locally:**

   ```bash
   python -m unittest discover -s site
   ```

   ```bash
   python site/build.py --out dist
   ```

   ```bash
   python -m http.server 8766 --directory dist
   ```

   Open `http://localhost:8766`, check the card and tags, click **Browse
   files**, and try the download.
6. **Open a pull request.** The same checks run on it; merging to `main`
   publishes the site.

New files are picked up as long as Git doesn't ignore them; they don't need to
be committed first to show up in a local build.

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
  a Word template or JavaScript scripts won't work there as downloaded. The
  site's Gemini instructions list which ones.
- **Other tools:** unzip the download and put the folder where your tool looks
  for skills. The [Agent Skills site](https://agentskills.io/clients) links to
  each tool's setup steps.

**Without the site:** download this repo (**Code > Download ZIP**) and unzip
it. Open the skill's top-level folder, then zip the inner folder, the one that
contains `SKILL.md` (Windows: right-click > **Compress to ZIP file**; Mac:
**Compress**). That zip has the same contents as the site's download.

All firms, people, and clients in these skills are fictional. This is teaching
material, not legal advice.
