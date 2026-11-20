#!/usr/bin/env python3
"""Generate the root-owned cross-rule interaction battery for the R2-link stage.

The seams here are ones the three per-rule batteries cannot own: Concatlines
continuations crossing into or out of code, raw and comment spans; a Freelink
inside an Iftags-suppressed body and inside a Math label position; and eref
resolution against equations defined later in the document, duplicated labels,
and labels on equations suppressed by Iftags. Tagged cases carry a "tags" array
that both the reference harness and the shared ftml dumper consume, so a true
and a false Iftags gate can be compared deterministically.
"""
import json

OUT = "conformance-refphp/link/xbattery.jsonl"

cases = []
def add(cid, src, tags=None):
    rec = {"id": cid, "source": src}
    if tags is not None:
        rec["tags"] = tags
    cases.append(rec)

EX = "muse-probe-r2link-free-exists"
NEW = "muse-probe-r2link-x-absent-page"

# A. Concatlines continuations crossing literal-span boundaries.
add("x-concat-code-inside", "[[code]]\na\\\nb\n[[/code]]\n")
add("x-concat-code-outside", "before\\\nafter [[code]]x[[/code]]\n")
add("x-concat-code-before-open", "a\\\n[[code]]\nx\n[[/code]]\n")
add("x-concat-code-after-close", "[[code]]\nx\n[[/code]]\\\ntail\n")
add("x-concat-raw-inside", "[[raw]]\na\\\nb\n[[/raw]]\n")
add("x-concat-raw-before-open", "a\\\n[[raw]]\nx\n[[/raw]]\n")
add("x-concat-rawold-inside", "[[rawold]]\na\\\nb\n[[/rawold]]\n")
add("x-concat-comment-inside", "[!-- a\\\nb --]tail\n")
add("x-concat-comment-before", "a\\\n[!-- hidden --]tail\n")
add("x-concat-comment-after", "[!-- hidden --]\\\ntail\n")
add("x-concat-math-inside", "[[math E]]\nx\\\ny\n[[/math]]\n")
add("x-concat-freelink-join", "[[[%s|some\\\ntext]]]\n" % EX)
add("x-concat-eref-join", "[[eref la\\\nbel]]\n")

# B. Freelink inside a suppressed Iftags body and inside a Math label.
add("x-free-iftags-keep", "[[iftags +alpha]]\n[[[%s]]]\n[[/iftags]]\n" % EX, ["alpha"])
add("x-free-iftags-drop", "[[iftags +beta]]\n[[[%s]]]\n[[/iftags]]\n" % EX, ["alpha"])
add("x-free-iftags-keep-new", "[[iftags +alpha]]\n[[[%s]]]\n[[/iftags]]\n" % NEW, ["alpha"])
add("x-free-iftags-drop-new", "[[iftags +beta]]\n[[[%s]]]\n[[/iftags]]\n" % NEW, ["alpha"])
add("x-free-math-label", "[[math [[[%s]]]]]\nx\n[[/math]]\n[[eref [[[%s]]]]]\n" % (EX, EX))
add("x-free-math-body", "[[math E]]\n[[[%s]]]\n[[/math]]\n" % EX)
add("x-free-inside-code", "[[code]]\n[[[%s]]]\n[[/code]]\n" % EX)
add("x-free-inside-raw", "[[raw]]\n[[[%s]]]\n[[/raw]]\n" % EX)
add("x-free-inside-comment", "[!-- [[[%s]]] --]tail\n" % EX)
add("x-free-next-to-math", "[[[%s]]][[math E]]x[[/math]]\n" % EX)

# C. eref resolution, forward references, duplicates and suppressed equations.
add("x-eref-backward", "[[math E]]\nx\n[[/math]]\n[[eref E]]\n")
add("x-eref-forward", "[[eref E]]\n[[math E]]\nx\n[[/math]]\n")
add("x-eref-duplicate", "[[math E]]\nx\n[[/math]]\n[[math E]]\ny\n[[/math]]\n[[eref E]]\n")
add("x-eref-duplicate-forward", "[[math E]]\nx\n[[/math]]\n[[eref E]]\n[[math E]]\ny\n[[/math]]\n")
add("x-eref-suppressed-math", "[[iftags -alpha]]\n[[math E]]\nx\n[[/math]]\n[[/iftags]]\n[[eref E]]\n", ["alpha"])
add("x-eref-in-suppressed-body", "[[math E]]\nx\n[[/math]]\n[[iftags -alpha]]\n[[eref E]]\n[[/iftags]]\n", ["alpha"])
add("x-eref-kept-math", "[[iftags +alpha]]\n[[math E]]\nx\n[[/math]]\n[[/iftags]]\n[[eref E]]\n", ["alpha"])
add("x-eref-inside-code", "[[code]]\n[[eref E]]\n[[/code]]\n")
add("x-eref-inside-raw", "[[raw]]\n[[eref E]]\n[[/raw]]\n")
add("x-eref-inside-comment", "[!-- [[eref E]] --]tail\n")
add("x-eref-two-labels", "[[math A]]\na\n[[/math]]\n[[math B]]\nb\n[[/math]]\n[[eref A]] [[eref B]]\n")
add("x-eref-nested-freelink", "[[math E]]\nx\n[[/math]]\n[[eref [[[%s]]]]]\n" % EX)
add("x-eref-undefined", "[[eref NO_SUCH_LABEL]]\n")

with open(OUT, "w", encoding="utf-8") as f:
    for rec in cases:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(f"wrote {len(cases)} cases to {OUT}")
