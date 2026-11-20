#!/usr/bin/env python3
"""Focused live probes for Tabview shapes the pins and dumper leave open."""
import json

C = []
def add(cid, src):
    C.append({"id": cid, "source": src})

add("p01-basic-two", "[[tabview]]\n[[tab One]]\nfirst\n[[/tab]]\n[[tab Two]]\nsecond\n[[/tab]]\n[[/tabview]]")
add("p02-title-double-space", "[[tabview]]\n[[tab A  B]]\nx\n[[/tab]]\n[[/tabview]]")
add("p03-title-trailing-space", "[[tabview]]\n[[tab A ]]\nx\n[[/tab]]\n[[/tabview]]")
add("p04-title-entity", "[[tabview]]\n[[tab A &amp; B]]\nx\n[[/tab]]\n[[/tabview]]")
add("p05-title-htmlchars", "[[tabview]]\n[[tab <em>x</em>]]\nx\n[[/tab]]\n[[/tabview]]")
add("p06-attr-then-text", '[[tabview]]\n[[tab class="c" A]]\nx\n[[/tab]]\n[[/tabview]]')
add("p07-raw-title", '[[tabview]]\n[[tab title="@@a@@"]]\nx\n[[/tab]]\n[[/tabview]]')
add("p08-view-class", '[[tabview class="x"]]\n[[tab A]]\nx\n[[/tab]]\n[[/tabview]]')
add("p09-unterminated-view", "[[tabview]]\n[[tab A]]\nbody\n[[/tab]]")
add("p10-unterminated-tab", "[[tabview]]\n[[tab A]]\nbody\n[[/tabview]]")
add("p11-prose-between", "[[tabview]]\n[[tab A]] a [[/tab]]\nprose\n[[tab B]] b [[/tab]]\n[[/tabview]]")
add("p12-stray-tab-first", "[[tabview]]\n[[/tab]]\n[[tab A]]\nx\n[[/tab]]\n[[/tabview]]")
add("p13-nested-view", "[[tabview]]\n[[tab outer]]\nA\n[[tabview]]\n[[tab inner]]\nB\n[[/tab]]\n[[/tabview]]\n[[/tab]]\n[[/tabview]]")
add("p14-untitled", "[[tabview]]\n[[tab]]\nx\n[[/tab]]\n[[/tabview]]")
add("p15-coll-in-tab", "[[tabview]]\n[[tab A]]\n[[collapsible]]\ninner\n[[/collapsible]]\n[[/tab]]\n[[/tabview]]")
add("p16-empty-tab", "[[tabview]]\n[[tab A]]\n[[/tab]]\n[[/tabview]]")

with open("probe-cases.jsonl", "w", encoding="utf-8") as f:
    for row in C:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print("wrote", len(C), "probe cases")
