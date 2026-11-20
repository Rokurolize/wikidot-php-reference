#!/usr/bin/env python3
"""Compare reference render, ftml render and live captures for probe cases.

Live page content is the oracle. The known Stage-2 output-shaping surface
(leading/trailing page padding, <br /> vs <br>, tight newline joins) is
normalized away; everything else is a genuine rule-level disagreement.
"""
import json, re

root = "/home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh/conformance-refphp/formraw/"


def load(p):
    out = {}
    try:
        for line in open(root + p, encoding="utf-8"):
            r = json.loads(line)
            out[r["id"]] = r
    except FileNotFoundError:
        pass
    return out


ref = load("ref-probe-render.jsonl")
ftml = load("ftml-probe-dump.jsonl")
caps = json.load(open(root + "captures.json", encoding="utf-8"))
if isinstance(caps, dict) and "cases" in caps:
    caps = caps["cases"]


def shape(s):
    if not isinstance(s, str):
        return s or ""
    s = s.replace("\r\n", "\n").replace("<br />", "<br>")
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip("\n")


n = 0
ok_ref = ok_ftml = 0
diffs = []
for cid, c in caps.items():
    live = c.get("page_content") or c.get("content") or c.get("html") or ""
    r = ref.get(cid, {}).get("output", "MISSING")
    f = ftml.get(cid, {}).get("html", "MISSING")
    if "error" in ref.get(cid, {}):
        r = "ERROR:" + ref[cid]["error"]
    n += 1
    sr, sf, sl = shape(r), shape(f), shape(live)
    if sr == sl:
        ok_ref += 1
    if sf == sl:
        ok_ftml += 1
    if sr != sl:
        diffs.append((cid, r, f, live))
print("total=%d ref_match=%d ftml_match=%d ref_disagreements=%d" % (n, ok_ref, ok_ftml, len(diffs)))
for cid, r, f, l in diffs:
    print("=== %s\n  ref: %r\n  ftm: %r\n  live:%r" % (cid, r[:220], f[:220], l[:220]))
