# House settings

Edit this file once so you don't have to repeat yourself on every run. Every setting is optional. Leave a setting blank to use the default. Anything you say in a request overrides these settings for that run.

## About you

- **Your role:** (default: outside counsel at a law firm)
  Options: outside counsel at a law firm · in-house counsel · government lawyer · legal aid or nonprofit · law student · other: ___
- **Who you usually write for:** (default: inferred from each document)
  Examples: individual clients · business executives · internal business teams · agency staff
- **Practice areas:** (default: none; used only to adapt persona parameters, never to add legal content)

## Defaults for every run

- **Mode:** fast | guided (default: fast)
- **Output:** chat summary + HTML report | add docx memo (default: chat summary + HTML report)
- **Always include these personas:** (default: none)
- **Never use these personas:** (default: none)
- **Maximum personas per run:** (default: 4)

## Document-type overrides

List any document types where you want different readers than `doc-type-map.md` gives. Example:

```
Client letter: client-business-decision-maker, senior-colleague, client-in-house-counsel
```

## What these settings change

- **In-house:** "own client" becomes the internal business client (`client-business-decision-maker`, adapted), and `client-in-house-counsel` is not used. `senior-colleague` reads as a peer or the head of the legal department.
- **Government:** "own client" becomes the agency decision-maker (`client-business-decision-maker`, adapted to an agency official).
- **Legal aid or nonprofit:** own client defaults to `client-individual`, with experience set to "first legal matter" and cost sensitivity set high.
- **Law student:** `senior-colleague` reads as a supervising attorney or professor.
