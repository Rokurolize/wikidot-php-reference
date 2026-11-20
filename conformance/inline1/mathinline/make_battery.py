#!/usr/bin/env python3
"""Generate the R2-inline1 Mathinline differential battery (battery.jsonl).

Each record is {"id": ..., "source": ...} for the shared harness batch.php
(render / tokens) and the shared ftml dumper. Sources are LF-only, matching
the line-ending normalization the harness applies at input. The categories
are inline delimiters and whitespace, label-like and attribute-like content,
newlines/paragraph breaks, malformed and unterminated forms, neighbours and
nesting with the earlier rules (span, heading, table, list, div, code, raw,
comment, footnote, collapsible), and the comment/dollar closer seams ftml's
math.rs handles specially.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "battery.jsonl")

# (id, source). Each source is explicit so every byte-level difference is
# visible to the reader; no generator tricks.
CASES = [
    # --- basic delimiters and whitespace ---------------------------------
    ("basic", "A [[$ x^2 $]] B"),
    ("no-spaces", "[[$x^2$]]"),
    ("left-space-only", "[[$ x$]]"),
    ("right-space-only", "[[$x $]]"),
    ("tabs-around", "[[$\tx\t$]]"),
    ("empty", "[[$$]]"),
    ("spaces-only", "[[$   $]]"),
    ("multiple-line", "[[$ a $]] and [[$ b $]]"),
    ("adjacent", "[[$a$]][[$b$]]"),
    ("dollar-in-content", "[[$ a$b $]]"),
    ("html-content", "[[$ <b>x</b> $]]"),
    ("entities-content", "[[$ a &amp; b $]]"),
    ("unicode-content", "[[$ \u03b1 + \u03b2 $]]"),

    # --- label-like / attribute-like content -----------------------------
    ("label-like-word", "[[$ label=x $]]"),
    ("label-like-brackets", "[[$ [foo] $]]"),
    ("attr-like", "[[$ type=\"align\" $]]"),
    ("pipe-in-content", "[[$ a|b $]]"),
    ("backslash-commands", "[[$ \\alpha + \\beta $]]"),
    ("typography-dots", "[[$ a...b $]]"),
    ("typography-dashes", "[[$ a--b $]]"),
    ("comment-markers", "[[$ [!-- c --] $]]"),

    # --- newlines, paragraph breaks, malformed, unterminated -------------
    ("single-newline", "[[$ E =\nmc^2 $]]"),
    ("blank-line-inside", "[[$ E =\n\nmc^2 $]]"),
    ("newline-after-opener", "[[$\nx$]]"),
    ("newline-before-closer", "[[$x\n$]]"),
    ("unterminated", "[[$ x"),
    ("unterminated-empty", "[[$"),
    ("stray-closer", "x $]]"),
    ("close-first", "$]] [[$ x $]]"),
    ("triple-close", "[[$x$]]]"),
    ("quad-close", "[[$x$]]]]"),
    ("double-dollar-open", "[[$$x$]]"),
    ("shifted-close", "[[$ x $]"),
    ("shifted-open", "[$ x $]]"),

    # --- neighbours and nesting -----------------------------------------
    ("in-span", "[[span class=\"x\"]][[$ y $]][[/span]]"),
    ("in-scored-span", "[[span_]] [[$ y $]] [[/span]]"),
    ("in-heading1", "+ [[$ x $]]"),
    ("in-heading2", "++ Heading [[$ x $]]"),
    ("in-table-cell", "|| [[$ a $]] || [[$ b $]] ||"),
    ("in-list", "* [[$ x $]]"),
    ("in-blockquote", "> [[$ x $]]"),
    ("in-div", "[[div]]\n[[$ x $]]\n[[/div]]"),
    ("in-code", "[[code]][[$ x $]][[/code]]"),
    ("in-raw", "@@ [[$ x $]] @@"),
    ("in-comment", "[!-- [[$ x $]] --]"),
    ("before-heading", "[[$ x $]]\n+ Head"),
    ("math-block-then-inline", "[[math]]\nx\n[[/math]]\n[[$ y $]]"),
    ("inline-then-math-block", "[[$ y $]]\n[[math]]\nx\n[[/math]]"),
    ("in-footnote", "[[footnote]][[$ x $]][[/footnote]]"),
    ("in-collapsible", "[[collapsible]][[$ x $]][[/collapsible]]"),

    # --- comment / dollar closer seams ----------------------------------
    ("comment-inside", "[[$ a[!--c--]b $]]"),
    ("comment-joined-close-1", "[[$ a $[!--c--]]]"),
    ("comment-joined-close-2", "[[$ a $][!--c--]]]"),
    ("raw-inside", "[[$ a@@raw@@b $]]"),
    ("crlf", "[[$ x $]]\r\n[[$ y $]]\r\n"),
    ("trailing-newline", "[[$ x $]]\n"),
]


def main():
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        for name, source in CASES:
            fh.write(json.dumps({"id": name, "source": source},
                                ensure_ascii=False) + "\n")
    print(f"wrote {len(CASES)} cases to {OUT}")


if __name__ == "__main__":
    main()
