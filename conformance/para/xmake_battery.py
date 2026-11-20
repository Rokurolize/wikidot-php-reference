#!/usr/bin/env python3
"""Generate root's R2-para cross-rule interaction battery (xbattery.jsonl).

Whole-document cases for the interactions no single rule owner can own: images
inside paragraphs, cells, captions and containers; paragraph formation around
every block family corrected so far; newline behavior inside containers; and
the two routed open items (tab space-run collapse, score-span paragraph
suppression) at interaction level. Sources are LF-only with no trailing
newline and no trailing whitespace, because Wikidot strips trailing whitespace
on save and saved_source_matches must hold.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xbattery.jsonl")

IMG = "[[image http://example.com/a.png]]"
IMG2 = "[[image http://example.com/b.png]]"

cases = []


def add(cid, source):
    cases.append({"id": cid, "source": source})


# A. Images in paragraph and text flow.
add("x01-image-alone", IMG)
add("x02-image-in-text-run", "before " + IMG + " after")
add("x03-image-between-paragraphs", "lead\n\n" + IMG + "\n\ntail")
add("x04-image-with-caption", IMG + "caption here[[/image]]")
add("x05-aligned-image-in-paragraph", "text\n\n[[=image http://example.com/a.png]]\n\nmore")
add("x06-image-with-link", '[[image http://example.com/a.png link="http://example.com/page"]]')
add("x07-two-images-one-paragraph", IMG + " " + IMG2)
add("x08-image-after-newline", "line one\n" + IMG + "\nline two")

# B. Images in cells, captions and containers.
add("x09-image-in-simple-cell", "|| " + IMG + " || b ||")
add("x10-image-in-adv-cell", "[[table]][[row]][[cell]]" + IMG + "[[/cell]][[/row]][[/table]]")
add("x11-image-in-div", '[[div class="box"]]\n' + IMG + "\n[[/div]]")
add("x12-image-in-collapsible", "[[collapsible]]\n" + IMG + "\n[[/collapsible]]")
add("x13-image-in-quote", "> " + IMG)
add("x14-image-caption-with-link", IMG + "click [[http://example.com|here]][[/image]]")
add("x15-image-caption-with-image", IMG + IMG2 + "[[/image]]")
add("x16-aligned-image-in-cell", "|| [[=image http://example.com/a.png]] || b ||")

# C. Paragraph formation around each corrected block family.
add("x17-text-div-text", "lead\n[[div]]inner[[/div]]\ntail")
add("x18-text-collapsible-text", "lead\n[[collapsible]]inner[[/collapsible]]\ntail")
add("x19-text-table-text", "lead\n|| a || b ||\ntail")
add("x20-text-adv-table-text", "lead\n[[table]][[row]][[cell]]a[[/cell]][[/row]][[/table]]\ntail")
add("x21-text-list-text", "lead\n* item\ntail")
add("x22-text-deflist-text", "lead\n: term : definition\ntail")
add("x23-text-heading-text", "lead\n= Heading =\ntail")
add("x24-text-footnoteblock-text", "lead[[footnote]]note[[/footnote]]\n[[footnoteblock]]\ntail")
add("x25-text-code-text", "lead\n[[code]]\nx\n[[/code]]\ntail")
add("x26-text-quote-text", "lead\n> quoted\ntail")
add("x27-div-text-div", "[[div]]a[[/div]]\nmid\n[[div]]b[[/div]]")
add("x28-heading-text-list", "= Heading =\nmid\n* item")
add("x29-text-toc-text", "lead\n[[toc]]\ntail")
add("x30-block-tabs-text", "[[div]]a[[/div]]\nword1\tword2\ntail")

# D. Newline behavior inside containers.
add("x31-newline-in-div", "[[div]]\nline1\nline2\n[[/div]]")
add("x32-newline-in-collapsible", "[[collapsible]]\nline1\nline2\n[[/collapsible]]")
add("x33-newline-in-simple-cell", "|| a\nb || c ||")
add("x34-newline-in-adv-cell", "[[table]][[row]][[cell]]a\nb[[/cell]][[/row]][[/table]]")
add("x35-newline-in-list", "* item\ncontinue")
add("x36-doubled-newline-in-div", "[[div]]\nline1\n\nline2\n[[/div]]")
add("x37-newline-in-quote", "> line1\n> line2")
add("x38-newline-in-caption", IMG + "cap1\ncap2[[/image]]")

# E. Routed open items at interaction level.
add("x39-score-span-alone", '[[span class="score"]]100[[/span]]')
add("x40-score-span-with-text", 'before\n[[span class="score"]]100[[/span]]\nafter')
add("x41-score-span-in-div", '[[div]]\n[[span class="score"]]100[[/span]]\n[[/div]]')
add("x42-tab-in-paragraph", "word1\tword2")
add("x43-tab-in-list", "* word1\tword2")
add("x44-tab-in-cell", "|| word1\tword2 || b ||")

# F. Malformed boundaries near blocks.
add("x45-unclosed-image-opener", "[[image http://example.com/a.png\n\n[[div]]x[[/div]]")
add("x46-image-caption-unclosed", IMG + "caption\n\nnext")

with open(OUT, "w", encoding="utf-8") as f:
    for c in cases:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
print("wrote", OUT, len(cases), "cases")
