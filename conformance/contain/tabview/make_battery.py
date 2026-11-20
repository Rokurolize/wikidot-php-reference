#!/usr/bin/env python3
"""Build the Tabview R2 differential battery (JSONL {"id","source"[,"tags"]})."""
import json

C = []
def add(cid, src, tags=None):
    row = {"id": cid, "source": src}
    if tags is not None:
        row["tags"] = tags
    C.append(row)

# --- titles and named / unnamed tabs -------------------------------------
add("tv01-single", "[[tabview]]\n[[tab solo]]\ndata here\n[[/tab]]\n[[/tabview]]")
add("tv02-two-tabs", "[[tabview]]\n[[tab One]]\nfirst\n[[/tab]]\n[[tab Two]]\nsecond\n[[/tab]]\n[[/tabview]]")
add("tv03-title-double-space", "[[tabview]]\n[[tab A  B]]\nx\n[[/tab]]\n[[/tabview]]")
add("tv04-title-trailing-space", "[[tabview]]\n[[tab A ]]\nx\n[[/tab]]\n[[/tabview]]")
add("tv05-title-attr", '[[tabview]]\n[[tab title="A"]]\nx\n[[/tab]]\n[[/tabview]]')
add("tv06-title-attr-spaces", '[[tabview]]\n[[tab title="A B"]]\nx\n[[/tab]]\n[[/tabview]]')
add("tv07-class-attr", '[[tabview]]\n[[tab class="c"]]\nx\n[[/tab]]\n[[/tabview]]')
add("tv08-foo-attr", '[[tabview]]\n[[tab foo="A"]]\nx\n[[/tab]]\n[[/tabview]]')
add("tv09-attr-then-text", '[[tabview]]\n[[tab class="c" A]]\nx\n[[/tab]]\n[[/tabview]]')
add("tv10-text-then-attr", '[[tabview]]\n[[tab A class="c"]]\nx\n[[/tab]]\n[[/tabview]]')
add("tv11-untitled-bare", "[[tabview]]\n[[tab]]\nx\n[[/tab]]\n[[/tabview]]")
add("tv12-untitled-spaces", "[[tabview]]\n[[tab  ]] x [[/tab]]\n[[/tabview]]")
add("tv13-case-insensitive", "[[TABVIEW]]\n[[TaB mixed]]\nx\n[[/tAb]]\n[[/TABVIEW]]")
add("tv14-alias-tabs", "[[tabs]]\n[[tab A]]\nx\n[[/tab]]\n[[/tabs]]")
add("tv15-mixed-alias", "[[tabview]]\n[[tab A]]\nx\n[[/tab]]\n[[/tabs]]")
add("tv16-title-entities", "[[tabview]]\n[[tab A &amp; B]]\nx\n[[/tab]]\n[[/tabview]]")
add("tv17-title-htmlchars", "[[tabview]]\n[[tab <em>x</em>]]\nx\n[[/tab]]\n[[/tabview]]")

# --- same-rule nesting ----------------------------------------------------
add("tv18-nested-view", "[[tabview]]\n[[tab outer]]\nA\n[[tabview]]\n[[tab inner]]\nB\n[[/tab]]\n[[/tabview]]\n[[/tab]]\n[[/tabview]]")
add("tv19-nested-alias", "[[tabview]]\n[[tab 1]]\nA\n[[tabs]]\n[[tab 2]]\nB\n[[/tabs]]\n[[/tab]]\n[[/tabview]]")
add("tv20-nested-deep", "[[tabview]]\n[[tab 1]]\nA\n[[tabs]]\n[[tab 2]]\nB\n[[tabview]]\n[[tab 3]]\nC\n[[/tabview]]\n[[/tabs]]\n[[/tab]]\n[[/tabview]]")
add("tv21-nested-blank", "[[tabview]]\n[[tab 1]]\nA\n\n[[tabview]]\n[[tab 2]]\nB\n[[/tab]]\n[[/tabview]]\n[[/tab]]\n[[/tabview]]")

