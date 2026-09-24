#!/usr/bin/env python3
"""Build the Working Papers workbook from matter.json (+ paranums from render_complaint.js).
Usage: python3 build_workpapers.py matter.json paranums.json out.xlsx
Tabs: README, Chronology, Claims, Element Map, Damages (live formulas), Decisions, Review Log, Open Questions, Run Log.
"""
import json, re, sys
from datetime import date
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

m = json.load(open(sys.argv[1])); pn = json.load(open(sys.argv[2])); out = sys.argv[3]
ids = pn["ids"]
def refs(text):
    if text is None: return ""
    text = str(text)
    text = re.sub(r"\{\{ref:([\w-]+)\}\}", lambda x: "¶" + str(ids.get(x.group(1), "??" + x.group(1))), text)
    return text
def plist(lst): return ", ".join("¶%s" % ids.get(i, "??" + i) for i in (lst or []))

HDR = PatternFill("solid", fgColor="1F3864"); HF = Font(bold=True, color="FFFFFF")
FLAG = PatternFill("solid", fgColor="FCE4D6"); INPUT = PatternFill("solid", fgColor="FFF2CC")
GREEN = PatternFill("solid", fgColor="E2EFDA"); GREY = PatternFill("solid", fgColor="EDEDED")
thin = Side(style="thin", color="BFBFBF"); BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
WRAP = Alignment(wrap_text=True, vertical="top")
wb = Workbook()
def sheet(title, headers, rows, widths, flagcol=None):
    ws = wb.create_sheet(title); ws.append(headers)
    for c in ws[1]: c.fill, c.font, c.alignment, c.border = HDR, HF, WRAP, BOX
    for r in rows: ws.append(r)
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment, c.border = WRAP, BOX
        if flagcol is not None and row[flagcol].value: row[flagcol].fill = FLAG
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"; return ws

M = m["matter"]; name = M.get("name", "Matter")
ws = wb.active; ws.title = "README"
for r in [[f"{name}: Complaint Working Papers"],
          [f"Generated {date.today().isoformat()} from matter.json by build_workpapers.py. AI-assisted work product for attorney review."],
          [""], ["Tab", "Contents", "Module"],
          ["Chronology", "Events, sources, AI-timeline comparison, complaint ¶, flags", "M1"],
          ["Claims", "Every candidate claim, decision, rationale, authority, risk", "M2"],
          ["Element Map", "Elements → authority → complaint ¶¶ (gaps flagged)", "M3"],
          ["Damages", "Principal (live formulas), tier check, illustrative 10% interest", "M4"],
          ["Decisions", "Judgment calls with alternatives and gate type", "M2–M7"],
          ["Review Log", "Findings from each review lens and dispositions", "M6"],
          ["Open Questions", "What the client/attorney must supply", "M7"],
          ["Run Log", "Which modules ran, in what mode, with which tool/agent", "All"],
          [""], ["¶ numbers are generated from paragraph IDs and stay correct when regenerated after edits."]]:
    ws.append(r)
ws["A1"].font = Font(bold=True, size=14)
for c in ws[4]: c.font = Font(bold=True)
ws.column_dimensions["A"].width = 18; ws.column_dimensions["B"].width = 80; ws.column_dimensions["C"].width = 12

sheet("Chronology", ["#", "Date", "Date basis", "Event", "Source", "AI-timeline comparison", "Complaint ¶", "Flag"],
      [[i + 1, e.get("date"), e.get("date_basis"), e.get("event"), e.get("source"), e.get("ai_comparison"), plist(e.get("paras")), e.get("flag")]
       for i, e in enumerate(m.get("chronology", []))], [4, 14, 16, 50, 22, 30, 14, 40], flagcol=7)

ws = sheet("Claims", ["ID", "Clause", "Claim", "By", "Against", "Decision", "Alt. to", "Suggested by", "Rationale", "Authority", "Risk"],
      [[c["id"], c.get("clause_id"), c["title"], ", ".join(c.get("by", [])), ", ".join(c.get("against", [])), c["decision"], ", ".join(c.get("alt_to", [])),
        c.get("suggested_by"), c.get("rationale"), c.get("authority"), c.get("risk")] for c in m.get("claims", [])],
      [6, 9, 28, 10, 10, 18, 8, 16, 40, 34, 34])
