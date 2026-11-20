#!/usr/bin/env python3
"""Three-way comparison of reference render, ftml dump and live captures for the
root-owned cross-rule interaction battery of the R2 module stage."""
import json, re, sys

root = "/home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh-r2mod/conformance-refphp/module/"

def load_jsonl(p):
    out = {}
    try:
        for line in open(root + p, encoding="utf-8"):
            r = json.loads(line)
            out[r["id"]] = r
    except FileNotFoundError:
        pass
    return out

def shape(s):
    if not isinstance(s, str):
        return s
    s = s.replace("\r\n", "\n").replace("<br />", "<br>")
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip("\n")

ref = load_jsonl(sys.argv[1] if len(sys.argv) > 1 else "x-ref-render-final.jsonl")
ftml = load_jsonl("x-ftml-dump.jsonl")
try:
    live = json.load(open(root + "captures-x.json", encoding="utf-8"))
except FileNotFoundError:
    live = {}

ids = sorted(ref)
print(f"cases={len(ids)} ref={len(ref)} ftml={len(ftml)} live={len(live)}")
agree_all = agree_live_ref = agree_live_ftml = agree_ref_ftml = 0
rows = []
for cid in ids:
    r = shape(ref[cid].get("output", "ERR:" + ref[cid].get("error", "")))
    f = shape(ftml.get(cid, {}).get("html", "MISSING"))
    lv = live.get(cid, {})
    l = shape(lv.get("html", "MISSING")) if lv else "MISSING"
    valid = lv.get("valid", False) if lv else False
    a_rf = r == f
    a_rl = valid and r == l
    a_fl = valid and f == l
    agree_ref_ftml += a_rf; agree_live_ref += a_rl; agree_live_ftml += a_fl
    agree_all += (a_rf and a_rl and a_fl)
    rows.append((cid, a_rl, a_rf, a_fl, valid, r, f, l))
print(f"all_three={agree_all} live==ref={agree_live_ref} live==ftml={agree_live_ftml} ref==ftml={agree_ref_ftml}")
for cid, a_rl, a_rf, a_fl, valid, r, f, l in rows:
    if not (a_rl and a_rf and a_fl):
        print(f"=== {cid} valid={valid} (live==ref:{a_rl} ref==ftml:{a_rf} live==ftml:{a_fl})")
        print(f"  live: {l[:200]!r}")
        print(f"  ref : {r[:200]!r}")
        print(f"  ftml: {f[:200]!r}")
