#!/usr/bin/env python3
"""Generate root's R2-table follow-up interaction battery (xbattery2.jsonl).

Covers the three cross-rule shapes the Table owner handed to root (p08 strong
clipping at a cell boundary, p09 a [[ul]] run inside a simple cell, p10 a
[[div]] closer residual) plus nearby variants of the same inline-span and
block-in-cell seams. Sources are LF-only with no trailing newline.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xbattery2.jsonl")

cases = [
    ("y01-bold-crosses-cell", "|| **A1 || B2** || C3 ||\nx"),
    ("y02-italic-crosses-cell", "|| ''A1 || B2'' || C3 ||\nx"),
    ("y03-ul-in-simple-cell", "||[[ul]]\n* one\n* two\n[[/ul]] ||\n|| after ||\nx"),
    ("y04-ol-in-simple-cell", "||[[ol]]\n* one\n* two\n[[/ol]] ||\n|| after ||\nx"),
    ("y05-div-in-simple-cell", '||[[div class="x"]]\ninside\n[[/div]] ||\n|| after ||\nx'),
    ("y06-collapsible-in-simple-cell", "||[[collapsible]]\ninside\n[[/collapsible]] ||\n|| after ||\nx"),
    ("y07-note-crosses-cell", "|| a[[footnote]]note || b[[/footnote]] || c ||\nx\n\n[[footnoteblock]]"),
    ("y08-adv-div-in-cell", '[[table]][[row]][[cell]][[div class="x"]]\ninside\n[[/div]][[/cell]][[/row]][[/table]]\nx'),
    ("y09-adv-ul-in-cell", "[[table]][[row]][[cell]][[ul]]\n* one\n* two\n[[/ul]][[/cell]][[/row]][[/table]]\nx"),
    ("y10-bold-crosses-adv-cells", "[[table]][[row]][[cell]]**A1[[/cell]][[cell]]B2**[[/cell]][[/row]][[/table]]\nx"),
]

with open(OUT, "w", encoding="utf-8") as f:
    for cid, source in cases:
        f.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
print("wrote", OUT, len(cases), "cases")
