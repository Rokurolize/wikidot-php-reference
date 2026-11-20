#!/usr/bin/env python3
"""Build the R2 Concatlines differential battery and the live probe set.

Concatlines has no regex property of its own: its whole matching space is the
backslash-newline pair and the positions where that pair may or may not join,
which depend on the rules that have already tokenized the source before it
runs (Code, Raw, Math, Comment in the reference pipeline) and on the raw-body
and div-opener exemptions in ftml's Wikidot preprocessing. The battery is
therefore arranged in six groups: plain joins and backslash/newline count
variations, whitespace and line-ending edges, cascades across repeated
pairs, literal-span interiors and their boundaries, div/span opener adjacency
in pipeline order, and adjacency with the Freelink, Equationreference, Iframe,
Date, IfTags, Mathinline and URL rules that follow Concatlines. The live probe
set is the subset whose shape is not settled by the ftml corpus pins.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

B = "\\"          # one literal backslash
N = "\n"          # one literal newline


def c(cid, source, group):
    return {"id": cid, "source": source, "group": group}


cases = []

# Group 1: plain joins and backslash/newline count variations.
cases += [
    c("basic", "a" + B + N + "b", "join"),
    c("mid-word", "hel" + B + N + "lo", "join"),
    c("line-start-backslash", B + N + "a", "join"),
    c("backslash-only", B, "join"),
    c("backslash-at-eof", "a" + B, "join"),
    c("two-backslash-one-nl", "a" + B * 2 + N + "b", "join"),
    c("three-backslash-one-nl", "a" + B * 3 + N + "b", "join"),
    c("one-backslash-two-nl", "a" + B + N * 2 + "b", "join"),
    c("two-backslash-two-nl", "a" + B * 2 + N * 2 + "b", "cascade"),
    c("three-backslash-three-nl", "a" + B * 3 + N * 3 + "b", "cascade"),
    c("four-backslash-two-nl", "a" + B * 4 + N * 2 + "b", "cascade"),
    c("backslash-newline-pair", "a" + B + N + B + N + "b", "cascade"),
    c("multi-cont", "a" + B + N + "b" + B + N + "c", "cascade"),
    c("two-cont-lines", "a" + B + N + "b" + N + "c" + B + N + "d", "cascade"),
    c("blank-lines-around", N + "a" + B + N + "b" + N, "join"),
]

# Group 2: whitespace and line-ending edges.
cases += [
    c("backslash-space-newline", "a" + B + " " + N + "b", "edge"),
    c("backslash-tab-newline", "a" + B + "\t" + N + "b", "edge"),
    c("space-backslash-newline", "a " + B + N + "b", "edge"),
    c("tab-backslash-newline", "a\t" + B + N + "b", "edge"),
    c("backslash-two-spaces-newline", "a" + B + "  " + N + "b", "edge"),
    c("backslash-crlf", "a" + B + "\r\n" + "b", "edge"),
    c("backslash-lone-cr", "a" + B + "\r" + "b", "edge"),
    c("backslash-blank-space-line", "a" + B + N + " " + N + "b", "edge"),
    c("backslash-trailing-spaces-eof", "a" + B + "   ", "edge"),
]

# Group 3: literal-span interiors and their boundaries.
cases += [
    c("code-block", "[[code]]" + N + "x" + B + N + "y" + N + "[[/code]]", "literal"),
    c("code-block-upper", "[[CODE]]" + N + "x" + B + N + "y" + N + "[[/CODE]]", "literal"),
    c("inline-code", "[[code]]x" + B + N + "y[[/code]]", "literal"),
    c("code-then-cont", "[[code]]" + N + "x" + N + "[[/code]]" + N + "y" + B + N + "z", "literal"),
    c("cont-into-code", "a" + B + N + "[[code]]" + N + "x" + N + "[[/code]]", "literal"),
    c("raw-block", "[[raw]]" + N + "x" + B + N + "y" + N + "[[/raw]]", "literal"),
    c("math-block", "[[math]]" + N + "x" + B + N + "y" + N + "[[/math]]", "literal"),
    c("math-block-labeled", "[[math E]]" + N + "x" + B + N + "y" + N + "[[/math]]", "literal"),
    c("math-two-cont", "[[math]]" + N + "x " + B + N + "y " + B + N + "[[/math]]", "literal"),
    c("comment-join", "A" + B + "[!--x--]" + N + "B", "literal"),
    c("comment-inner-cont", "[!-- a" + B + N + "b --]" + N + "C", "literal"),
    c("cont-into-math", "a" + B + N + "[[math]]" + N + "x" + N + "[[/math]]", "literal"),
]

# Group 4: div and span opener adjacency in pipeline order.
cases += [
    c("div-opener", "a" + B + N + "[[div]]" + N + "x" + N + "[[/div]]", "div"),
    c("div-opener-attrs", "a" + B + N + "[[div class=\"box\"]]" + N + "x" + N + "[[/div]]", "div"),
    c("div-opener-upper", "a" + B + N + "[[DIV]]" + N + "x" + N + "[[/DIV]]", "div"),
    c("div-opener-tab", "a" + B + N + "[[div\tclass=\"box\"]]" + N + "x" + N + "[[/div]]", "div"),
    c("div-opener-underscore", "a" + B + N + "[[div_]]" + N + "x" + N + "[[/div]]", "div"),
    c("malformed-division", "alpha" + B + N + "[[division]]", "div"),
    c("malformed-divx", "alpha" + B + N + "[[divx]]", "div"),
    c("span-opener", "a" + B + N + "[[span]]x[[/span]]", "div"),
    c("span-opener-attr", "a" + B + N + "[[span style=\"color:red\"]]x[[/span]]", "div"),
]

# Group 5: adjacency with rules that follow Concatlines.
cases += [
    c("freelink-cont", "[[[tar" + B + N + "get]]]", "adjacency"),
    c("freelink-cont-space", "[[[tar" + B + N + " get|label]]]", "adjacency"),
    c("eref-cont", "[[math E]]" + N + "x=1" + N + "[[/math]]" + N + "[[eref " + B + N + "E]]", "adjacency"),
    c("iframe-src-cont", "[[iframe http://exa" + B + N + "mple.com]]", "adjacency"),
    c("date-cont", "[[date 12345" + B + N + "]]", "adjacency"),
    c("iftags-cont", "[[iftags +alpha]]" + N + "x" + B + N + "y" + N + "[[/iftags]]", "adjacency"),
    c("mathinline-cont", "[[mathinline]]x" + B + N + "y[[/mathinline]]", "adjacency"),
    c("url-cont", "[[http://exa" + B + N + "mple.com]]", "adjacency"),
    c("heading-cont", "= head" + B + N + "line", "adjacency"),
    c("quote-cont", "> quote" + B + N + "line", "adjacency"),
]

# Group 6: case and Unicode variations.
cases += [
    c("unicode-cont", "é" + B + N + "ü", "case"),
    c("fullwidth-cont", "ａ" + B + N + "ｂ", "case"),
    c("mixed-case-code", "[[CoDe]]" + N + "x" + B + N + "y" + N + "[[/cOdE]]", "case"),
    c("upper-continuation-word", "A" + B + N + "B" + B + N + "C", "case"),
]

# Live probes: shapes not settled by the ftml corpus pins. Sources are LF-only
# with trailing newlines stripped because Wikidot normalizes them on save.
# backslash-crlf is deliberately excluded: a first create run reached it and
# Wikidot rewrote the CRLF pair on save, so read-back verification failed and
# the whole batch aborted; lone-CR and CRLF are serving-layer boundaries that
# live cannot settle and stay in the local battery only.
PROBE_IDS = [
    "basic", "two-backslash-one-nl", "one-backslash-two-nl", "two-backslash-two-nl",
    "three-backslash-three-nl", "four-backslash-two-nl", "backslash-newline-pair",
    "multi-cont", "backslash-space-newline", "backslash-tab-newline",
    "space-backslash-newline", "backslash-at-eof",
    "code-block-upper", "inline-code", "raw-block", "math-block-labeled",
    "comment-inner-cont", "cont-into-code", "cont-into-math",
    "div-opener", "div-opener-attrs", "div-opener-upper", "div-opener-tab",
    "div-opener-underscore", "malformed-division", "span-opener-attr",
    "freelink-cont", "freelink-cont-space", "eref-cont", "iframe-src-cont",
    "date-cont", "mathinline-cont", "url-cont", "unicode-cont",
]

lookup = {x["id"]: x for x in cases}
probes = [{"id": pid, "source": lookup[pid]["source"]} for pid in PROBE_IDS]

with open(os.path.join(HERE, "battery.jsonl"), "w", encoding="utf-8") as f:
    for x in cases:
        f.write(json.dumps({"id": x["id"], "source": x["source"]}, ensure_ascii=False) + "\n")

with open(os.path.join(HERE, "probe-cases.jsonl"), "w", encoding="utf-8") as f:
    for x in probes:
        f.write(json.dumps(x, ensure_ascii=False) + "\n")

print("battery cases:", len(cases))
print("probe cases:", len(probes))
for name, count in sorted({g: sum(1 for x in cases if x["group"] == g) for g in {x["group"] for x in cases}}.items()):
    print(" group", name, count)
