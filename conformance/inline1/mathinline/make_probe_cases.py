#!/usr/bin/env python3
"""Generate probe-cases.jsonl for the live Mathinline probe set.

Sources are LF-only with trailing newlines stripped: Wikidot rewrites line
endings and trailing newlines on save, so an intended source that carries
them fails saved_source_matches. Group A settles the observable math-inline
markup surface, group B the suppress/newline/seam divergences, group C the
neighbour and nesting shapes.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe-cases.jsonl")

CASES = [
    # A: observable math-inline markup surface
    ("basic", "[[$ x^2 $]]"),
    ("trim", "[[$  x  $]]"),
    ("multiple", "[[$ a $]] and [[$ b $]]"),
    ("empty", "[[$$]]"),
    ("html-chars", "[[$ a & b < c $]]"),
    ("unicode", "[[$ \u03b1 $]]"),
    ("label-like", "[[$ label=x $]]"),
    ("adjacent", "[[$a$]][[$b$]]"),

    # B: suppress / newline / seam divergences
    ("single-newline", "[[$ E =\nmc^2 $]]"),
    ("newline-after-opener", "[[$\nx$]]"),
    ("newline-before-closer", "[[$x\n$]]"),
    ("blank-line-inside", "[[$ E =\n\nmc^2 $]]"),
    ("raw-inside", "[[$ a@@raw@@b $]]"),
    ("comment-inside", "[[$ a[!--c--]b $]]"),
    ("triple-close", "[[$x$]]]"),
    ("unterminated", "[[$ x"),
    ("stray-closer", "x $]]"),

    # C: neighbours and nesting
    ("in-span", "[[span class=\"x\"]][[$ y $]][[/span]]"),
    ("in-heading", "+ [[$ x $]]"),
    ("in-table-cell", "|| [[$ a $]] || [[$ b $]] ||"),
    ("in-div", "[[div]]\n[[$ x $]]\n[[/div]]"),
    ("in-list", "* [[$ x $]]"),
    ("in-code", "[[code]][[$ x $]][[/code]]"),
    ("in-raw", "@@ [[$ x $]] @@"),
    ("in-comment", "[!-- [[$ x $]] --]"),
    ("before-heading", "[[$ x $]]\n+ Head"),
    ("math-block-then-inline", "[[math]]\nx\n[[/math]]\n[[$ y $]]"),

    # D: escaping and interior whitespace, pinned for the render correction
    ("quotes", "[[$ a\"b'c $]]"),
    ("gt", "[[$ a > b $]]"),
    ("multispace", "[[$ a   b $]]"),
    ("tab-pad", "[[$\tx\t$]]"),
    ("entity", "[[$ a &amp; b $]]"),
]


def main():
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        for name, source in CASES:
            fh.write(json.dumps({"id": name, "source": source},
                                ensure_ascii=False) + "\n")
    print(f"wrote {len(CASES)} probe cases to {OUT}")


if __name__ == "__main__":
    main()
