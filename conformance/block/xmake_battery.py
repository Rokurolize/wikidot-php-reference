#!/usr/bin/env python3
"""Generate the root-owned cross-rule interaction battery for the R2-block stage.

These are the seams the three per-rule batteries cannot own on their own:
a Toc reading headings inside divs, collapsibles and suppressed Iftags bodies,
heading anchor ids when the same heading text repeats, and a blockquote
containing headings, lists and footnote blocks (including the empty containers
the NOTES stage recorded live dropping). Every case is a whole document;
tagged cases carry a "tags" array consumed by both the reference harness and
the shared ftml dumper.
"""
import json

OUT = "conformance-refphp/block/xbattery.jsonl"

cases = []
def add(cid, src, tags=None):
    rec = {"id": cid, "source": src}
    if tags is not None:
        rec["tags"] = tags
    cases.append(rec)

# A. Toc computed over headings inside other constructs.
add("x-toc-basic", "+ Alpha\n++ Beta\n[[toc]]\n")
add("x-toc-before", "[[toc]]\n+ Alpha\n++ Beta\n")
add("x-toc-two", "[[toc]]\n+ One\n[[toc]]\n++ Two\n")
add("x-toc-in-div", "[[div]]\n+ In div\n[[/div]]\n+ Outside\n[[toc]]\n")
add("x-toc-in-collapsible", "[[collapsible]]\n+ In collapsible\n[[/collapsible]]\n+ Outside\n[[toc]]\n")
add("x-toc-in-iftags-drop", "[[iftags -alpha]]\n+ Hidden\n[[/iftags]]\n+ Visible\n[[toc]]\n", ["alpha"])
add("x-toc-in-iftags-keep", "[[iftags +alpha]]\n+ Kept\n[[/iftags]]\n+ Visible\n[[toc]]\n", ["alpha"])
add("x-toc-untagged-iftags", "[[iftags -alpha]]\n+ Hidden\n[[/iftags]]\n+ Visible\n[[toc]]\n")
add("x-toc-in-code", "[[code]]\n+ Literal\n[[/code]]\n+ Real\n[[toc]]\n")
add("x-toc-in-quote", "> + Quoted heading\n\n+ Real\n[[toc]]\n")
add("x-toc-in-toc-div", "[[div]]\n[[toc]]\n+ Inside\n[[/div]]\n+ Outside\n[[toc]]\n")
add("x-toc-float-right", "[[f>toc]]\n+ Alpha\n++ Beta\n")
add("x-toc-float-left", "[[f<toc]]\n+ Alpha\n++ Beta\n")
add("x-toc-attr", '[[toc class="mine"]]\n+ Alpha\n[[toc ]]\n')

# B. Heading anchors when heading text repeats or carries markup.
add("x-anchor-repeat", "+ Alpha\n+ Alpha\n[[toc]]\n")
add("x-anchor-repeat-levels", "+ Alpha\n++ Alpha\n+ Alpha\n[[toc]]\n")
add("x-anchor-markup", "+ **Bold** and [[http://example.com|link]]\n[[toc]]\n")
add("x-anchor-spaces", "+  Two spaces\n+ Trailing  \n[[toc]]\n")
add("x-anchor-across-containers", "[[div]]\n+ Same\n[[/div]]\n+ Same\n[[toc]]\n")
add("x-anchor-skips", "+ Level1\n++++ Level4\n[[toc]]\n")
add("x-anchor-collapsible-repeat", "[[collapsible]]\n+ Repeat\n[[/collapsible]]\n+ Repeat\n[[toc]]\n")
add("x-anchor-head-footnote", "+ Head [[footnote]]note[[/footnote]]\n[[toc]]\n[[footnoteblock]]\n")

# C. Blockquote containing headings, lists and footnote blocks.
add("x-bq-head", "[[blockquote]]\n+ Inside\n[[/blockquote]]\n+ Outside\n[[toc]]\n")
add("x-bq-list", "[[blockquote]]\n* one\n* two\n[[/blockquote]]\n")
add("x-bq-footnote", "[[blockquote]]\n[[footnote]]inside[[/footnote]]\n[[/blockquote]]\n[[footnoteblock]]\n")
add("x-bq-head-list-footnote", "[[blockquote]]\n+ Inside\n* item\n[[footnote]]note[[/footnote]]\n[[/blockquote]]\n[[toc]]\n[[footnoteblock]]\n")
add("x-bq-empty", "a\n[[blockquote]][[/blockquote]]\nb\n")
add("x-bq-empty-lines", "a\n[[blockquote]]\n\n[[/blockquote]]\nb\n")
add("x-bq-nested-head", "[[blockquote]]\n[[blockquote]]\n+ Deep\n[[/blockquote]]\n[[/blockquote]]\n[[toc]]\n")
add("x-bq-attr", '[[blockquote id="bq" class="c"]]text[[/blockquote]]\n')
add("x-bq-unterminated", "[[blockquote]]\ntext\n")
add("x-quote-head", "> + quoted\n\n+ real\n[[toc]]\n")
add("x-quote-list", "> * item\n\noutside\n")

# D. All three families in one document.
add("x-mix-bq-head-toc", "[[blockquote]]\n+ In quote\n[[/blockquote]]\n+ Outside\n[[toc]]\n")
add("x-mix-toc-in-bq", "[[blockquote]]\n[[toc]]\n+ Inside\n[[/blockquote]]\n")
add("x-mix-div-toc-iftags", "[[div]]\n+ In div\n[[toc]]\n[[/div]]\n[[iftags -alpha]]\n+ Hidden\n[[/iftags]]\n+ Visible\n", ["alpha"])

with open(OUT, "w", encoding="utf-8") as f:
    for rec in cases:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(f"wrote {len(cases)} cross-rule cases to {OUT}")
