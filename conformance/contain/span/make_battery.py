#!/usr/bin/env python3
"""Generate the R2-contain Span rule battery.

Covers the span matching space: the [[span attrs]]...[[/span]] block form,
the fossil-hypothesised %%...%% inline form (which neither side implements as
a span), the attribute matrix (class, id, style, unknown keys, quoting
variants), empty bodies, unterminated and stray closers, same-rule and
cross-rule nesting including the span-shaped family (span, size, colour and
strikethrough all render as <span> and re-nest by HTML tag name), inline
content inside block containers, block content inside the inline span, and
malformed openers. Every case is a whole document; optional "tags" are
consumed by both the reference harness and the shared ftml dumper.
"""
import json

OUT = "conformance-refphp/contain/span/battery.jsonl"

cases = []
def add(cid, src, tags=None):
    rec = {"id": cid, "source": src}
    if tags is not None:
        rec["tags"] = tags
    cases.append(rec)

# A. Basic [[span]] form and surface variants.
add("s01-plain", "[[span]]X[[/span]]")
add("s02-inline-context", "BEGIN|[[span]]X[[/span]]|END")
add("s03-empty", "[[span]][[/span]]")
add("s04-empty-spaces", "[[span ]]  [[/span]]")
add("s05-multiline", "[[span]]line one\nline two[[/span]]")
add("s06-uppercase", "[[SPAN]]X[[/SPAN]]")
add("s07-two-spans", "[[span]]A[[/span]] [[span]]B[[/span]]")
add("s08-leading-trailing", "a [[span]] X [[/span]] b")

# B. Attribute matrix: class, id, style, unknown keys, quoting variants.
add("s09-class", '[[span class="c"]]X[[/span]]')
add("s10-id", '[[span id="i"]]X[[/span]]')
add("s11-style", '[[span style="color:red"]]X[[/span]]')
add("s12-style-two", '[[span style="color:red; font-size:120%"]]X[[/span]]')
add("s13-style-hidden", '[[span style="visibility:hidden"]]X[[/span]]')
add("s14-style-none", '[[span style="display:none"]]X[[/span]]')
add("s15-title", '[[span title="tip"]]X[[/span]]')
add("s16-role", '[[span role="note"]]X[[/span]]')
add("s17-data", '[[span data-x="value"]]X[[/span]]')
add("s18-unknown", '[[span frobnicate="yes"]]X[[/span]]')
add("s19-onclick", '[[span onclick="alert(1)"]]X[[/span]]')
add("s20-class-id-style", '[[span class="c" id="i" style="color:red"]]X[[/span]]')
add("s21-single-quote", "[[span class='c']]X[[/span]]")
add("s22-unquoted", "[[span class=c]]X[[/span]]")
add("s23-attr-spaces", '[[span  class="c"  style="color:red" ]]X[[/span]]')

# C. Same-rule nesting and crossing.
add("s24-nested", "[[span]]outer [[span]]inner[[/span]][[/span]]")
add("s24b-nested3", "[[span]]a[[span]]b[[span]]c[[/span]][[/span]][[/span]]")
add("s25-crossed", "[[span]]A [[span]]B[[/span]] C[[/span]]")
add("s26-stray-close", "X [[/span]] Y")
add("s27-unterminated", "[[span]]unterminated")
add("s28-close-first", "[[/span]] [[span]]X[[/span]]")

# D. Span-shaped family: span, size, colour, strikethrough re-nest by <span>.
add("s29-span-size", "[[span]]A [[size 120%]]B[[/size]] C[[/span]]")
add("s30-span-color", "[[span]]A ##red|B## C[[/span]]")
add("s31-span-strike", "[[span]]A --B-- C[[/span]]")
add("s32-size-span", "[[size 120%]]A [[span]]B[[/span]] C[[/size]]")
add("s33-color-span", "##red|A [[span]]B[[/span]] C##")
add("s34-strike-span", "--A [[span]]B[[/span]] C--")
add("s35-span-size-cross", "[[span]]A [[size 120%]]B[[/span]] C[[/size]]")
add("s36-span-color-cross", "[[span]]A ##red|B[[/span]] C##")
add("s37-span-strike-cross", "[[span]]A --B[[/span]] C--")
add("s38-size-color-strike", "[[size 120%]]A ##red|--B--## C[[/size]]")
add("s39-span-in-span-block", "[[span]]A\n[[span]]B[[/span]]\nC[[/span]]")

# E. Score span and the fossil-hypothesised %% inline form.
add("s40-score-span", "[[span_]]X[[/span]]")
add("s41-score-span-extra", "[[span_]]]X[[/span]]")
add("s42-percent", "%%hidden%%")
add("s43-percent-span", "[[span]]%%hidden%%[[/span]]")
add("s44-malformed-opener", "[[span class=\"c\"X[[/span]]")
add("s45-missing-space", "[[spanclass=\"c\"]]X[[/span]]")
add("s46-double-open", "[[span]][[span]]X[[/span]]")
add("s47-newline-in-attr", '[[span\nclass="c"]]X[[/span]]')

# F. Inline in block containers and block content inside the inline span.
add("s48-span-in-div", "[[div]]\n[[span]]X[[/span]]\n[[/div]]")
add("s49-div-in-span", "[[span]]A [[div]]B[[/div]] C[[/span]]")
add("s50-span-across-div", "[[span]]A\n[[div]]B[[/div]]\nC[[/span]]")
add("s51-span-in-collapsible", "[[collapsible]]\n[[span]]X[[/span]]\n[[/collapsible]]")
add("s52-span-in-heading", "+ [[span]]Head[[/span]]")
add("s53-span-in-quote", "> [[span]]Quoted[[/span]]\n\n")
add("s54-span-in-list", "* [[span]]item[[/span]]\n")
add("s55-span-in-code", "[[code]]\n[[span]]literal[[/span]]\n[[/code]]")
add("s56-span-in-iftags", "[[iftags +alpha]]\n[[span]]kept[[/span]]\n[[/iftags]]", ["alpha"])
add("s57-span-block-content", "[[span]]+ head\n* list[[/span]]")
add("s58-span-attr-entity", '[[span title="a &amp; b"]]X[[/span]]')
add("s59-span-class-empty", '[[span class=""]]X[[/span]]')
add("s60-span-style-empty", '[[span style=""]]X[[/span]]')

with open(OUT, "w", encoding="utf-8") as f:
    for rec in cases:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(f"wrote {len(cases)} span cases to {OUT}")
