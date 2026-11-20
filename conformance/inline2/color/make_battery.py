#!/usr/bin/env python3
"""Emit the R2-inline2 Colortext whole-document battery as JSONL.

Each record is {"id": ..., "source": ...}. Case ids c01.. are stable and are
also used as live-probe page slugs under muse-probe-r2in2-color-. The cases
cover named colors, hex forms, CSS values, invalid/rejected colors, empty and
vanishing bodies, pairing and crossing with the sibling markers (** // __
--), unpaired and tripled ##, word boundaries, line breaks, block boundaries,
and container/cell seams. Newlines in sources are encoded by json.dumps.
"""
import json

CASES = [
    # Named colors
    ("c01", "##red|Apple##"),
    ("c02", "##blue|Blueberry##"),
    ("c03", "##orange|Orange##"),
    ("c04", "##DarkRed|Dark##"),
    ("c05", "##white|White##"),
    ("c06", "##aqua|Aqua##"),
    ("c07", "##grey|Grey##"),
    # Hex forms
    ("c08", "###fff|White##"),
    ("c09", "###cd3636|Cherry##"),
    ("c10", "##c00|Short##"),
    ("c11", "##FF0000|Red##"),
    ("c12", "##123456|Hex##"),
    ("c13", "###FFFF|Upper##"),
    ("c14", "##1234|Four##"),
    # CSS values admitted by live/ftml
    ("c15", "##rgb(241, 194, 50)|Mango##"),
    ("c16", "##var(--c-keyword)|Var##"),
    ("c17", "##rgb(var(--x))|VarRGB##"),
    ("c18", "##not-a-color|Text##"),
    ("c19", "##rgb(1, 2, 3)|A##"),
    ("c20", "##expression(alert(1))|Expr##"),
    # Invalid / rejected colors
    ("c21", "##rgba(10,20,30,.5)|A##"),
    ("c22", "##hsl(120, 50%, 25%)|A##"),
    ("c23", "##a_b|A##"),
    ("c24", "##red;background:blue|A##"),
    ("c25", "##url(javascript:alert(1))|A##"),
    ("c26", "##|gold|A##"),
    ("c27", "##|A##"),
    ("c28", "##||A##"),
    ("c29", "##not color"),
    # Empty / vanishing bodies
    ("c30", "##red|##"),
    ("c31", "##red| ##"),
    ("c32", "##red|{{}}##"),
    ("c33", "##red|   ##"),
    # Pairing / nesting with sibling markers
    ("c34", "##red|**bold**##"),
    ("c35", "##red|//italic//##"),
    ("c36", "##red|__under__##"),
    ("c37", "##red|--strike--##"),
    ("c38", "**##red|A##**"),
    ("c39", "##orange|**ORANGE##-PRIME:**"),
    ("c40", "##red|**a //b__c--d##"),
    # Unpaired and tripled ##
    ("c41", "##red|A"),
    ("c42", "red|A##"),
    ("c43", "##red|A####"),
    ("c44", "##red|A##blue|B##"),
    ("c45", "##red|A##green|B####blue|C##"),
    ("c46", "####red|A##"),
    ("c47", "##red##"),
    ("c48", "##blue|##red|a##"),
    # Word boundaries and inside words
    ("c49", "ab##red|cd##ef"),
    ("c50", "ab ##red|cd## ef"),
    ("c51", "x##red|A##y##blue|B##z"),
    ("c52", "## red | A ##"),
    ("c53", "##red|A ##blue|B## C##"),
    # Line breaks
    ("c54", "##red|A\nB##"),
    ("c55", "##red|A\n\nB##"),
    ("c56", "##red|A\nB\nC##"),
    ("c57", "##red|A##\n##blue|B##"),
    # Block boundaries
    ("c58", "##red|A\n\n[[div]]\nB\n[[/div]]\nC##"),
    ("c59", "> ##red|A##"),
    ("c60", "##red|A\n* item\nB##"),
    ("c61", "##red|A\n[[code]]\nB\n[[/code]]##"),
    ("c62", "##red|= Heading##"),
    # Container / cell seams
    ("c63", "[[div]]\n##red|A##\n[[/div]]"),
    ("c64", "##red|[[a href=\"x\"]]A[[/a]]##"),
    ("c65", "|| ##red|A||B## ||"),
    ("c66", "[[span]]##red|A##[[/span]]"),
    ("c67", "##darkred|[[##"),
]

with open("battery.jsonl", "w", encoding="utf-8") as fh:
    for case_id, source in CASES:
        fh.write(json.dumps({"id": case_id, "source": source}, ensure_ascii=False) + "\n")
print(f"wrote {len(CASES)} cases")
