#!/usr/bin/env python3
"""Generate the cached live-probe case list for the Date rule.

Sources are LF-only with trailing newlines stripped because Wikidot
normalizes them on save. The shared wikidot-probe CLI creates pages under
muse-probe-r2next-date- and captures saved anonymous page views.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe-cases.jsonl")

cases = [
    ("basic", "[[date 1216153821]]"),
    ("format-year", '[[date 1216153821 format="%Y"]]'),
    ("leading-zeros", '[[date 00001216153821 format="%Y"]]'),
    ("zero", "[[date 0]]"),
    ("negative", "[[date -1000]]"),
    ("huge-14", "[[date 99999999999999]]"),
    ("huge-20", "[[date 99999999999999999999]]"),
    ("neg-huge", "[[date -99999999999999]]"),
    ("plus-value", '[[date +1216153821 format="%Y"]]'),
    ("iso-date", "[[date 2009-12-25]]"),
    ("now", "[[date now]]"),
    ("dot", "[[date .]]"),
    ("blank", "[[date  ]]"),
    ("blank-format", '[[date  format="%Y"]]'),
    ("unquoted-format", "[[date 1216153821 format=%Y]]"),
    ("duplicate-format", '[[date 1216153821 format="%Y" format="%m"]]'),
    ("unknown-attr", '[[date 1216153821 foo="bar"]]'),
    ("empty-format", '[[date 1216153821 format=""]]'),
    ("agohover", '[[date 1216153821 format="%Y|agohover"]]'),
    ("g-format", '[[date 1216153821 format="%g"]]'),
    ("spaced-format", '[[date 1216153821 format="%d. %m. %Y"]]'),
    ("html-format", '[[date 1216153821 format="<b>&"]]'),
    ("raw-format", '[[date 0 format="@@a@@"]]'),
    ("case-upper", "[[DATE 1216153821]]"),
    ("midline", "before [[date 1216153821]] after"),
    ("unterminated", "[[date 1216153821"),
    ("comment-in-value", "[[date 1234[!--x--]567890]]"),
    ("comment-in-attr", '[[date 1216153821 format=[!-- x --]"%Y"]]'),
    ("tz-attr", '[[date 1216153821 format="%Y" tz="+8"]]'),
    ("two-dates", "[[date 1]] and [[date 2]]"),
    ("in-code", "[[code]]\n[[date 1216153821]]\n[[/code]]"),
    ("after-iframe", "[[iframe https://example.com/a]]\n[[date 1216153821]]"),
]

with open(OUT, "w", encoding="utf-8") as handle:
    for cid, source in cases:
        handle.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
print("wrote %d probe cases to %s" % (len(cases), OUT))
