#!/usr/bin/env python3
"""Focused live probes for Size shapes the ftml corpus pins do not settle."""
import json

C = []
def add(cid, src):
    C.append({"id": cid, "source": src})

# Value grammar that the corpus pins only partly settle.
add("long-px", "[[size 123456px]]X[[/size]]")
add("long-pct", "[[size 1000000%]]X[[/size]]")
add("multi-dot", "[[size 1.2.3px]]X[[/size]]")
add("dot-only", "[[size .px]]X[[/size]]")
add("trailing-dot", "[[size 1.px]]X[[/size]]")
add("nbsp-arg", "[[size \u00a0100%\u00a0]]X[[/size]]")
add("upper-value", "[[size LARGER]]X[[/size]]")
add("upper-unit", "[[size 80PX]]X[[/size]]")
add("pt-unit", "[[size 12pt]]X[[/size]]")

# Opener/head variants.
add("double-space-head", "[[size  100%]]X[[/size]]")
add("equals-form", "[[size=100%]]X[[/size=]]")
add("quoted-value", '[[size "100%"]]X[[/size]]')
add("closer-with-space", "[[size 80%]]x[[/size ]]")
add("entity-head", "[[size 100&#37;]]X[[/size]]")
add("mixed-case-tag", "[[SiZe larger]]X[[/sIzE]]")
add("no-arg", "[[size]]X[[/size]]")

# Empty, trailing-space and nesting behaviour.
add("empty-body", "[[size 100%]][[/size]]")
add("ws-body", "[[size 100%]]   [[/size]]")
add("space-before-close", "[[size 120%]]x [[/size]]")
add("nested-pair", "[[size 80%]]a[[size 90%]]b[[/size]]c[[/size]]")

# Span-shaped family crossing and block-container interaction.
add("crossed-span", '[[size 80%]]a[[span class="x"]]b[[/size]]c[[/span]]')
add("crossed-color", '[[color red]]a[[size 80%]]b[[/color]]c[[/size]]')
add("crossed-bold", "**[[size 110%]]OVERWATCH COUNCIL**[[/size]]")
add("size-in-div", '[[div class="d"]]\n[[size 80%]]x[[/size]]\n[[/div]]')
add("list-in-size", "[[size 80%]]a\n* x\n* y\n[[/size]]")
add("size-crosses-div", '[[size larger]]\n[[div class="outer"]]\nheader\n[[div class="links"]]\nlink\n[[/div]]\n[[div class="content"]]\n[[/size]]\nbody\n[[/div]]\n[[/div]]')

with open("probe-cases.jsonl", "w", encoding="utf-8") as f:
    for row in C:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print("wrote", len(C), "probe cases")