# --- cross-rule containment ----------------------------------------------
add("tv22-div-in-tab", "[[tabview]]\n[[tab A]]\n[[div class=x]]\ninner\n[[/div]]\n[[/tab]]\n[[/tabview]]")
add("tv23-coll-in-tab", "[[tabview]]\n[[tab A]]\n[[collapsible]]\ninner\n[[/collapsible]]\n[[/tab]]\n[[/tabview]]")
add("tv24-div-in-coll-in-tab", "[[tabview]]\n[[tab A]]\n[[collapsible show=show]]\n[[div class=x]]\ninner\n[[/div]]\n[[/collapsible]]\n[[/tab]]\n[[/tabview]]")
add("tv25-tab-in-div", "[[div class=a]]\n[[tabview]]\n[[tab A]]\ninner\n[[/tab]]\n[[/tabview]]\n[[/div]]")
add("tv26-bold-in-tab", "[[tabview]]\n[[tab A]]\n**bold** and [[B]]\n[[/tab]]\n[[/tabview]]")
add("tv27-span-in-tab", "[[tabview]]\n[[tab A]]\n[[span class=s]]text[[/span]]\n[[/tab]]\n[[/tabview]]")
add("tv28-para-in-tab", "[[tabview]]\n[[tab A]]\none\n\ntwo\n[[/tab]]\n[[/tabview]]")

# --- empty bodies ---------------------------------------------------------
add("tv29-empty-tab", "[[tabview]]\n[[tab A]]\n[[/tab]]\n[[/tabview]]")
add("tv30-empty-body-blank", "[[tabview]]\n[[tab A]]\n\n\n[[/tab]]\n[[/tabview]]")
add("tv31-empty-view", "[[tabview]][[/tabview]]")
add("tv32-empty-view-newlines", "[[tabview]]\n[[/tabview]]")

# --- pairing, stray and unterminated closers -----------------------------
add("tv33-unterminated-tab", "[[tabview]]\n[[tab A]]\nbody\n[[/tabview]]")
add("tv34-unterminated-view", "[[tabview]]\n[[tab A]]\nbody\n[[/tab]]")
add("tv35-stray-tab-first", "[[tabview]]\n[[/tab]]\n[[tab A]]\nx\n[[/tab]]\n[[/tabview]]")
add("tv36-stray-view-first", "[[tabview]]\n[[/tabview]]\n[[tab A]]\nx\n[[/tab]]")
add("tv37-double-tab-close", "[[tabview]]\n[[tab A]]\nx\n[[/tab]][[/tab]]\n[[/tabview]]")
add("tv38-prose-between", "[[tabview]]\n[[tab A]] a [[/tab]]\nprose\n[[tab B]] b [[/tab]]\n[[/tabview]]")
add("tv39-prose-before", "[[tabview]]\nprose\n[[tab A]] a [[/tab]]\n[[/tabview]]")
add("tv40-prose-after", "[[tabview]]\n[[tab A]] a [[/tab]]\nprose\n[[/tabview]]")

# --- inline form ----------------------------------------------------------
add("tv41-inline-one-line", "[[tabview]] [[tab A]] 1 [[/tab]] [[tab B]] 2 [[/tab]] [[/tabview]]")
add("tv42-inline-tight", "[[tabview]][[tab A]]1[[/tab]][[/tabview]]")

# --- attributes and quoting variants on the view opener ------------------
add("tv43-view-class", '[[tabview class="x"]]\n[[tab A]]\nx\n[[/tab]]\n[[/tabview]]')
add("tv44-view-unquoted", "[[tabview class=x]]\n[[tab A]]\nx\n[[/tab]]\n[[/tabview]]")
add("tv45-view-id", '[[tabview id="v"]]\n[[tab A]]\nx\n[[/tab]]\n[[/tabview]]')
add("tv46-view-style", '[[tabview style="color:red"]]\n[[tab A]]\nx\n[[/tab]]\n[[/tabview]]')
add("tv47-view-singlequote", "[[tabview class='c']]\n[[tab A]]\nx\n[[/tab]]\n[[/tabview]]")
add("tv48-view-multiple-attrs", '[[tabview class="a" id="b"]]\n[[tab A]]\nx\n[[/tab]]\n[[/tabview]]')

# --- malformed heads and forms -------------------------------------------
add("tv49-head-bracket", "[[tabview]]\n[[tab a]b]]\nx\n[[/tab]]\n[[/tabview]]")
add("tv50-head-comment", "[[tabview]]\n[[tab a[!-- c --]]] x [[/tab]]\n[[/tabview]]")
add("tv51-head-bold", "[[tabview]]\n[[tab **bold**]]\nx\n[[/tab]]\n[[/tabview]]")
add("tv52-title-raw", '[[tabview]]\n[[tab title="@@a@@"]]\nx\n[[/tab]]\n[[/tabview]]')
add("tv53-head-leading-space", "[[tabview]]\n[[ tab A ]]\nx\n[[/tab]]\n[[/tabview]]")
add("tv54-stray-view-end-only", "[[tab A]]\nx\n[[/tab]]\n[[/tabview]]")

with open("battery.jsonl", "w", encoding="utf-8") as f:
    for row in C:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print("wrote", len(C), "cases")
