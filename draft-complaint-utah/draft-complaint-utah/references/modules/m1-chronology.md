# M1: Fact intake and chronology

**GENERATE mode**
- Extract every datable event from the primary sources: client notes, documents, and emails.
- Give each event a `source` locator (for example, "Client notes §II ¶3" or "Invoice 2201").
- Normalize relative dates. For example, "last year" becomes an ISO date, and the assumption goes in `date_basis`. Use `[[...]]` when the date is unconfirmed.
- Write the result to `matter.chronology`.

**VALIDATE mode** (an outside timeline was supplied)
1. First build your own skeleton from the primary sources. Do not read the outside timeline before this step.
2. Then diff your skeleton against the outside timeline. For each event, fill `ai_comparison` with one of: consistent / omitted / invented / mischaracterized / wrong date.
3. Never import a fact that appears only in the outside timeline. Flag it instead.

**Always flag:**
- sequence conflicts (for example, event B is described as "after" A but dated earlier);
- amounts that don't reconcile (recompute them in code);
- source typos;
- facts that rest only on the client's recollection;
- unknowns that decide party or claim structure (who paid, who contracted, who owns what).

**Write:** `chronology`, then add each flag to `open_questions` with a priority, then a `run_log` entry.

