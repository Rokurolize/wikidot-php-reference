#!/usr/bin/env python3
"""Generate the root R2-inline2 cross-rule interaction battery.

Owns the marker-shaped crossing matrix the five per-rule batteries cannot own:
ordered crossings and proper-nesting controls of every pair of Colortext,
Strong, Emphasis, Underline and Strikethrough markers, then container, cell,
heading, link-label, URL-collision, unpaired and Typography/Tighten seams.
Sources are LF-only with no trailing newline because Wikidot strips one on save.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

MARKERS = {
    "C": ("##red|", "##"),   # Colortext
    "B": ("**", "**"),       # Strong
    "I": ("//", "//"),       # Emphasis
    "U": ("__", "__"),       # Underline
    "S": ("--", "--"),       # Strikethrough
}


def main():
    cases = []

    def add(cid, source, note):
        cases.append({"id": cid, "source": source, "note": note})

    keys = list(MARKERS)
    n = 0
    for a in keys:
        for b in keys:
            if a == b:
                continue
            ao, ac = MARKERS[a]
            bo, bc = MARKERS[b]
            n += 1
            add(f"x{n:02d}", f"{ao}a{bo}ab{ac}ba{bc}",
                f"cross {a}-outer {b}-inner: {ao} a {bo} ab {ac} ba {bc}")
    for a in keys:
        for b in keys:
            if a == b:
                continue
            ao, ac = MARKERS[a]
            bo, bc = MARKERS[b]
            n += 1
            add(f"x{n:02d}", f"{ao}a{bo}ab{bc}ba{ac}",
                f"nested control {a}-outer {b}-inner: {ao} a {bo} ab {bc} ba {ac}")

    specials = [
        ("all five properly nested, open C B I U S close S U I B C",
         "##red|a**b//c__d--e--d__c//b##a"),
        ("all five openers then closers in forward order C B I U S",
         "##red|**//__--text##end**end//end__end"),
        ("same-marker double nest of each marker in one source",
         "**a** **b** //c// //d// __e__ __f__ --g-- --h--"),
        ("markers crossing a single newline",
         "**bold\na//italic\nb//c**"),
        ("markers crossing a blank-line paragraph break",
         "**bold\n\nacross**"),
        ("colortext crossing a blank-line paragraph break",
         "##red|color\n\nspan##"),
        ("strong crossing a div container opener and closer",
         "**a[[div]]b**c[[/div]]"),
        ("underline crossing a collapsible container opener and closer",
         "__a[[collapsible]]b__c[[/collapsible]]"),
        ("strong crossing a wiki table cell boundary",
         "|| header || header ||\n| **a | b** |\n| c | d |"),
        ("strikethrough crossing a wiki table cell boundary",
         "|| header || header ||\n| --a | b-- |\n| c | d |"),
        ("all five markers inside a described-link label",
         "[https://example.com **b** //i// __u__ --s-- ##red|c##]"),
        ("all five markers inside a double-bracket link label",
         "[[https://example.com|**b** //i// __u__ --s-- ##red|c##]]"),
        ("all five markers inside a heading",
         "= **b** //i// __u__ --s-- ##red|c## ="),
        ("protocol-relative URL colliding with emphasis",
         "//example.com/path// and https://example.com//tail"),
        ("unpaired marker text that Typography and Tighten see",
         "a -- b ... // c ** d __ e ##red|f"),
        ("tripled markers and a hash-run next to colortext",
         "***b*** ///i/// ___u___ ---s--- ###red|t###"),
        ("adjacent same-marker spans",
         "**a****b** //c////d// __e____f__ --g----h--"),
        ("markers inside an inline code shield",
         "@@**b** //i// __u__ --s-- ##red|c##@@"),
        ("markers inside a code block shield",
         "[[code]]**b** //i// __u__ --s-- ##red|c##[[/code]]"),
        ("marker body spanning a list item boundary",
         "* **a\n* b**\n* c"),
        ("marker crossing a footnote body boundary",
         "**a[[footnote]]b**c[[/footnote]]"),
        ("colortext with a marker in its body inside a heading cell",
         "= ##red|**b** //i// ## ="),
        ("protocol-relative URL inside a bold span inside a link label",
         "[https://example.com **//example.com/x//**]"),
    ]
    for note, source in specials:
        n += 1
        add(f"x{n:02d}", source, note)

    out = HERE / "xbattery.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"wrote {out} with {len(cases)} cases")


if __name__ == "__main__":
    main()
