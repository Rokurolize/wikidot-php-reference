#!/usr/bin/env python3
"""Build the Strong rule's whole-document battery for R2-INLINE2.

Sources are LF-only with no trailing whitespace, matching what Wikidot stores
on save; a trailing sentinel paragraph is used where an empty shape would
otherwise be trimmed.  Each case is a full document, not a fragment.
"""
import json

cases = [
    # basic pairs
    ("s01", "**bold**"),
    ("s02", "before **bold** after"),
    ("s03", "**one** **two**"),
    ("s04", "**a**b**c**"),
    ("s05", "wor**d**in"),
    ("s06", "**two words**"),
    # padding and word boundaries
    ("s07", "** bold **"),
    ("s08", "**bold **"),
    ("s09", "** bold**"),
    ("s10", "**a b**"),
    ("s11", "** a**b** **"),
    ("s12", "**a** ** b ** **c**"),
    # unpaired, tripled, empty
    ("s13", "**unpaired"),
    ("s14", "unpaired**"),
    ("s15", "***triple***"),
    ("s16", "**a***"),
    ("s17", "***a**"),
    ("s18", "****"),
    ("s19", "** **"),
    ("s20", "**a****b**"),
    # nesting with sibling markers
    ("s21", "**//em//**"),
    ("s22", "//**bold**//"),
    ("s23", "**__u__**"),
    ("s24", "**--s--**"),
    ("s25", "##c00|**red bold**##"),
    ("s26", "**##c00|red##**"),
    ("s27", "**{{mono}}**"),
    ("s28", "{{**mono**}}"),
    ("s29", "**^^sup^^**"),
    ("s30", "**,,sub,,**"),
    # line breaks and block boundaries
    ("s31", "**a\nb**\nx"),
    ("s32", "**a\n\nb**\nx"),
    ("s33", "**a\n----\nb**\nx"),
    ("s34", "**a\n[!-- c --]\nb**\nx"),
    ("s35", "**a\nb**\n\nx"),
    ("s36", "**a\n> quote\nb**\nx"),
    ("s37", "**[[div]]inside[[/div]]**\nx"),
    ("s38", "**a\n* list\nb**\nx"),
    # table cells
    ("s39", "|| **A** || B ||\nx"),
    ("s40", "|| **A || B** || C ||\nx"),
    ("s41", "||a||**b**||c||\nx"),
    ("s42", "|| ** A ** ||\nx"),
    ("s43", "|||| **span** |||| x ||\nx"),
    # headings and link labels
    ("s44", "= **Head** =\nx"),
    ("s45", "**= Head =**\nx"),
    ("s46", "[[**label**|target]]"),
    ("s47", "[[target|**label**]]"),
    ("s48", "[[**page**]]"),
    # code and raw shields
    ("s49", "[code]**bold**[/code]"),
    ("s50", "{{**mono**}}"),
    ("s51", "[[raw]]**x**[[/raw]]"),
    ("s52", "`**code**`"),
    ("s53", "[code]\n**bold**\n[/code]"),
    ("s54", "**a[code]x[/code]b**"),
    ("s55", "[[code]]**bold**[[/code]]"),
    ("s56", "**a\n[[div]]\nb\n[[/div]]\nc**\nx"),
    # real Wikidot link labels (triple-bracket) and anchor-block bodies
    ("s57", "[[[**caption**|target]]]\nx"),
    ("s58", "[[[target|**caption**]]]\nx"),
    ("s59", "[[a href=\"https://example.com\"]]**label**[[/a]]\nx"),
    ("s60", "[[[**page**]]]\nx"),
]

if __name__ == "__main__":
    with open("battery.jsonl", "w") as f:
        for cid, src in cases:
            f.write(json.dumps({"id": cid, "source": src}, ensure_ascii=False) + "\n")
    print(f"wrote {len(cases)} cases")
