#!/usr/bin/env python3
"""Root's R2-contain cross-rule interaction battery.

Whole-document cases covering the seams no single rule owner owns: the
span-shaped family (span/size/colortext/strikethrough) crossing and nesting
under the two-stage inline model, containers inside suppressed iftags bodies
and inside code/raw spans, div inside collapsible inside tab and the reverse
nestings, footnote blocks inside containers, and the Concatlines [[div_]]
residual. Optional per-case "tags" mirror the shared harness protocol.
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

# A. span-shaped family crossing and nesting (recorded against the two-stage
# model: Stage 1 pairs in source order, Stage 2 re-nests by HTML tag name).
add("x01-span-size-cross", "[[span class=a]]A[[size 12px]]B[[/span]]C[[/size]]")
add("x02-size-span-cross", "[[size 12px]]A[[span class=a]]B[[/size]]C[[/span]]")
add("x03-span-color-nested", "[[span class=a]]A##red|B##C[[/span]]")
add("x04-color-span-cross", "##red|[[span class=a]]A##B[[/span]]")
add("x05-strike-span-cross", "--A[[span class=a]]B--C[[/span]]")
add("x06-span-strike-nested", "[[span class=a]]A--B--C[[/span]]")
add("x07-span-size-strike-cross", "[[span class=a]]A[[size 12px]]B--C[[/span]]D[[/size]]E--")
add("x08-span-nested-same", "[[span class=a]]A[[span class=b]]B[[/span]]C[[/span]]")
add("x09-size-nested-same", "[[size 12px]]A[[size 14px]]B[[/size]]C[[/size]]")
add("x10-span-empty", "[[span]] [[/span]]")
add("x11-span-size-cross-block", "[[div class=d]]\n[[span class=a]]A[[size 12px]]B[[/span]]C[[/size]]\n[[/div]]")

# B. containers inside suppressed iftags bodies and inside code/raw spans.
add("x12-iftags-suppressed-div", "[[iftags +alpha]]\n[[div class=x]]\ninside\n[[/div]]\n[[/iftags]]\nvisible", tags=[])
add("x13-iftags-active-div", "[[iftags +alpha]]\n[[div class=x]]\ninside\n[[/div]]\n[[/iftags]]\nvisible", tags=["alpha"])
add("x14-iftags-suppressed-coll", "[[iftags -alpha]]\n[[collapsible]]\ninside\n[[/collapsible]]\n[[/iftags]]\nvisible", tags=["alpha"])
add("x15-iftags-active-coll", "[[iftags -alpha]]\n[[collapsible]]\ninside\n[[/collapsible]]\n[[/iftags]]\nvisible", tags=[])
add("x16-iftags-suppressed-tab", "[[iftags +alpha]]\n[[tabview]]\n[[tab title=A]]\nbody\n[[/tab]]\n[[/tabview]]\n[[/iftags]]\nvisible", tags=[])
add("x17-code-inline-div", "@@[[div class=x]] inside [[/div]]@@")
add("x18-code-block-div", "[[code]]\n[[div]]\ninside\n[[/div]]\n[[/code]]")
add("x19-code-inline-coll", "@@[[collapsible]]body[[/collapsible]]@@")
add("x20-span-code-div", "[[span class=a]]A@@[[div]]x[[/div]]@@B[[/span]]")

# C. div inside collapsible inside tab, and reverse nestings.
add("x21-div-in-coll-in-tab", "[[tabview]]\n[[tab title=A]]\n[[collapsible show=show]]\n[[div class=x]]\ninner\n[[/div]]\n[[/collapsible]]\n[[/tab]]\n[[/tabview]]")
add("x22-coll-in-tab", "[[tabview]]\n[[tab title=A]]\n[[collapsible]]\ninner\n[[/collapsible]]\n[[/tab]]\n[[/tabview]]")
add("x23-div-in-tab", "[[tabview]]\n[[tab title=A]]\n[[div class=x]]\ninner\n[[/div]]\n[[/tab]]\n[[/tabview]]")
add("x24-three-nested-divs", "[[div class=a]]A\n[[div class=b]]B\n[[div class=c]]C\n[[/div]]\n[[/div]]\n[[/div]]")
add("x25-tab-in-coll-in-div", "[[div class=a]]\n[[collapsible]]\n[[tabview]]\n[[tab title=A]]\ninner\n[[/tab]]\n[[/tabview]]\n[[/collapsible]]\n[[/div]]")
add("x26-coll-first-closer-wins", "[[collapsible]]A[[collapsible]]B[[/collapsible]]C[[/collapsible]]")

# D. footnote blocks inside containers (BLOCK settled the quote case).
add("x27-footnote-in-div", "[[div class=x]]\ntext[[footnote]]note1[[/footnote]]\n[[footnoteblock]]\n[[/div]]")
add("x28-footnote-in-coll", "[[collapsible]]\ntext[[footnote]]note1[[/footnote]]\n[[footnoteblock]]\n[[/collapsible]]")
add("x29-footnote-in-tab", "[[tabview]]\n[[tab title=A]]\ntext[[footnote]]note1[[/footnote]]\n[[footnoteblock]]\n[[/tab]]\n[[/tabview]]")
add("x30-div-in-footnote", "[[footnote]]\n[[div]]\ninside\n[[/div]]\n[[/footnote]]\n[[footnoteblock]]")
add("x31-span-in-footnote", "[[footnote]][[span class=a]]S[[/span]][[/footnote]]\n[[footnoteblock]]")

# E. Concatlines [[div_]] residual and controls.
add("x32-div-underscore-basic", "[[div_]]\nbody\n[[/div]]")
add("x33-div-underscore-attrs", '[[div_ class="x"]]\nbody\n[[/div]]')
add("x34-div-underscore-inline", "before [[div_]] body [[/div]] after")
add("x35-div-underscore-unterminated", "[[div_]]\nbody")
add("x36-div-normal-control", "[[div class=x]]\nbody\n[[/div]]")

with open(os.path.join(OUT_DIR, "xbattery.jsonl"), "w", encoding="utf-8") as f:
    for row in C:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print("wrote", len(C), "cross-rule interaction cases")
