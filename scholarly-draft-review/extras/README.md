# extras

Maintainer tools for scholarly-draft-review. None of this is part of the installed skill.

| Folder | What's in it |
| --- | --- |
| `build/` | `check_personas.py` (persona schema check), `build_schema.py` (generates the skill's `results.schema.json`), `build_portable.py` (generates the paste-in prompt) |
| `portable/` | The generated paste-in prompt. Don't edit it by hand. |
| `fixtures/` | Fictional drafts with seeded issues and what a good review should find: a faculty workshop draft and an early student note |
| `examples/` | A complete working folder and report from a run on the workshop fixture. Open `workshop-article/report.html` to see what users get. The tests use it as their base case. |
| `tests/` | Offline tests for the skill's scripts (`python tests/test_scripts.py`) |
| `docs/` | `decisions.md`: design choices and open questions |

The example run was written by hand in a Claude Code session following SKILL.md, without a search for named works (the one specific work named is already cited in the draft).
