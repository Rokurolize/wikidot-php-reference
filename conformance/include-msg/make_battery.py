#!/usr/bin/env python3
import json
from pathlib import Path

cases = [
    ("im01", "[[include no-such-page]]"),
    ("im02", "[[include :no-such-page]]"),
    ("im03", "[[include :cat:sub:no-such-page]]"),
    ("im04", "[[include cat:no-such-page]]"),
    ("im05", "[[include :::]]"),
    ("im06", "[[include :foo:bar]]"),
    ("im07", "[[include :scp-jp.wikidot.com:other-page]]"),
    ("im08", "[[include :sandbox-for-codex:no-such-page]]"),
    ("im09", "[[include :]]"),
    ("im10", "[[include ---]]"),
    ("im11", "[[include :site:]]"),
    ("im12", "[[include ::page]]"),
    ("im13", "[[include no-such-page var=1]]"),
    ("im14", "Before\n\n[[include no-such-page]]\n\nAfter"),
    ("im15", "[[include include-target]]\n\n[[include no-such-page]]"),
]

out_path = Path(__file__).resolve().parent / "battery.jsonl"
with out_path.open("w", encoding="utf-8") as f:
    for cid, src in cases:
        f.write(json.dumps({"id": cid, "source": src}, ensure_ascii=False) + "\n")
print(f"Wrote {len(cases)} cases to {out_path}")
