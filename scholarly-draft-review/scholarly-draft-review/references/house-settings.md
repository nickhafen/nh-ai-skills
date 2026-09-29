# House settings

Edit this file once so you don't have to repeat yourself on every run. Every setting is optional. Leave a setting blank to use the default. Anything you say in a request overrides these settings for that run.

Nothing here changes the standard a draft is held to. Every draft is reviewed against the standard of published legal scholarship, whoever wrote it.

## About your work

- **Your fields:** (default: inferred from each draft; used only to adapt the expert readers, never to add legal content)
- **Where you usually publish or submit:** (default: student-edited law reviews)
  Examples: student-edited law reviews · peer-reviewed law journals · interdisciplinary journals · books
- **What you're usually writing:** (default: inferred from each draft)
  Examples: articles · essays · job-talk paper · note or comment · seminar paper · book chapter

## Defaults for every run

- **Always include these readers:** (default: none)
- **Never use these readers:** (default: none)
- **Maximum readers per run:** (default: 4)

## Stage overrides

List any stage where you want different readers than `stage-map.md` gives. Example:

```
workshop: field-expert, skeptical-expert, practitioner-judge
```

## What these settings change

- **Peer-reviewed or interdisciplinary venues:** at `submission`, the peer-reviewer swap replaces `articles-editor`.
- **Notes or comments:** at `submission`, `articles-editor` reads as a notes editor.
- **Pieces that propose something to courts or practice:** the prescriptive-piece swap in `stage-map.md` applies.
