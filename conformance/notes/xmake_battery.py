#!/usr/bin/env python3
"""Generate the root-owned cross-rule interaction battery for the R2-notes stage.

These are the document-state seams the six per-rule batteries cannot own:
footnote numbering inside other constructs (divs, collapsibles, suppressed
Iftags bodies, included content), the footnoteblock's position relative to the
notes it collects, bibliography ordering, citations to entries defined later,
duplicate bibitem labels, and the footnote family and bibliography family in
one document. Every case is a whole document. Tagged cases carry a "tags" array
consumed by both the reference harness and the shared ftml dumper.
"""
import json

OUT = "conformance-refphp/notes/xbattery.jsonl"

cases = []
def add(cid, src, tags=None):
    rec = {"id": cid, "source": src}
    if tags is not None:
        rec["tags"] = tags
    cases.append(rec)

# A. Footnote numbering inside other constructs.
add("x-fn-in-div", "[[div]]\nfirst [[footnote]]in div[[/footnote]] text\n[[/div]]\nsecond [[footnote]]outside[[/footnote]]\n[[footnoteblock]]\n")
add("x-fn-in-collapsible", "[[collapsible]]\n[[footnote]]in collapsible[[/footnote]]\n[[/collapsible]]\n[[footnote]]outside[[/footnote]]\n[[footnoteblock]]\n")
add("x-fn-in-iftags-drop", "[[iftags -alpha]]\n[[footnote]]suppressed[[/footnote]]\n[[/iftags]]\n[[footnote]]kept[[/footnote]]\n[[footnoteblock]]\n", ["alpha"])
add("x-fn-in-iftags-keep", "[[iftags +alpha]]\n[[footnote]]kept inside[[/footnote]]\n[[/iftags]]\n[[footnote]]outside[[/footnote]]\n[[footnoteblock]]\n", ["alpha"])
add("x-fn-around-iftags", "[[footnote]]before[[/footnote]]\n[[iftags -alpha]]\n[[footnote]]hidden[[/footnote]]\n[[/iftags]]\n[[footnote]]after[[/footnote]]\n[[footnoteblock]]\n", ["alpha"])
add("x-fn-in-include", "[[include muse-probe-g14-target]]\n[[footnote]]after include[[/footnote]]\n[[footnoteblock]]\n")
add("x-fn-in-code", "[[code]]\n[[footnote]]literal[[/footnote]]\n[[/code]]\nreal [[footnote]]note[[/footnote]]\n[[footnoteblock]]\n")
add("x-fn-in-quote", "> quoted [[footnote]]in quote[[/footnote]]\nplain [[footnote]]outside[[/footnote]]\n[[footnoteblock]]\n")
add("x-fn-in-list", "* item [[footnote]]in list[[/footnote]]\n* second\nplain [[footnote]]outside[[/footnote]]\n[[footnoteblock]]\n")

# B. Footnoteblock position relative to notes.
add("x-fn-block-before", "[[footnoteblock]]\nfirst [[footnote]]one[[/footnote]]\nsecond [[footnote]]two[[/footnote]]\n")
add("x-fn-block-between", "first [[footnote]]one[[/footnote]]\n[[footnoteblock]]\nsecond [[footnote]]two[[/footnote]]\n")
add("x-fn-block-after", "first [[footnote]]one[[/footnote]]\nsecond [[footnote]]two[[/footnote]]\n[[footnoteblock]]\n")
add("x-fn-block-multiple", "first [[footnote]]one[[/footnote]]\n[[footnoteblock]]\nsecond [[footnote]]two[[/footnote]]\n[[footnoteblock]]\n")
add("x-fn-block-none", "first [[footnote]]one[[/footnote]]\nsecond [[footnote]]two[[/footnote]]\n")
add("x-fn-block-two-before", "[[footnoteblock]]\n[[footnoteblock]]\n[[footnote]]one[[/footnote]]\n")
add("x-fn-block-empty", "no notes here\n[[footnoteblock]]\n")
add("x-fn-block-title", "[[footnote]]one[[/footnote]]\n[[footnoteblock title=\"Custom\"]]\n")
add("x-fn-block-title-empty", "[[footnote]]one[[/footnote]]\n[[footnoteblock title=\"\"]]\n")

