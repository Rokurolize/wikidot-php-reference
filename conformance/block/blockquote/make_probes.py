#!/usr/bin/env python3
"""Focused live probes for shapes the ftml corpus pins do not settle."""
import json

C = []
def add(cid, src):
    C.append({"id": cid, "source": src})

# Note: a line whose entire content is ">" + trailing space cannot be saved
# verbatim on Wikidot (trailing whitespace is stripped), so the standalone
# marker+space shape is settled by the corpus pin, not by a saved-page probe.
add("marker-space-two-spaces", ">  text")
add("marker-tab", ">\ttext")
add("bare-marker-in-run", "> one\n>\n> two")
add("nospace-in-run", "> one\n>no\n> two")
add("nested-mixed", "> a\n>> b\n> c")
add("depth-skip", "> a\n>>> c")
add("block-form", "[[blockquote]]\ntext\n[[/blockquote]]")
add("quote-alias", "[[quote]]\ntext\n[[/quote]]")
add("block-attrs", '[[blockquote class="bq" id="q1"]]\ntext\n[[/blockquote]]')
add("block-unterminated", "[[blockquote]]\ntext")
add("quote-then-heading", "> q\n+ h")
add("quote-then-list", "> q\n* i")
add("quote-then-div", "> q\n[[div]]\nin\n[[/div]]")
# A space-prefixed marker (" > q") cannot be saved verbatim either; Wikidot
# strips the leading space on save, which corroborates the settled standing
# fact and needs no further probe.
add("marker-space-before-text", "> \nX")
add("inline-markup", "> **b** [http://example.com label]")
add("entities", "> &amp; &lt;")

with open("probe-cases.jsonl", "w", encoding="utf-8") as f:
    for row in C:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print("wrote", len(C), "probe cases")
