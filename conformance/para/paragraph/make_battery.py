#!/usr/bin/env python3
"""Generate the R2 paragraph owner's whole-document conformance battery.

Groups: blank-line splitting (pg01-pg10), single-line runs and inline content
(pg11-pg16), leading/trailing whitespace runs including tabs (pg17-pg26),
empty and whitespace-only runs (pg27-pg32), block neighbours above and below
(pg33-pg46), and the suppression forms including the scored and score-class
spans (pg47-pg56). Sources are LF-only; where a source is meant to be
live-savable it also has no trailing newline and no trailing whitespace,
because Wikidot strips trailing whitespace on save. The trailing-whitespace
cases are deliberately reference-and-dumper-only and are marked as such in
the section; the live probes cover the savable proxies.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "battery.jsonl")

cases = []


def add(cid, source, note=""):
    # The note is documentation only; it never enters the JSONL record, whose
    # optional "tags" field is reserved for the harness's Iftags page gates.
    if note:
        NOTES[cid] = note
    cases.append({"id": cid, "source": source})


NOTES = {}


# A. Blank-line splitting.
add("pg01-single-paragraph", "one paragraph line")
add("pg02-two-paragraphs", "first\n\nsecond")
add("pg03-three-paragraphs", "one\n\ntwo\n\nthree")
add("pg04-multiple-blank-lines", "one\n\n\n\n\ntwo")
add("pg05-leading-blank-lines", "\n\nlead")
add("pg06-trailing-blank-lines", "tail\n\n")
add("pg07-leading-and-trailing-blanks", "\n\nbody\n\n")
add("pg08-blank-between-white-lines", "a\n \n\nb")
add("pg09-blank-between-tab-lines", "a\n\t\n\nb")
add("pg10-blank-between-formfeed-lines", "a\n\x0c\n\nb")

# B. Single-line runs and inline content.
add("pg11-single-line", "only one line")
add("pg12-single-line-inline", "plain ''em'' and **strong** text")
add("pg13-two-lines-single-break", "line one\nline two")
add("pg14-three-lines-single-breaks", "one\ntwo\nthree")
add("pg15-inline-span-run", "before [[span]]inside[[/span]] after")
add("pg16-inline-link-run", "see [[http://example.com|example]] now")

# C. Leading and trailing whitespace runs, including tabs.
add("pg17-leading-spaces", "   hello world")
add("pg18-leading-tab", "\thello world")
add("pg19-leading-mixed", " \t  hello world")
add("pg20-trailing-spaces", "hello world   ", "unsavable-trailing-ws")
add("pg21-trailing-tab", "hello world\t", "unsavable-trailing-ws")
add("pg22-trailing-mixed", "hello world \t  ", "unsavable-trailing-ws")
add("pg23-both-edges", "  \thello world\t  ", "unsavable-trailing-ws")
add("pg24-tab-inside-flow", "word1\tword2")
add("pg25-multiple-spaces-inside-flow", "word1    word2")
add("pg26-tab-at-run-boundary", "first line\t\n\nsecond line", "unsavable-trailing-ws")

# D. Empty and whitespace-only runs.
add("pg27-empty-document", "")
add("pg28-only-newlines", "\n\n\n")
add("pg29-only-spaces", "   ")
add("pg30-only-tabs", "\t\t")
add("pg31-whitespace-run-between-text", "a\n\n  \t \n\nb")
add("pg32-blank-then-whitespace-only", "a\n\n   \n\n \t\n")

# E. Block neighbours above and below.
add("pg33-heading-above", "= Heading =\n\ntext after")
add("pg34-heading-below", "text before\n\n= Heading =")
add("pg35-div-above", "[[div]]block[[/div]]\n\ntext after")
add("pg36-div-below", "text before\n\n[[div]]block[[/div]]")
add("pg37-code-above", "[[code]]\ncode\n[[/code]]\n\ntext after")
add("pg38-code-below", "text before\n\n[[code]]\ncode\n[[/code]]")
add("pg39-list-above", "* item\n\ntext after")
add("pg40-list-below", "text before\n\n* item")
add("pg41-table-above", "|| a || b ||\n\ntext after")
add("pg42-table-below", "text before\n\n|| a || b ||")
add("pg43-horiz-between", "above\n\n----\n\nbelow")
add("pg44-quote-between", "above\n\n> quoted\n\nbelow")
add("pg45-text-div-text", "lead\n[[div]]inner[[/div]]\ntail")
add("pg46-mixed-blocks", "start\n\n= H =\n\nmid\n\n* a\n* b\n\nend")

# F. Suppression forms: block openers and the two scored-span shapes.
add("pg47-only-div", "[[div]]block[[/div]]")
add("pg48-only-code", "[[code]]\ncode\n[[/code]]")
add("pg49-only-heading", "= Heading =")
add("pg50-only-list", "* item")
add("pg51-only-table", "|| a || b ||")
add("pg52-only-quote", "> quoted")
add("pg53-plain-span-run", "[[span]]X[[/span]]")
add("pg54-scored-span-alone", "[[span_]]X[[/span]]")
add("pg55-score-class-span-alone", '[[span class="score"]]100[[/span]]')
add("pg56-score-class-with-text", 'before\n[[span class="score"]]100[[/span]]\nafter')

with open(OUT, "w", encoding="utf-8") as f:
    for c in cases:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
with open(os.path.join(os.path.dirname(OUT), "battery-notes.json"), "w", encoding="utf-8") as f:
    json.dump(NOTES, f, ensure_ascii=False, indent=1)
print("wrote", OUT, len(cases), "cases")
