#!/usr/bin/env python3
"""Derive root's live probe case files from the cross-rule battery.

Untagged set: every battery case, created as an ordinary saved page under
muse-probe-r2contain-x- (no tags). Tagged set: the five iftags seam cases
published with tags=["alpha"] through wikidot.py, because the probe CLI has
no tag subcommand. Sources have no trailing newline: Wikidot strips one on
save and the probe tool requires a byte-identical read-back.
"""
import json
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(line) for line in
        open(os.path.join(OUT_DIR, "xbattery.jsonl"), encoding="utf-8") if line.strip()]

untagged = []
tagged = []
IFTAGS = {"x12", "x13", "x14", "x15", "x16"}
for row in rows:
    src = row["source"]
    if src.endswith("\n"):
        raise SystemExit("source ends with a newline: " + row["id"])
    untagged.append({"id": row["id"], "source": src})
    if row["id"].split("-")[0] in IFTAGS:
        tagged.append({"id": row["id"] + "-tagged", "source": src, "tags": ["alpha"]})

for name, data in (("x-probe-cases.jsonl", untagged),
                   ("x-probe-tagged.jsonl", tagged)):
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print("wrote", name, len(data), "cases")
