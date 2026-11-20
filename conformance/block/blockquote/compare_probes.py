#!/usr/bin/env python3
"""Three-way probe report: live (cached capture) vs reference vs ftml dumper."""
import json, re

def canon(s):
    s = s.replace("<br />", "<br>").replace("&#39;", "'")
    s = re.sub(r"\s+", " ", s)
    return s.strip()

caps = json.load(open("probe-captures.json"))
srcs = {k: v["source"] for k, v in caps.items()}
with open("probe-cases.jsonl", "w", encoding="utf-8") as f:
    for k, s in srcs.items():
        f.write(json.dumps({"id": k, "source": s}, ensure_ascii=False) + "\n")

def load(path, key):
    out = {}
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        out[r["id"]] = r.get(key, r.get("error", ""))
    return out

ref = load("ref-probe-render.jsonl", "output")
ftml = load("ftml-probe-dump.jsonl", "html")
ids = sorted(caps)
print(f"probes={len(ids)}")
counts = {"all3": 0, "ref_live": 0, "ftml_live": 0, "ref_ftml": 0, "none": 0}
for k in ids:
    live = caps[k]["html"]
    r, f = ref.get(k, "MISSING"), ftml.get(k, "MISSING")
    cr, cf, cl = canon(r), canon(f), canon(live)
    eq_rl, eq_fl, eq_rf = cr == cl, cf == cl, cr == cf
    if eq_rl and eq_fl:
        key = "all3"
    elif eq_rl:
        key = "ref_live"
    elif eq_fl:
        key = "ftml_live"
    elif eq_rf:
        key = "ref_ftml"
    else:
        key = "none"
    counts[key] += 1
    print(f"{k}: {key} (ref_live={eq_rl} ftml_live={eq_fl} ref_ftml={eq_rf})")
    if key != "all3":
        print("  LIVE:", repr(live)[:220])
        print("  REF :", repr(r)[:220])
        print("  FTL :", repr(f)[:220])
print("counts:", counts)
