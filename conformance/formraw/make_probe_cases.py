#!/usr/bin/env python3
"""Generate live probe cases for the R2 Form/Raw/Rawold stage.

Each probe is a saved page whose rendered HTML is the oracle. The probe tool
creates one page per case with the given wikitext and captures it twice.
"""
import json

cases = []


def add(cid, source):
    cases.append({"id": cid, "source": source})


# Raw basics / escaping
add("raw-basic", "BEFORE @@raw **bold** [[link]]@@ AFTER")
add("raw-empty", "A @@@@ B")
add("raw-ws", "A @@   @@ B")
add("raw-entities", "@@\"double\" 'single' & < > <b>&amp;</b>@@")
add("raw-wikitext", "@@//italic// **bold** = H = * list@@")
add("raw-at-run", "A @@@x@@@ B @@@@x@@@@ C @@@@@x@@@@@ D")
add("raw-adjacent", "@@one@@@@two@@")
add("raw-unterm", "A @@never closed")
add("raw-lone", "A @@ B @@@ C")
add("raw-in-bold", "**before @@raw@@ after**")
add("raw-in-div", "[[div class=\"x\"]]\n@@raw@@\n[[/div]]")
add("raw-in-quote", "> @@raw@@")

# Rawold
add("old-basic", "A ``raw **bold**`` B")
add("old-empty", "A ```` B")
add("old-apostrophe", "A ``it's`` B")
add("old-wikitext", "``//italic// **bold** [[link]]``")
add("old-and-raw", "``old`` @@raw@@")

# Form
add("form-basic", "[[form]]\nfields:\n  name:\n    type: text\n    label: Name\n---\nname: Alice\n[[/form]]")
add("form-no-data", "[[form]]\nfields:\n  name:\n    type: text\n    label: Name\n---\n\n[[/form]]")
add("form-empty", "[[form]]\n\n---\n\n[[/form]]")
add("form-select", "[[form]]\nfields:\n  color:\n    type: select\n    label: Color\n    options:\n      r: Red\n      b: Blue\n---\ncolor: r\n[[/form]]")
add("form-wiki", "[[form]]\nfields:\n  note:\n    type: wiki\n    label: Note\n---\nnote: **bold**\n[[/form]]")
add("form-unterm", "[[form]]\nfields:\n  name:\n    type: text\n---\nname: x")
add("form-malformed", "[[form]]\nfields:\n  name: [broken\n---\nname: x\n[[/form]]")
add("form-no-sep", "[[form]]\nfields:\n  name:\n    type: text\n[[/form]]")

# Pipeline interactions
add("raw-in-code", "[[code]]\n@@raw@@\n[[/code]]")
add("code-in-raw", "@@[[code]]x[[/code]]@@")
add("form-in-code", "[[code]]\n[[form]]\nx\n---\ny\n[[/form]]\n[[/code]]")

with open("probe-cases.jsonl", "w", encoding="utf-8") as f:
    for c in cases:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
print(f"wrote {len(cases)} probe cases")
