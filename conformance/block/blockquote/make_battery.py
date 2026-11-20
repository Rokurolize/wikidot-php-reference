#!/usr/bin/env python3
"""Build the Blockquote R2 differential battery (JSONL {"id","source"[,"tags"]})."""
import json

C = []
def add(cid, src, tags=None):
    row = {"id": cid, "source": src}
    if tags is not None:
        row["tags"] = tags
    C.append(row)

# --- basic > quote lines -------------------------------------------------
add("bq01-simple", "> quote")
add("bq02-two-lines", "> one\n> two")
add("bq03-nospace", ">no space")
add("bq04-marker-only", ">")
add("bq05-marker-space", "> ")
add("bq06-at-doc-start", "> first line")
add("bq07-leading-blank", "\n> quote")
add("bq08-tab-after-marker", ">\tquote")

# --- nesting depth and mixed nesting ------------------------------------
add("bq09-space-nested", "> > nested")
add("bq10-tight-nested", ">> nested")
add("bq11-depth3-space", "> > > three")
add("bq12-depth3-tight", ">>> three")
add("bq13-mixed-up", "> one\n>> two\n>>> three")
add("bq14-mixed-down", ">>> three\n>> two\n> one")
add("bq15-mixed-updown", "> one\n>> two\n> three\n>>> four\n>> five\n> six")
add("bq16-depth-skip", "> one\n>>> three")
add("bq17-depth4", "> one\n>> two\n>>> three\n>>>> four")

# --- native [[blockquote]] / [[quote]] block ----------------------------
add("bq18-block-basic", "[[blockquote]]\ntext\n[[/blockquote]]")
add("bq19-block-quote-alias", "[[quote]]\ntext\n[[/quote]]")
add("bq20-block-attr-class", '[[blockquote class="bq"]]\ntext\n[[/blockquote]]')
add("bq21-block-attr-style", '[[blockquote style="color: red;"]]\ntext\n[[/blockquote]]')
add("bq22-block-attr-id", '[[blockquote id="q1"]]\ntext\n[[/blockquote]]')
add("bq23-block-unterminated", "[[blockquote]]\ntext")
add("bq24-block-with-marker", "[[blockquote]]\n> quote\n[[/blockquote]]")
add("bq25-block-inline", "[[blockquote]]text[[/blockquote]]")
add("bq26-block-empty", "[[blockquote]][[/blockquote]]")
add("bq27-block-mixed-case", "[[Blockquote]]\ntext\n[[/blockquote]]")
add("bq28-block-bogus-attr", '[[blockquote bogus="x"]]\ntext\n[[/blockquote]]')

# --- quote lines adjacent to other blocks ------------------------------
add("bq29-quote-then-heading", "> quote\n+ heading")
add("bq30-heading-then-quote", "+ heading\n> quote")
add("bq31-quote-then-list", "> quote\n* item")
add("bq32-list-then-quote", "* item\n> quote")
add("bq33-quote-then-div", "> quote\n[[div]]\ninside\n[[/div]]")
add("bq34-div-then-quote", "[[div]]\ninside\n[[/div]]\n> quote")
add("bq35-quote-then-code", "> quote\n[[code]]\ncode\n[[/code]]")
add("bq36-blank-in-run", "> one\n\n> two")
add("bq37-quote-then-para", "> quote\nplain paragraph")
add("bq38-para-then-quote", "plain paragraph\n> quote")

# --- malformed and settled shapes --------------------------------------
add("bq39-space-prefixed-marker", " > quote")
add("bq40-quote-midline", "text > quote")
add("bq41-double-space-after-marker", ">  quote")
add("bq42-inline-bold", "> **bold** quote")
add("bq43-inline-link", "> [http://example.com label]")
add("bq44-wikitext-body", "> a [[div]] b")
add("bq45-unterminated-deep", ">>> three\n>> two")
add("bq46-shallower-after-run", "> one\n>> two\nplain")
add("bq47-entities", "> &amp; &lt; &#39;")
add("bq48-unicode", "> café 日本語")

# --- mixed nesting across block and quote forms ------------------------
add("bq49-quote-around-block", "> before\n[[blockquote]]\ninner\n[[/blockquote]]\n> after")
add("bq50-block-around-quote", "[[blockquote]]\n> inner quote\n[[/blockquote]]")

with open("battery.jsonl", "w", encoding="utf-8") as f:
    for row in C:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print("wrote", len(C), "cases")
