#!/usr/bin/env python3
"""Deterministic checks on a matter.json before and after drafting.
Rule currency is NOT checked here: the attorney is responsible for confirming that the rules pack is current.
Usage: python3 validate_matter.py matter.json [--profile profiles/default.json]
Exit code 0 = no errors (warnings allowed); 1 = errors. Prints a JSON report.
The rules encoded here come from the URCP complaint checklist and the common-misses list. Add a check whenever a real miss is found.
"""
import json, re, sys, os, itertools
from datetime import date

args = sys.argv[1:]
m = json.load(open(args[0]))
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
def opt(flag, default):
    return args[args.index(flag) + 1] if flag in args else default
profile = json.load(open(opt("--profile", os.path.join(root, "profiles", m.get("profile", "default") + ".json"))))
E, W, I = [], [], []
C = m.get("complaint", {}); M = m.get("matter", {})

# --- 1. required structure
for k in ["matter", "parties", "chronology", "claims", "damages", "elements", "complaint", "decisions", "open_questions"]:
    if k not in m: E.append(f"missing top-level key: {k}")
for k in ["intro", "sections", "counts", "prayer"]:
    if k not in C: E.append(f"complaint missing: {k}")

# --- 2. paragraph ids / refs
paras = []
for s in C.get("sections", []): paras += s.get("paragraphs", [])
for key in ("attorney_fees", "rule19c"):
    if C.get(key): paras += C[key].get("paragraphs", [])
for c in C.get("counts", []): paras += c.get("paragraphs", [])
ids = [p.get("id") for p in paras]
dups = {i for i in ids if ids.count(i) > 1}
if dups: E.append(f"duplicate paragraph ids: {sorted(dups)}")
if None in ids: W.append("some paragraphs lack an id (cannot be cited in the element map)")
idset = set(ids)
alltext = " ".join([C.get("intro", "")] + [p.get("text", "") + " " + " ".join(p.get("items", [])) for p in paras] + C.get("prayer", []))
for r in re.findall(r"\{\{ref:([\w-]+)\}\}", json.dumps(m)):
    if r not in idset: E.append(f"unresolved reference {{{{ref:{r}}}}}")

# --- 3. claims ↔ counts ↔ elements
counts_by_claim = {c.get("claim_id") for c in C.get("counts", [])}
for cl in m.get("claims", []):
    d = cl.get("decision", "")
    if d in ("PLEADED", "ALTERNATIVE"):
        if cl["id"] not in counts_by_claim: E.append(f"claim {cl['id']} ({cl['title']}) is {d} but has no count in the complaint")
        els = [e for e in m.get("elements", []) if e["claim"] == cl["id"]]
        if not els: E.append(f"claim {cl['id']} has no element map rows")
        for e in els:
            if not e.get("paras"): E.append(f"GAP: {cl['id']} element '{e['element']}' has no supporting paragraph")
            for p in e.get("paras", []):
                if p not in idset: E.append(f"element map for {cl['id']} cites missing paragraph id {p}")
        if d == "ALTERNATIVE":
            cnt = next((c for c in C.get("counts", []) if c.get("claim_id") == cl["id"]), None)
            if cnt and "alternative" not in (cnt.get("sub", "") + " ".join(p.get("text", "") for p in cnt.get("paragraphs", []))).lower():
                W.append(f"count for {cl['id']} is ALTERNATIVE but is not labeled as pleaded in the alternative (Rule 8(e))")
    elif not cl.get("rationale"):
        E.append(f"claim {cl['id']} ({cl['title']}) is {d or 'undecided'} with no rationale; never drop a suggested claim silently")
for c in C.get("counts", []):
    if c.get("claim_id") not in {cl["id"] for cl in m.get("claims", [])}: E.append(f"count '{c.get('title')}' has claim_id not in claims chart")

# --- 4. damages, reconciliation, tier (URCP 26(c)(3)-(4))
dm = m.get("damages", [])
total = round(sum(d["amount"] for d in dm), 2)
stated = M.get("client_stated_total")
if stated is not None and round(stated, 2) != total:
    W.append(f"damages total {total:,.2f} does not match client-stated total {stated:,.2f}; reconcile or explain in memo")
