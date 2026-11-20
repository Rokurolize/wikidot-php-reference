#!/usr/bin/env python3
"""Compare reference render vs ftml legacy html for the R2 Code battery.

Produces a readable table. Two columns:
  strict  : exact byte equality
  shaped  : equality after normalizing the known output-shaping surface
            (reference's leading/trailing newline padding, blank-line joins,
            <br /> -> <br>, and CRLF -> LF). These are frame-level conventions
            catalogued in R2-INCLUDE.md and R2-FRAME.md, not Code-rule behavior.
"""
import json, re

root = "/home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh/conformance-refphp/code/"


def load(p):
    return {r["id"]: r for r in (json.loads(l) for l in open(root + p, encoding="utf-8"))}


ref = load("ref-render.jsonl")
ftml = load("ftml-dump.jsonl")


def shape(s):
    if not isinstance(s, str):
        return s
    s = s.replace("\r\n", "\n")
    s = s.replace("<br />", "<br>")
    # reference pads token splice boundaries with \n\n and the render rule
    # returns "\n...\n\n"; collapse runs of 2+ newlines to 1 for comparison
    s = re.sub(r"\n{2,}", "\n", s)
    s = s.strip("\n")
    return s


strict = 0
shaped = 0
diffs = []
for cid in ref:
    r = ref[cid].get("output", "ERR:" + ref[cid].get("error", ""))
    f = ftml[cid].get("html", "ERR")
    st = r == f
    sh = shape(r) == shape(f)
    strict += st
    shaped += sh
    if not sh:
        diffs.append((cid, r, f))

print(f"total={len(ref)} strict={strict} shaped={shaped} diffs={len(diffs)}")
print()
for cid, r, f in diffs:
    print("===", cid, "===")
    print("  ref:", repr(r[:400]))
    print("  ftm:", repr(f[:400]))
