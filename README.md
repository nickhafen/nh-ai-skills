# nh-ai-skills

Agent skills for teaching law students, lawyers, and instructors how skills
work.

| Skill | What it does |
|---|---|
| [engagement-letter](engagement-letter/engagement-letter/) | Drafts a client engagement letter for a fictional Utah firm, computes Utah answer deadlines for litigation matters, and produces a Word redline with real tracked changes. See its [presenter guide](engagement-letter/engagement-letter/README.md). |

## Layout

Each skill has a top-level folder. Inside it, the skill itself is in a
subfolder with the same name, next to an `extras` folder:

```
engagement-letter/
├── engagement-letter/   ← the skill (SKILL.md is here). Zip this folder.
└── extras/              ← presenter and maintainer tools. Not part of the skill.
```

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