for row in ws.iter_rows(min_row=2):
    v = str(row[5].value or "")
    row[5].fill = GREEN if v in ("PLEADED", "ALTERNATIVE") else (FLAG if "DECISION" in v or "CONFIRM" in v else GREY)

rows = []
for el in m.get("elements", []):
    missing = [p for p in el.get("paras", []) if p not in ids]
    gap = "GAP: no ¶" if not el.get("paras") else ("BAD REF: " + ", ".join(missing) if missing else "")
    rows.append([el["claim"], el["element"], el.get("authority"), plist(el.get("paras")), el.get("note", ""), gap])
sheet("Element Map", ["Claim", "Element", "Authority", "Complaint ¶¶", "Notes", "Check"], rows, [8, 34, 34, 22, 40, 16], flagcol=5)

ws = wb.create_sheet("Damages")
ws.append(["Item", "Plaintiff", "Amount", "Due date (input)", "Days to as-of", "Interest @10% (illustrative)", "Claims", "Alt. group"])
for c in ws[1]: c.fill, c.font, c.alignment = HDR, HF, WRAP
dmg = m.get("damages", []); s = 2
for i, d in enumerate(dmg):
    r = s + i
    ws.append([d["item"], d.get("plaintiff"), d["amount"], d.get("due_date"), None, None, ", ".join(d.get("claims", [])), d.get("alternative_group", "")])
    ws.cell(r, 4).fill = INPUT
    ws.cell(r, 5).value = f'=IF(ISNUMBER(D{r}),$B${s+len(dmg)+4}-D{r},"")'
    ws.cell(r, 6).value = f'=IF(ISNUMBER(E{r}),ROUND(C{r}*0.1*E{r}/365,2),"")'
    try:
        y, mo, dd = map(int, str(d.get("due_date"))[:10].split("-")); ws.cell(r, 4).value = date(y, mo, dd); ws.cell(r, 4).number_format = "yyyy-mm-dd"
    except Exception: pass
e = s + len(dmg) - 1
ws.append([]); ws.append(["TOTAL PRINCIPAL (no duplication; URCP 26(c)(4))", "", f"=SUM(C{s}:C{e})", "", "Interest subtotal", f"=SUM(F{s}:F{e})"])
tot = e + 2
ws.append(["Client-stated total", "", M.get("client_stated_total"), "", "Reconciles?", f'=IF(ROUND(C{tot},2)=ROUND(C{tot+1},2),"MATCH","MISMATCH")'])
ws.append(["As-of date (input)", date.fromisoformat(M.get("as_of_date", date.today().isoformat()))])
ws.cell(tot + 2, 2).fill = INPUT; ws.cell(tot + 2, 2).number_format = "yyyy-mm-dd"
ws.append(["Tier (URCP 26(c)(3))", f'=IF(C{tot}<=50000,"Tier 1",IF(C{tot}<300000,"Tier 2","Tier 3"))', "", "Caption tier", M.get("tier")])
for r in range(s, tot + 2):
    for col in (3, 6): ws.cell(r, col).number_format = "$#,##0.00"
for col, w in zip("ABCDEFGH", [44, 14, 14, 16, 12, 18, 12, 10]): ws.column_dimensions[col].width = w

sheet("Decisions", ["Decision", "Chosen", "Alternative", "Why", "Gate"],
      [[d["decision"], d["chosen"], d.get("alternative"), d.get("why"), d.get("gate")] for d in m.get("decisions", [])], [24, 30, 26, 50, 10])
sheet("Review Log", ["Lens", "Finding", "Action", "Status", "Reviewer (agent id / inline)"],
      [[r.get("lens"), r.get("finding"), r.get("action"), r.get("status"), r.get("reviewer", "")] for r in m.get("review_log", [])], [18, 50, 50, 14, 22])
sheet("Open Questions", ["#", "Priority", "Question", "Who / where", "Affects"],
      [[i + 1, q.get("priority"), q.get("question"), q.get("who"), refs(q.get("affects"))] for i, q in enumerate(m.get("open_questions", []))], [4, 10, 70, 24, 18])
sheet("Run Log", ["Module", "Mode", "Inputs", "Tool / agent", "Timestamp", "Notes"],
      [[r.get("module"), r.get("mode"), r.get("inputs"), r.get("tool"), r.get("timestamp"), r.get("notes")] for r in m.get("run_log", [])], [10, 12, 40, 26, 20, 40])
wb.save(out); print(json.dumps({"ok": True, "out": out}))
