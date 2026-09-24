# M0: Intake and configuration

1. **Load the profile.** Default: `profiles/default.json`. If more than one profile exists and the request doesn't say which to use, ask once.
2. **Inventory the materials.** Classify each file as one of:
   - client facts
   - outside timeline (and which vendor made it)
   - research memo (and which vendor)
   - court forms or templates
   - rules and statutes
   - sample pleadings
   - firm template
3. **Pick a mode for each module:**
   - GENERATE when there is no input for it.
   - VALIDATE when an outside version exists.
   - MERGE when there are several research memos.
   - SKIP only when the user says so.
   Write one `run_log` entry per module, in the form `{module, mode, inputs, tool, timestamp}`.
4. **Ask the configuration questions** in one AskUserQuestion call, and only for things not already settled by the request, the profile, or memory: court and county, plaintiff and defendant structure, and any change to the profile's claim posture or checkpoint mode.
5. **Note the rules-pack date.** `references/rules/manifest.json` records when each rule and statute was last verified and any known supersession date. This skill does not check for amendments; tell the attorney the pack's date and list it as a pre-filing item in the memo.


6. **Hard gates. Stop and ask when:**
   - the client's identity or party role is unclear;
   - a fact that decides whether a claim exists at all cannot be inferred.
**Out of scope:** conflicts clearance, limitations analysis, and checking for rule or statute amendments are not part of this skill. The attorney handles all three.

7. **Create `matter.json`** with `matter`, `parties`, and an empty `run_log`. Report the plan in 3–6 lines.
