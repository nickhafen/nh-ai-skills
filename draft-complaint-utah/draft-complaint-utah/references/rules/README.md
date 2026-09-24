# Rules pack

Snapshot of the Utah authority this skill relies on when drafting a complaint.

| File | What it is |
|---|---|
| `urcp-complaint-checklist.md` | Verbatim URCP requirements for the content and form of a complaint |
| `manifest.json` | Each rule and statute: citation, official source URL, effective date, the date it was last verified, and any known supersession date |

## Rule currency is the attorney's responsibility

**This skill does not check whether rules or statutes have changed.** Everything here is a snapshot verified on the date in `manifest.json` (initially 2026-09-21). Utah amends the Rules of Civil Procedure on a regular cycle, and Utah Code sections get renumbered (for example, general venue moved from § 78B-3-307 to § 78B-3a-201 in 2024). Known items to watch:

- Utah Code § 58-55-604 (contractor licensure) is scheduled to be superseded on 2027-01-01.
- URCP 26 was amended effective 2025-05-07; URCP 73 effective 2026-05-01.

Before relying on the pack, confirm the rules you actually cite against the official sources in `manifest.json` (utcourts.gov for the rules, le.utah.gov for the code), and update the snapshot and the `last_verified` date when you do.

Add the full URCP text here as a searchable file if you want it. Do not load it into context by default; search it for the rule you need.
