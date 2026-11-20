#!/usr/bin/env python3
"""Generate the root-owned cross-rule interaction battery for the R2-next stage.

This battery covers seams the per-rule batteries cannot own: a Comment span
hiding an opener or closer of a later rule (Iframe, Date, Math, Iftags), an
Iftags body carrying Module or Math syntax in both tag polarities, Date and
Math inside a suppressed Iftags region, a Comment crossing an Iftags boundary,
and Iframe URL/attribute edges shared with the Url family. Tagged cases carry
a "tags" array that both the reference harness and the shared ftml dumper
consume, so suppressed and kept bodies can be compared deterministically.
"""
import json

OUT = "conformance-refphp/next/xbattery.jsonl"

cases = []
def add(cid, src, tags=None):
    rec = {"id": cid, "source": src}
    if tags is not None:
        rec["tags"] = tags
    cases.append(rec)

# 1. Comment hides an opener or closer of a later rule.
add("x-comment-hides-iframe", "before[!-- [[iframe https://example.com/a]] --]after\n")
add("x-comment-hides-date", "before[!-- [[date 1216153821]] --]after\n")
add("x-comment-hides-math-open", "before[!-- [[math E]] --]\nx=1\n[[/math]]\nafter\n")
add("x-comment-hides-math-close", "[[math E]]\nx=1\n[!-- [[/math]] --]\ny=2\n[[/math]]\nafter\n")
add("x-comment-hides-iftags-open", "[!-- [[iftags +alpha]] --]body[[/iftags]]\n")
add("x-comment-hides-iftags-close", "[[iftags +alpha]]body[!-- [[/iftags]] --]tail\n", ["alpha"])
add("x-comment-inside-iframe-attr", '[[iframe https://example.com/a width=[!-- 100 --]200]]\n')
add("x-comment-inside-date-attr", '[[date 1216153821 format=[!-- x --]"%Y"]]\n')
add("x-comment-inside-math-body", "[[math E]]\nx[!-- hidden --]=1\n[[/math]]\n")
add("x-comment-multiline-hides-math", "a[!--\n[[math E]]\nx=1\n[[/math]]\n--]b\n")

# 2. Iftags bodies containing module or math syntax, both polarities.
add("x-iftags-keep-module", "[[iftags +alpha]]\n[[module UnknownModuleX]]\nbody\n[[/module]]\n[[/iftags]]\n", ["alpha"])
add("x-iftags-drop-module", "[[iftags +beta]]\n[[module UnknownModuleX]]\nbody\n[[/module]]\n[[/iftags]]\n", ["alpha"])
add("x-iftags-keep-math", "[[iftags +alpha]]\n[[math E]]\nx=1\n[[/math]]\n[[/iftags]]\n", ["alpha"])
add("x-iftags-drop-math", "[[iftags +beta]]\n[[math E]]\nx=1\n[[/math]]\n[[/iftags]]\n", ["alpha"])
add("x-iftags-keep-date", "[[iftags +alpha]]\n[[date 1216153821]]\n[[/iftags]]\n", ["alpha"])
add("x-iftags-drop-date", "[[iftags +beta]]\n[[date 1216153821]]\n[[/iftags]]\n", ["alpha"])
add("x-iftags-keep-iframe", "[[iftags +alpha]]\n[[iframe https://example.com/a]]\n[[/iftags]]\n", ["alpha"])
add("x-iftags-drop-iframe", "[[iftags +beta]]\n[[iframe https://example.com/a]]\n[[/iftags]]\n", ["alpha"])
add("x-iftags-drop-nested-math-iftags", "[[iftags -alpha]]\n[[iftags +alpha]]\n[[math E]]\nx=1\n[[/math]]\n[[/iftags]]\n[[/iftags]]\n", ["alpha"])
add("x-iftags-untagged-any", "[[iftags alpha]]kept-or-dropped[[/iftags]]\n")
add("x-iftags-comment-spec", "[[iftags +alpha[!-- c --]]]\nbody\n[[/iftags]]\n", ["alpha"])

# 3. Date and Math inside regions suppressed by earlier rules.
add("x-module-body-math", "[[module UnknownModuleX]]\n[[math E]]\nx=1\n[[/math]]\n[[/module]]\n")
add("x-module-body-date", "[[module UnknownModuleX]]\n[[date 1216153821]]\n[[/module]]\n")
add("x-code-body-math", "[[code]]\n[[math E]]\nx=1\n[[/math]]\n[[/code]]\n")
add("x-raw-body-date", "[[raw]]\n[[date 1216153821]]\n[[/raw]]\n")

# 4. Iframe URL/attribute edges shared with the Url family.
add("x-iframe-then-url", "[[iframe https://example.com/a]]\n[[https://example.com/b]]\n")
add("x-url-in-iframe-attr", '[[iframe https://example.com/a style="background:url(https://example.com/i.png)"]]\n')
add("x-iframe-mailto", "[[iframe mailto:someone@example.com]]\n")
add("x-iframe-url-scheme-case", "[[iframe HTTPS://EXAMPLE.COM/A]]\n")
add("x-iframe-adjacent-date", "[[iframe https://example.com/a]]\n[[date 1216153821]]\n")
add("x-iframe-adjacent-math", "[[iframe https://example.com/a]]\n[[math E]]\nx=1\n[[/math]]\n")

# 5. Pipeline-order adjacency seams among our five rules.
add("x-iftags-comment-iframe-date-math", "[[iftags +alpha]]a[!-- c --]b[[/iftags]][[iframe https://example.com/a]][[date 1216153821]][[math E]]\nx=1\n[[/math]]\n", ["alpha"])
add("x-comment-then-iftags", "[!-- hidden --]\n[[iftags +alpha]]body[[/iftags]]\n", ["alpha"])

with open(OUT, "w", encoding="utf-8") as f:
    for rec in cases:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(f"wrote {len(cases)} cases to {OUT}")
