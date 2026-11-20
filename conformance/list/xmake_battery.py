#!/usr/bin/env python3
"""Root's R2-list cross-rule interaction battery.

Whole-document cases for the seams no single rule owner owns: lists inside
divs, collapsibles, blockquotes and tabview; deflists inside bibliography
bodies; lists interrupted by headings, toc, footnotes and other blocks;
the empty-list-container question routed here by the NOTES and CONTAIN
stages; and list items containing the span-shaped inline family. Optional
per-case "tags" mirror the shared harness protocol.
"""
import json
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

C = []
def add(cid, src, tags=None):
    row = {"id": cid, "source": src}
    if tags is not None:
        row["tags"] = tags
    C.append(row)

# A. Lists inside containers.
add("x01-list-in-div", "[[div class=x]]\n* one\n* two\n[[/div]]")
add("x02-numbered-in-div", "[[div class=x]]\n# one\n# two\n[[/div]]")
add("x03-nested-list-in-div", "[[div class=x]]\n* one\n * nested\n* two\n[[/div]]")
add("x04-list-in-collapsible", "[[collapsible]]\n* one\n* two\n[[/collapsible]]")
add("x05-list-in-collapsible-labeled", "[[collapsible show=show hide=hide]]\n# one\n# two\n[[/collapsible]]")
add("x06-list-in-quote", "> * one\n> * two")
add("x07-nested-list-in-quote", "> * one\n>  * nested\n> * two")
add("x08-list-in-tab", "[[tabview]]\n[[tab title=A]]\n* one\n* two\n[[/tab]]\n[[/tabview]]")
add("x09-div-in-list-item", "[[div class=x]]\ninside\n[[/div]]\n* one\n* two")
add("x10-list-then-div", "* one\n* two\n[[div class=x]]\nafter\n[[/div]]")
add("x11-quote-then-list", "> quoted\n* one\n* two")
add("x12-collapsible-in-list-item", "* one [[collapsible]]inside[[/collapsible]]\n* two")

# B. Deflists inside bibliography bodies and containers.
add("x13-deflist-in-bib", "((bibcite a))\n[[bibliography]]\n: a : Alpha\n[[/bibliography]]")
add("x14-deflist-multi-bib", "((bibcite a)) ((bibcite b))\n[[bibliography]]\n: a : Alpha\n: b : Bravo\n[[/bibliography]]")
add("x15-deflist-bib-colon", "((bibcite a))\n[[bibliography]]\n: a: Alpha: with colon\n[[/bibliography]]")
add("x16-deflist-in-div", "[[div class=x]]\n: term : definition\n[[/div]]")
add("x17-deflist-in-quote", "> : term : definition")
add("x18-deflist-in-collapsible", "[[collapsible]]\n: term : definition\n[[/collapsible]]")
add("x19-bib-then-deflist", "[[bibliography]]\n: a : Alpha\n[[/bibliography]]\n: b : Bravo")
add("x20-deflist-then-bib", ": b : Bravo\n[[bibliography]]\n: a : Alpha\n[[/bibliography]]")

# C. Lists interrupted by headings, toc and footnote blocks.
add("x21-list-heading", "* one\n== Heading ==\n* two")
add("x22-list-toc", "* one\n[[toc]]\n* two")
add("x23-list-footnote", "* one[[footnote]]note[[/footnote]]\n* two\n[[footnoteblock]]")
add("x24-list-footnoteblock", "* one\n[[footnoteblock]]\n* two")
add("x25-list-hr", "* one\n----\n* two")
add("x26-list-code", "* one\n[[code]]\ncode\n[[/code]]\n* two")
add("x27-deflist-heading", ": term : definition\n== Heading ==\n: other : more")
add("x28-list-quote-interrupt", "* one\n> quoted\n* two")
add("x29-heading-then-list", "== Heading ==\n* one\n* two")

# D. Empty-list-container question routed here by NOTES and CONTAIN.
add("x30-empty-bullet", "* ")
add("x31-empty-number", "# ")
add("x32-empty-items-mixed", "* a\n* \n* b")
add("x33-whitespace-only-item", "*   \t ")
add("x34-empty-nested", "* one\n * \n* two")
add("x35-empty-deflist-term", ":  : definition")
add("x36-empty-deflist-def", ": term :  ")

# E. List items containing the span-shaped inline family.
add("x37-span-in-item", "[[span class=a]]A[[/span]]\n* one\n* two")
add("x38-span-cross-item", "* [[span class=a]]one\n* two[[/span]]")
add("x39-size-cross-item", "* [[size 12px]]one\n* two[[/size]]")
add("x40-color-cross-item", "* ##red|one\n* two##")
add("x41-strike-in-item", "* --one--\n* two")
add("x42-bold-in-item", "* **one**\n* two")
add("x43-span-nested-in-item", "* one [[span class=a]]A[[size 12px]]B[[/span]]C[[/size]]\n* two")

# F. Controls and tag seams.
add("x44-list-plain-control", "* one\n* two")
add("x45-iftags-suppressed-list", "[[iftags +alpha]]\n* one\n* two\n[[/iftags]]\nvisible", tags=[])
add("x46-iftags-active-list", "[[iftags +alpha]]\n* one\n* two\n[[/iftags]]\nvisible", tags=["alpha"])

with open(os.path.join(OUT_DIR, "xbattery.jsonl"), "w", encoding="utf-8") as f:
    for row in C:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print("wrote", len(C), "cross-rule interaction cases")
