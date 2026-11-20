#!/usr/bin/env python3
"""Compare reference render and ftml dumper outputs case by case.

Usage: compare.py REF_RENDER.jsonl FTML_DUMP.jsonl OUT.txt
Prints a raw-equality summary and a per-case block with both sides; a raw
mismatch is flagged DIFF. A light frame normalization (drop surrounding <p>,
collapse whitespace) is reported separately via the NORM marker.
"""
import json
import re
import sys

ref_path, dump_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

def load(path, key):
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            rows[r["id"]] = r.get(key)
    return rows

ref = load(ref_path, "output")
dump = load(dump_path, "html")

def norm(html):
    if html is None:
        return None
    s = html.strip()
    if s.startswith("<p>") and s.endswith("</p>") and s.count("<p>") == 1:
        s = s[3:-4]
    s = re.sub(r"\s+", " ", s)
    return s

exact_same = raw_same = norm_same = total = 0
lines = []
for cid in sorted(ref, key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
    total += 1
    r, f = ref.get(cid), dump.get(cid)
    if r == f:
        exact_same += 1
    if r is not None and f is not None and r.rstrip() == f.rstrip():
        raw_same += 1
    if norm(r) == norm(f):
        norm_same += 1
    lines.append(f"=== {cid} ===")
    lines.append(f"REF : {r!r}")
    lines.append(f"FTML: {f!r}")
    if r != f:
        lines.append("DIFF" + ("" if norm(r) == norm(f) else "+NORM"))
lines.insert(0, f"total={total} exact_equal={exact_same} rstrip_equal={raw_same} norm_equal={norm_same}")
with open(out_path, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
print(lines[0])
