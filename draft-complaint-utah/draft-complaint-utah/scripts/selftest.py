#!/usr/bin/env python3
"""Self-test for the deterministic checks. Run after editing scripts: python3 scripts/selftest.py"""
import json, subprocess, copy, os, sys, tempfile
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = json.load(open(os.path.join(root, "assets", "sample-matter.json")))
def run(m):
    json.dump(m, open(os.path.join(tempfile.gettempdir(), "_selftest.json"), "w"))
    r = subprocess.run([sys.executable, os.path.join(root, "scripts", "validate_matter.py"), os.path.join(tempfile.gettempdir(), "_selftest.json")], capture_output=True, text=True)
    return r.returncode, json.loads(r.stdout)
cases = []
def case(name, mutate, expect_fail, needle):
    m = copy.deepcopy(base); mutate(m); code, rep = run(m)
    hit = any(needle in e for e in rep["errors"] + rep["warnings"])
    ok = (code == 1) == expect_fail and (hit or not needle)
    cases.append((name, ok)); print(("PASS " if ok else "FAIL ") + name)
case("clean sample passes", lambda m: None, False, "")
case("fees without RPC 5.4 statement", lambda m: m["complaint"]["attorney_fees"]["paragraphs"].pop(), True, "5.4")
case("wrong tier", lambda m: m["matter"].update(tier=1), True, "tier")
case("contractor without licensure", lambda m: m["complaint"]["sections"][2]["paragraphs"][0].update(text="Wasatch, a sign contractor, agreed to build signs."), True, "58-55-604")
case("unresolved ref", lambda m: m["complaint"]["counts"][0]["paragraphs"][0].update(text="See {{ref:nope}}."), True, "unresolved")
case("silently dropped claim", lambda m: m["claims"].append({"id": "c9", "title": "Fraud", "decision": "OMITTED"}), True, "silently")
case("element gap", lambda m: m["elements"][0].update(paras=[]), True, "GAP")
case("stray dollar figure", lambda m: m["complaint"]["sections"][2]["paragraphs"][1].update(text="Wasatch invoiced $61,000.00."), False, "61,000.00")
case("case cite in complaint", lambda m: m["complaint"]["counts"][0]["paragraphs"][0].update(text="See Jeffs v. Stubbs, 970 P.2d 1234."), False, "case citations")
sys.exit(0 if all(ok for _, ok in cases) else 1)
