#!/usr/bin/env python3
"""Compare live saved-page captures against reference and ftml on Bibitem probes."""
import json
import re
import sys

suffix = sys.argv[1] if len(sys.argv) > 1 else "before"


def load(p):
    return {r["id"]: r for r in (json.loads(l) for l in open(p, encoding="utf-8"))}


caps = json.load(open("captures.json", encoding="utf-8"))
ref = load(f"ref-probe-render-{suffix}.jsonl")
ft = load("ftml-probe-dump.jsonl")


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def bibitems(s):
    return re.findall(r'<div class="bibitem"[^>]*>.*?</div>', norm(s))


def cite_numbers(s):
    return re.findall(r'<a[^>]*class="bibcite"[^>]*>(\d+)</a>', s)


def error_spans(s):
    return re.findall(r'<span class="error-inline">.*?</span>', s)


n = 0
all3 = live_ref = live_ft = ref_ft = disagree = 0
rows = []
for cid in sorted(caps):
    c = caps[cid]
    live = c["html"]
    r = ref[cid].get("output", ref[cid].get("error", ""))
    f = ft[cid].get("html", "")
    lb, rb, fb = bibitems(live), bibitems(r), bibitems(f)
    lc, rc, fc = cite_numbers(live), cite_numbers(r), cite_numbers(f)
    le, re_, fe = error_spans(live), error_spans(r), error_spans(f)
    ok_r = (lb, lc, le) == (rb, rc, re_)
    ok_f = (lb, lc, le) == (fb, fc, fe)
    ok_rf = (rb, rc, re_) == (fb, fc, fe)
    rows.append((cid, ok_r, ok_f, ok_rf, lb, rb, fb))
    n += 1
    if ok_r and ok_f:
        all3 += 1
    if ok_r:
        live_ref += 1
    if ok_f:
        live_ft += 1
    if ok_rf:
        ref_ft += 1
    if not ok_r and not ok_f:
        disagree += 1

print(f"=== live comparison {suffix} ===")
print(f"probes: {n} (all valid/stable/source-matching)")
print(f"all-three agree at shape: {all3}/{n}")
print(f"live==reference shape: {live_ref}/{n}")
print(f"live==ftml shape: {live_ft}/{n}")
print(f"reference==ftml shape: {ref_ft}/{n}")
print(f"both-differ-from-live: {disagree}/{n}")
print("--- per-probe ---")
for cid, ok_r, ok_f, ok_rf, lb, rb, fb in rows:
    flag = "ALL3" if ok_r and ok_f else ("L+R" if ok_r else ("L+F" if ok_f else "DIFF"))
    print(f"{flag:4} {cid}: live={lb}")
    if not ok_r:
        print(f"     ref ={rb}")
    if not ok_f:
        print(f"     ftml={fb}")