# C. Bibliography ordering and resolution.
add("x-bib-def-order", "[[bibliography]]\n: alpha : Alpha text\n: beta : Beta text\n: gamma : Gamma text\n[[/bibliography]]\nCite ((bibcite gamma)) and ((bibcite alpha)).\n")
add("x-bib-unordered-labels", "[[bibliography]]\n: zeta : Zeta text\n: alpha : Alpha text\n: mu : Mu text\n[[/bibliography]]\nCite ((bibcite mu)) and ((bibcite zeta)).\n")
add("x-bib-cite-before", "Cite ((bibcite gamma)) then ((bibcite alpha)) then ((bibcite beta)).\n[[bibliography]]\n: alpha : Alpha text\n: beta : Beta text\n: gamma : Gamma text\n[[/bibliography]]\n")
add("x-bib-cite-after", "[[bibliography]]\n: alpha : Alpha text\n: beta : Beta text\n[[/bibliography]]\nCite ((bibcite beta)) then ((bibcite alpha)).\n")
add("x-bib-dup-label", "[[bibliography]]\n: k : First k\n: k : Second k\n[[/bibliography]]\nCite ((bibcite k)).\n")
add("x-bib-undefined", "Cite ((bibcite missing)) with no such entry.\n[[bibliography]]\n: k : A real entry\n[[/bibliography]]\n")
add("x-bib-multi-block", "[[bibliography]]\n: a : Entry A\n[[/bibliography]]\nBetween.\n[[bibliography]]\n: b : Entry B\n[[/bibliography]]\nCite ((bibcite a)) and ((bibcite b)).\n")
add("x-bib-title", "[[bibliography title=\"References\"]]\n: k : Entry text\n[[/bibliography]]\nCite ((bibcite k)).\n")
add("x-bib-empty", "No entries.\n[[bibliography]]\n[[/bibliography]]\n")
add("x-bib-empty-body", "[[bibliography]]\n: k : \n[[/bibliography]]\nCite ((bibcite k)).\n")

# D. Footnote family and bibliography family in one document.
add("x-mix-fn-bib", "[[footnote]]note one[[/footnote]] and ((bibcite k)).\n[[bibliography]]\n: k : Entry k\n[[/bibliography]]\n[[footnoteblock]]\n")
add("x-mix-bibcite-in-fn", "[[footnote]]see ((bibcite k))[[/footnote]]\n[[bibliography]]\n: k : Entry k\n[[/bibliography]]\n[[footnoteblock]]\n")
add("x-mix-fn-in-bib", "[[bibliography]]\n: k : Entry with [[footnote]]nested note[[/footnote]]\n[[/bibliography]]\nCite ((bibcite k)).\n[[footnoteblock]]\n")
add("x-mix-blocks-interleaved", "[[footnote]]fn[[/footnote]]\n[[bibliography]]\n: k : Entry\n[[/bibliography]]\n[[footnoteblock]]\nCite ((bibcite k)).\n")
add("x-mix-bibcite-in-block", "[[footnote]]note about ((bibcite k))[[/footnote]]\n[[bibliography]]\n: k : Entry k\n[[/bibliography]]\n[[footnoteblock]]\n")

# E. Nested markup and malformed/unterminated forms.
add("x-fn-nested-strong", "[[footnote]]**bold** and //italic// text[[/footnote]]\n[[footnoteblock]]\n")
add("x-bib-nested-markup", "[[bibliography]]\n: k : **bold** text\n[[/bibliography]]\nCite ((bibcite k)).\n")
add("x-fn-unterminated", "[[footnote]]no closing tag\n[[footnoteblock]]\n")
add("x-bib-unterminated", "[[bibliography]]\n: k : no closing tag\n")
add("x-fn-empty-body", "[[footnote]][[/footnote]]\n[[footnoteblock]]\n")
add("x-bib-cite-malformed", "Cite ((bibcite K)) and ((bibcite k)) and ((bibcite)).\n[[bibliography]]\n: k : Entry k\n[[/bibliography]]\n")

with open(OUT, "w", encoding="utf-8") as f:
    for rec in cases:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(f"wrote {len(cases)} cases to {OUT}")
