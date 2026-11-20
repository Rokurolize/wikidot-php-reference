#!/usr/bin/env python3
"""Generate the R2 Form/Raw/Rawold differential battery as JSONL.

Every record is {"id", "source"}. Sources are literal wikitext; escapes are
only those needed to write the Python string. The battery covers Raw edge
forms, Rawold shapes, Form blocks, and pipeline interactions with Code/Include.
"""
import json

cases = []


def add(cid, source):
    cases.append({"id": cid, "source": source})


# --- Raw: basic and empty forms ----------------------------------------------
add("raw-basic", "before @@raw **bold** [[link]]@@ after")
add("raw-basic-inline", "@@hello@@")
add("raw-empty", "a @@@@ b")
add("raw-ws-only", "a @@   @@ b")
add("raw-tab-body", "a @@\t@@ b")
add("raw-multiline", "before\n@@line one\nline two@@\nafter")
add("raw-multiline-leading", "@@\nindented\n@@")
add("raw-nbsp", "@@\u00a0x\u00a0@@")

# --- Raw: @@ runs, unterminated, lone @@ ------------------------------------
add("raw-triple-open", "a @@@x@@@ b")
add("raw-quad", "a @@@@x@@@@ b")
add("raw-five-run", "a @@@@@x@@@@@ b")
add("raw-at-end", "a @@x@@@ b")
add("raw-at-start", "a @@@x@@ b")
add("raw-inner-at", "@@x@y@@")
add("raw-adjacent", "@@one@@@@two@@")
add("raw-unterminated", "a @@never closed")
add("raw-lone", "a @@ b")
add("raw-two-lone", "a @@ b @@ c")
add("raw-closer-only", "a @@ b @@@ c")

# --- Raw: bodies containing wikitext, brackets, quotes, HTML ----------------
add("raw-wikitext", "@@//italic// **bold** __under__++strikethrough++@@")
add("raw-brackets", "@@[[wikilink]] [[/bad]]@@")
add("raw-quotes", "@@\"double\" 'single' & < >@@")
add("raw-html", "@@<b>bold</b> <script>alert(1)</script>@@")
add("raw-entities", "@@&amp; &lt; &quot; &#39;@@")
add("raw-code-markup", "@@[[code]]inner[[/code]]@@")
add("raw-form-markup", "@@[[form]]x---y[[/form]]@@")
add("raw-heading", "@@= Heading =@@")
add("raw-list", "@@* item\n* item@@")
add("raw-link", "@@http://example.com/?a=1&b=2@@")
add("raw-accents", "@@caf\u00e9 \u03b1 \u65e5\u672c@@")

# --- Raw: adjacency to other inline markup ----------------------------------
add("raw-in-bold", "**before @@raw@@ after**")
add("raw-in-italic", "//before @@raw@@ after//")
add("raw-next-bold", "@@raw@@ **bold**")
add("raw-in-link", "[[http://x/|@@raw@@]]")
add("raw-in-div", "[[div class=\"x\"]]\n@@raw@@\n[[/div]]")
add("raw-in-quote", "> @@raw@@")

# --- Rawold: shapes ----------------------------------------------------------
add("old-basic", "before ``raw **bold**`` after")
add("old-empty", "a ```` b")
add("old-ws-only", "a ``  `` b")
add("old-multiline", "before\n``line one\nline two``\nafter")
add("old-apostrophe", "a ``it's`` b")
add("old-triple", "a ```x``` b")
add("old-unterminated", "a ``never closed")
add("old-lone", "a `` b")
add("old-wikitext", "``//italic// **bold** [[link]]``")
add("old-html", "``<b>&\"'</b>``")
add("old-adjacent", "``one````two``")
add("old-and-raw", "``old`` @@raw@@")
add("old-quote-run", "a ``x`` b ``y`` c")

# --- Form: blocks ------------------------------------------------------------
add("form-basic", "[[form]]\nfields:\n  name:\n    type: text\n    label: Name\n---\nname: Alice\n[[/form]]")
add("form-no-data", "[[form]]\nfields:\n  name:\n    type: text\n    label: Name\n---\n\n[[/form]]")
add("form-empty-body", "[[form]]\n\n---\n\n[[/form]]")
add("form-unterminated", "[[form]]\nfields:\n  name:\n    type: text\n---\nname: x")
add("form-malformed-field", "[[form]]\nfields:\n  name: [broken\n---\nname: x\n[[/form]]")
add("form-no-separator", "[[form]]\nfields:\n  name:\n    type: text\n[[/form]]")
add("form-select", "[[form]]\nfields:\n  color:\n    type: select\n    label: Color\n    options:\n      r: Red\n      b: Blue\n---\ncolor: r\n[[/form]]")
add("form-wiki", "[[form]]\nfields:\n  note:\n    type: wiki\n    label: Note\n---\nnote: **bold**\n[[/form]]")
add("form-in-div", "[[div class=\"x\"]]\n[[form]]\nx\n---\ny\n[[/form]]\n[[/div]]")
add("form-stray-closer", "text\n[[/form]]\nafter")
add("form-inline", "before [[form]]x---y[[/form]] after")

# --- Pipeline interactions ---------------------------------------------------
add("raw-in-code", "[[code]]\n@@raw@@\n[[/code]]")
add("code-in-raw", "@@[[code]]x[[/code]]@@")
add("include-in-raw", "@@[[include page=test]]@@")
add("raw-in-include", "[[include page=raw-include]]")
add("form-in-code", "[[code]]\n[[form]]\nx\n---\ny\n[[/form]]\n[[/code]]")
add("code-in-form", "[[form]]\nfields:\n  note:\n    type: wiki\n---\nnote: [[code]]x[[/code]]\n[[/form]]")
add("raw-after-code", "[[code]]x[[/code]]\n@@raw@@")
add("old-in-code", "[[code]]\n``old``\n[[/code]]")

with open(__file__.replace("make_battery.py", "battery.jsonl"), "w", encoding="utf-8") as f:
    for c in cases:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
print(f"wrote {len(cases)} cases")
