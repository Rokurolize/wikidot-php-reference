#!/usr/bin/env python3
"""Structural comparator for the Size battery: reference render vs ftml dump."""
import json
import re
import sys

def load(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            out[row["id"]] = row.get("output", row.get("html", ""))
    return out

def norm(s):
    s = s.replace("\r\n", "\n")
    s = s.replace("<br />", "<br>")
    s = s.replace("<div >", "<div>")
    s = re.sub(r">\s+<", "><", s)
    s = s.strip()
    return s

def main():
    ref = load(sys.argv[1] if len(sys.argv) > 1 else "ref-render-before.jsonl")
    ftm = load(sys.argv[2] if len(sys.argv) > 2 else "ftml-dump.jsonl")
    ids = list(ref)
    raw_same = struct_same = 0
    diffs = []
    for cid in ids:
        a, b = ref.get(cid, ""), ftm.get(cid, "")
        if a == b:
            raw_same += 1
        if norm(a) == norm(b):
            struct_same += 1
        else:
            diffs.append((cid, a, b))
    print(f"cases={len(ids)} raw_same={raw_same} struct_same={struct_same} struct_diff={len(diffs)}")
    for cid, a, b in diffs:
        print(f"\n=== {cid} ===")
        print(f"REF: {a!r}")
        print(f"FTM: {b!r}")

if __name__ == "__main__":
    main()
