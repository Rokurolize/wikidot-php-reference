#!/usr/bin/env python3
"""Generate the R2 Newline (pipeline rule 38) battery of whole-document Wikidot-source cases.

The battery covers the whole matching space of the Newline rule: single line breaks
between text lines (one, two and three in a run), doubled and tripled breaks that
become paragraph splits, leading and trailing newlines, whitespace around a break,
breaks at block-token openers and closers (div, code, quote, heading, hr, table,
list), breaks inside bullet and numbered lists and explicit [[ul]]/[[li]] items,
breaks inside table cells and rows, breaks inside inline spans (bold, span, color,
italic), underscore line breaks, the backslash continuation that Concatlines owns,
comments adjacent to breaks, and mixed whole documents. Every case id is prefixed
n38- so it stays disjoint from the Image and Paragraph owners and root's cross-rule
cases. Sources are LF-only with trailing newlines stripped, matching Wikidot's save
normalization; JSON stores their newlines as escaped \\n. Both the shared reference
harness and the shared ftml dumper accept this JSONL protocol. Reproduce with
`python3 conformance-refphp/para/newline/make_battery.py`.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "battery.jsonl")

CASES = [
    # --- basic single line breaks -------------------------------------------
    ("n38-01-single-break", "alpha\nbeta"),
    ("n38-02-two-breaks", "a\nb\nc"),
    ("n38-03-four-lines", "one\ntwo\nthree\nfour"),
    ("n38-04-doubled-break", "alpha\n\nbeta"),
    ("n38-05-tripled-break", "alpha\n\n\nbeta"),
    ("n38-06-leading-newline", "\nalpha"),
    ("n38-07-trailing-newline", "alpha\n"),
    ("n38-08-only-newlines", "\n\n"),
    ("n38-09-break-with-spaces", "alpha \n beta"),
    ("n38-10-break-with-tabs", "alpha\t\n\tbeta"),
    # --- around block tokens -------------------------------------------------
    ("n38-11-before-div", "text\n[[div]]\nbody\n[[/div]]"),
    ("n38-12-after-div", "[[div]]\nbody\n[[/div]]\ntext"),
    ("n38-13-before-code", "text\n[[code]]\nbody\n[[/code]]"),
    ("n38-14-after-code", "[[code]]\nbody\n[[/code]]\ntext"),
    ("n38-15-before-quote", "text\n> quoted"),
    ("n38-16-after-quote", "> quoted\ntext"),
    ("n38-17-before-heading", "text\n+ Heading"),
    ("n38-18-after-heading", "+ Heading\ntext"),
    ("n38-19-before-hr", "text\n----"),
    ("n38-20-after-hr", "----\ntext"),
    ("n38-21-before-table", "text\n|| a || b ||"),
    ("n38-22-after-table", "|| a || b ||\ntext"),
    ("n38-23-before-ul", "text\n* item"),
    ("n38-24-after-ul", "* item\ntext"),
    ("n38-25-before-ol", "text\n# item"),
    ("n38-26-explicit-ul", "text\n[[ul]]\n[[li]]item\n[[/li]]\n[[/ul]]"),
    # --- inside lists --------------------------------------------------------
    ("n38-27-ul-two-items", "* one\n* two"),
    ("n38-28-ol-two-items", "# one\n# two"),
    ("n38-29-list-continuation", "* one\ncontinued"),
    ("n38-30-list-blank-between", "* one\n\n* two"),
    ("n38-31-nested-list", "* one\n** two\n* three"),
    # --- inside cells --------------------------------------------------------
    ("n38-32-table-two-rows", "|| a || b ||\n|| c || d ||"),
    ("n38-33-table-cell-break", "|| a\nb || c ||"),
    ("n38-34-table-with-leading-text", "text\n|| a || b ||\ntext"),
    # --- doubled and repeated breaks -----------------------------------------
    ("n38-35-doubled-with-space", "a \n\n b"),
    ("n38-36-doubled-after-block", "[[div]]\nx\n[[/div]]\n\nafter"),
    ("n38-37-many-blank", "a\n\n\n\n\nb"),
    # --- inline spans --------------------------------------------------------
    ("n38-38-break-in-bold", "**a\nb**"),
    ("n38-39-break-in-span", "[[span]]a\nb[[/span]]"),
    ("n38-40-break-across-closer", "**a\nb\nc**"),
    ("n38-41-break-in-color", "[[color red]]a\nb[[/color]]"),
    ("n38-42-break-before-closer", "a\n[[/div]]"),
    # --- underscore line breaks ----------------------------------------------
    ("n38-43-underscore-break", "a _\nb"),
    ("n38-44-underscore-doubled", "a _\n\nb"),
    ("n38-45-underscore-space", "a _ \nb"),
    # --- misc and mixed ------------------------------------------------------
    ("n38-46-crlf", "a\r\nb"),
    ("n38-47-mixed-blocks", "a\n\n[[div]]\nx\ny\n[[/div]]\n\n[[code]]\nz\n[[/code]]\n\nb"),
    ("n38-48-break-after-comment", "a[!--c--]\nb"),
    ("n38-49-comment-with-break", "a[!--c\nd--]b"),
    ("n38-50-break-after-freelink", "www.example.com\nb"),
    ("n38-51-escape-continued", "a\\\nb"),
    ("n38-52-break-with-inline-markup", "**bold**\n//italic//"),
    ("n38-53-bq-multiline", "> a\n> b"),
    ("n38-54-bq-blank", "> a\n>\n> b"),
    ("n38-55-break-in-collapsible", "[[collapsible]]\na\nb\n[[/collapsible]]"),
    ("n38-56-empty-doc", ""),
    ("n38-57-space-only", "   "),
    ("n38-58-only-block", "[[div]]\nx\n[[/div]]"),
    ("n38-59-heading-then-text-blank", "+ H\n\ntext"),
    ("n38-60-mixed", "a\nb\n\n* x\n* y\nc\n|| p || q ||\nd"),
]


def main():
    ids = set()
    with open(OUT, "w", encoding="utf-8") as fh:
        for cid, source in CASES:
            assert cid not in ids, "duplicate id: " + cid
            ids.add(cid)
            fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
    print("wrote %d cases to %s" % (len(CASES), OUT))


if __name__ == "__main__":
    main()