tier = 1 if total <= 50000 else (2 if total < 300000 else 3)
has_nonmonetary = any(k in alltext.lower() for k in ("injunct", "declar", "accounting", "specific performance"))
if total == 0 and has_nonmonetary: tier = 2
if M.get("tier") != tier: E.append(f"caption tier {M.get('tier')} but computed tier from undup. damages {total:,.2f} is {tier}")
if not re.search(r"Tier\s*%s\b" % M.get("tier"), alltext): E.append("body does not state the tier (URCP 8(a)/26(c)(3))")
if tier in (1, 2): I.append(f"Tier {tier} pleading waives damages above the tier cap unless amended (URCP 8(a)). Confirm with client.")
# dollar amounts in complaint must be derivable from damages items (single items, subset sums, or total)
amts = [round(d["amount"], 2) for d in dm]
derivable = set()
if len(amts) <= 16:
    for r in range(1, len(amts) + 1):
        for combo in itertools.combinations(amts, r): derivable.add(round(sum(combo), 2))
else: derivable = set(amts) | {total}
for s in re.findall(r"\$([\d,]+\.\d{2})", alltext):
    v = round(float(s.replace(",", "")), 2)
    context = {round(float(x), 2) for x in m.get("context_amounts", [])}
    if v not in derivable and v not in context and v not in (50000.00, 300000.00):
        W.append(f"complaint states ${s} which is not an item, subset sum, or total of the damages table; check arithmetic, or list it in context_amounts if it is a non-damages figure (e.g., a partial payment)")

# --- 5. rules-based content checks
fees_claimed = re.search(r"attorney(?:’|'|s)?\s*fee", " ".join(C.get("prayer", [])), re.I)
if fees_claimed:
    af = " ".join(p["text"] for p in (C.get("attorney_fees") or {}).get("paragraphs", []))
    if not af: E.append("prayer seeks attorney fees but no attorney-fee basis section (URCP 73(e): state basis, cite law or attach contract)")
    elif "5.4" not in af: E.append("attorney-fee section lacks the Rule 5.4 no-fee-sharing statement (URCP 73(e))")
if re.search(r"\b(contractor|subcontract|stucco|plumb|electric|roofing|construction|remodel|hvac)", alltext, re.I):
    if not re.search(r"58-55-604|licensed|license", alltext, re.I):
        E.append("construction/contractor facts but no licensure allegation (Utah Code § 58-55-604 requires alleging and proving licensure)")
    else: I.append("licensure allegation present; confirm license classifications cover every trade billed (e.g., electrical, plumbing)")
for c in C.get("counts", []):
    if re.search(r"fraud|misrepresent", c.get("title", ""), re.I):
        W.append(f"count '{c['title']}': confirm Rule 9(c) particularity (who, what, when, where, how) in the general allegations")
if not profile["drafting"].get("cite_case_law_in_complaint", False):
    hits = re.findall(r"\b\d{1,4}\s+(?:P\.\s?[23]d|P\.\s?3d|Utah\s?2d|U\.S\.)\s+\d+|\b(?:19|20)\d{2}\s+UT(?:\s+App)?\s+\d+", alltext)
    if hits: W.append(f"case citations appear in complaint but profile says no case law: {hits[:5]}")
brackets = re.findall(r"\[\[(.*?)\]\]", json.dumps(C))
I.append(f"{len(brackets)} bracketed fill-ins/unconfirmed facts remain (resolve before filing)")
if len(brackets) and not m.get("open_questions"): W.append("bracketed items exist but open_questions is empty")
if C.get("rule19c") is None: I.append("no URCP 19(c) statement: confirm there are no needed persons left unjoined")

# --- 6. process evidence (run log / review)
rl = m.get("run_log", [])
done = {r.get("module") for r in rl}
for mod in ["M1", "M2", "M3", "M4", "M5", "M6", "M7"]:
    if mod not in done: W.append(f"run_log has no entry for {mod} (module skipped or not logged)")
if profile["review"].get("fresh_agent_adversarial_review"):
    oc = [r for r in m.get("review_log", []) if r.get("lens") == "opposing_counsel"]
    if not oc: W.append("profile requires a fresh-agent opposing-counsel review but review_log has no opposing_counsel findings")
    elif not any(str(r.get("reviewer", "")).startswith(("agent:", "workflow:")) for r in oc):
        W.append("opposing-counsel findings lack an agent id (reviewer 'agent:<id>'); cannot confirm an independent subagent ran")


rep = {"ok": not E, "errors": E, "warnings": W, "info": I, "damages_total": total, "computed_tier": tier}
print(json.dumps(rep, indent=1)); sys.exit(0 if not E else 1)
