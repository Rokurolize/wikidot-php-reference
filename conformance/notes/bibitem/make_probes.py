#!/usr/bin/env python3
"""Emit the Bibitem R2-notes live probe set as JSONL."""
import json

P = [
    ("p-empty-body", "[[bibliography]]\n: a :\n[[/bibliography]]"),
    ("p-empty-then-entry", "[[bibliography]]\n: a :\n: b : Bravo.\n[[/bibliography]]"),
    ("p-empty-blank-entry", "[[bibliography]]\n: a :\n\n: b : Bravo.\n[[/bibliography]]"),
    ("p-two-empty", "[[bibliography]]\n: a :\n: b :\n[[/bibliography]]"),
    ("p-dup", "Cite ((bibcite bell)).\n\n[[bibliography]]\n: bell : First bell.\n: bell : Second bell.\n: guy : Guy.\n[[/bibliography]]"),
    ("p-nested-markup", "[[bibliography]]\n: a : aa **bold** //ital// {{code}} end.\n[[/bibliography]]"),
    ("p-self-cite", "[[bibliography]]\n: a : See also ((bibcite a)).\n[[/bibliography]]"),
    ("p-nested-footnote", "[[bibliography]]\n: a : Source with a note[[footnote]]the note[[/footnote]].\n[[/bibliography]]"),
    ("p-uppercase-label", "[[bibliography]]\n: Alpha : Uppercase label.\n[[/bibliography]]"),
    ("p-digit-label", "[[bibliography]]\n: 2b : Digit-leading label.\n[[/bibliography]]"),
    ("p-hyphen-label", "((bibcite smith-2020))\n\n[[bibliography]]\n: smith-2020 : Never registered.\n[[/bibliography]]"),
    ("p-two-spaces-before-colon", "[[bibliography]]\n: a  : Alpha.\n[[/bibliography]]"),
    ("p-no-space-after-colon", "[[bibliography]]\n: a :Bravo.\n[[/bibliography]]"),
    ("p-title-option", "[[bibliography title=\"Works Cited\"]]\n: a : Alpha.\n[[/bibliography]]"),
    ("p-hide-option", "[[bibliography hide=\"true\"]]\n: a : Alpha.\n[[/bibliography]]"),
    ("p-forward-cite", "See ((bibcite a)).\n\n[[bibliography]]\n: a : Alpha.\n[[/bibliography]]"),
    ("p-special-chars", "[[bibliography]]\n: a : A & B < C > D \"q\" 's'.\n[[/bibliography]]"),
    ("p-span-inline", "[[bibliography]]\n: a : aa [[span]]bb[[/span]] cc\n[[/bibliography]]"),
    ("p-mixed-lines", "[[bibliography]]\n: a : Alpha.\n: b :Bravo.\n: c : Charlie.\n[[/bibliography]]"),
    ("p-trim-body", "[[bibliography]]\n: a :    Alpha source.   \n[[/bibliography]]"),
]

with open("probe-cases.jsonl", "w", encoding="utf-8") as fh:
    for cid, source in P:
        fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
print(f"wrote {len(P)} probes")
