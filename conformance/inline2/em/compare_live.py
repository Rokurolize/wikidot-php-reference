#!/usr/bin/env python3
# Three-way comparison: reference render, ftml dumper html, and cached live
# saved-page html, over the Emphasis battery. Usage:
#   compare_live.py <ref-render.jsonl> <ftml-dump.jsonl> <captures.json> [label]
import json, sys, html as htmlmod

REF, FTML, CAP = sys.argv[1:4]

def jl(path, key):
    d = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        v = rec.get(key)
        if key == "output" and v is not None:
            v = v.replace("\\/", "/")
        if isinstance(v, str):
            v = v.rstrip("\n")
        d[rec["id"]] = v
    return d

ref = jl(REF, "output")
ftml = jl(FTML, "html")
caps = json.load(open(CAP, encoding="utf-8"))

def norm(s):
    if s is None:
        return None
    # Live capture HTML is already campaign-norm'd; normalize the two local
    # renderers to the same可比 surface: entity apostrophes and <br /> vs <br>.
    s = s.replace("<br />", "<br>").replace("<br/>", "<br>")
    s = s.replace("&#039;", "'").replace("&#39;", "'")
    return s.strip()

ids = sorted(set(ref) | set(ftml) | set(caps))
buckets = {"all3": [], "ref+live": [], "ftml+live": [], "ref+ftml": [], "all_disagree": [], "no_live": []}
for cid in ids:
    r, f = norm(ref.get(cid)), norm(ftml.get(cid))
    c = caps.get(cid)
    lv = norm(c.get("html")) if c else None
    valid = bool(c and c.get("valid") and c.get("saved_source_matches"))
    if not valid:
        buckets["no_live"].append(cid)
        continue
    eq_rl, eq_fl, eq_rf = r == lv, f == lv, r == f
    if eq_rl and eq_fl:
        buckets["all3"].append(cid)
    elif eq_rl and not eq_fl:
        buckets["ref+live"].append(cid)
    elif eq_fl and not eq_rl:
        buckets["ftml+live"].append(cid)
    elif eq_rf and not eq_rl:
        buckets["ref+ftml"].append(cid)
    else:
        buckets["all_disagree"].append(cid)

for k, v in buckets.items():
    print(f"{k:14s} {len(v):2d}: {' '.join(v)}")
print("--- disagreements detail ---")
for cid in ids:
    c = caps.get(cid)
    if not (c and c.get("valid") and c.get("saved_source_matches")):
        continue
    r, f, lv = norm(ref.get(cid)), norm(ftml.get(cid)), norm(c.get("html"))
    if r == lv and f == lv:
        continue
    print(f"### {cid}")
    print(f"  REF : {r!r}")
    print(f"  FTML: {f!r}")
    print(f"  LIVE: {lv!r}")
