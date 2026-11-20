#!/usr/bin/env python3
"""Emit the Footnoteitem live probe set as whole-document JSONL."""
import json

P = [
    ("p-one", "A[[footnote]]Alpha[[/footnote]]\n\n[[footnoteblock]]"),
    ("p-two", "A[[footnote]]one[[/footnote]] B[[footnote]]two[[/footnote]]\n\n[[footnoteblock]]"),
    ("p-empty", "A[[footnote]][[/footnote]] B[[footnote]]plain[[/footnote]]\n\n[[footnoteblock]]"),
    ("p-empty-ws", "A[[footnote]]   [[/footnote]] B\n\n[[footnoteblock]]"),
    ("p-bold", "X[[footnote]]**bold** and //italic//[[/footnote]]\n\n[[footnoteblock]]"),
    ("p-multiline", "X[[footnote]]\nline one\nline two\n[[/footnote]]\n\n[[footnoteblock]]"),
    ("p-nested", "X[[footnote]]outer[[footnote]]inner[[/footnote]]tail[[/footnote]]\n\n[[footnoteblock]]"),
    ("p-block-first", "[[footnoteblock]]\n\nA[[footnote]]note A[[/footnote]]"),
    ("p-block-middle", "A[[footnote]]note A[[/footnote]]\n\n[[footnoteblock]]\n\nB[[footnote]]note B[[/footnote]]"),
    ("p-no-block", "A[[footnote]]note A[[/footnote]] and no block."),
    ("p-two-blocks", "A[[footnote]]A[[/footnote]]\n[[footnoteblock]]\n\nB[[footnote]]B[[/footnote]]\n[[footnoteblock]]"),
    ("p-title", "A[[footnote]]note[[/footnote]]\n\n[[footnoteblock title=\"My Notes\"]]"),
    ("p-title-empty", "A[[footnote]]note[[/footnote]]\n\n[[footnoteblock title=\"\"]]"),
    ("p-list-body", "X[[footnote]]\n* one\n* two\n[[/footnote]]\n\n[[footnoteblock]]"),
    ("p-quote-body", "X[[footnote]]\n> quoted\n[[/footnote]]\n\n[[footnoteblock]]"),
    ("p-html-special", "X[[footnote]]A \" B ' C & D < E > F[[/footnote]]\n\n[[footnoteblock]]"),
    ("p-unicode", "Café[[footnote]]résumé 日本語 🎯[[/footnote]]\n\n[[footnoteblock]]"),
    ("p-link", "X[[footnote]][http://example.com link][[/footnote]]\n\n[[footnoteblock]]"),
    ("p-with-bib", "A[[footnote]]note[[/footnote]] [[bibcite alpha]]\n\n[[bibliography]]\n[[bibitem alpha]]Entry[[/bibitem]]\n[[/bibliography]]\n\n[[footnoteblock]]"),
    ("p-unterminated", "X[[footnote]]bad no close\n\n[[footnoteblock]]"),
]

with open("probe-cases.jsonl", "w", encoding="utf-8") as fh:
    for cid, source in P:
        fh.write(json.dumps({"id": cid, "source": source.rstrip("\n")}, ensure_ascii=False) + "\n")
print("wrote", len(P), "probes")
