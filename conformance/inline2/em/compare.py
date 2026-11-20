#!/usr/bin/env python3
# Normalize and compare two JSONL render streams (id -> output/html).
import json, sys

def load(path, key):
    d = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        val = rec.get(key)
        if key == "output" and val is not None:
            val = val.replace("\\/", "/")
        if isinstance(val, str):
            val = val.rstrip("\n")
        d[rec["id"]] = val
    return d

left = load(sys.argv[1], sys.argv[2])   # reference
right = load(sys.argv[3], sys.argv[4])  # ftml
ids = list(left)
same = 0
for cid in ids:
    a, b = left.get(cid), right.get(cid)
    if a == b:
        same += 1
        continue
    print(f"--- {cid} ---")
    print(f"  REF : {a!r}")
    print(f"  FTML: {b!r}")
print(f"\nSAME {same}/{len(ids)}   DIFF {len(ids)-same}/{len(ids)}")
