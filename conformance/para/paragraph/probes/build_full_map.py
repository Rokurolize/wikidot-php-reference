#!/usr/bin/env python3
"""Build the capture map for all 26 probe pages.

The create CLI writes its map only on a fully successful run, and two runs
stopped on unsavable whitespace-only sources before that point. Every page
p01..p20 was reported created by a run whose source file matched the current
probe-cases.jsonl for those ids; p21..p26 come from probe-map-remaining.json.
The fullname rule is the CLI's prefix plus the case id, and capture only needs
fullname and source to verify the saved source byte-for-byte.
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
PREFIX = "muse-probe-r2para-pg-"
cases = [json.loads(l) for l in open(os.path.join(BASE, "probe-cases.jsonl"), encoding="utf-8")]
mapping = {}
for c in cases:
    mapping[c["id"]] = {"fullname": PREFIX + c["id"],
                        "source": c["source"], "action": "created"}
remaining_path = os.path.join(BASE, "probe-map-remaining.json")
if os.path.exists(remaining_path):
    mapping.update(json.load(open(remaining_path, encoding="utf-8")))
json.dump(mapping, open(os.path.join(BASE, "probe-map.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("wrote", len(mapping), "entries")
