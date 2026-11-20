#!/usr/bin/env python3
"""Build the Typography rule's whole-document battery for R2-INLINE3.

Typography is the whole-document replacement pass that runs after Strikethrough,
Tt, Superscript and Subscript and before Tighten.  Every case here is a full
document (LF-only, no trailing whitespace, with a sentinel paragraph where an
empty shape would otherwise be trimmed), matching what Wikidot stores on save.
Coverage: dash runs of every length 1..10 both bare and adjacent to words,
ellipses in both spellings and in long dot runs, straight/backtick/low quote
forms, French guillemets and their line-start blockquote gate, number-space-
digit and number-plus-unit spacing with negative lookahead collisions, ordinary
hyphens/negative numbers/URLs/code/comment/attribute/math shields, crossings
with every sibling inline marker, and line-break and block boundaries.  The
probe subset is the set of shapes whose live spelling cannot be settled from
the ftml corpus pins alone; its ids are battery ids so the three sides join.
"""
import json
import os

CASES = [
    # dash runs, bare and adjacent to words (typo01-typo20)
    ("typo01", "-"),
    ("typo02", "a - b\nx"),
    ("typo03", "a-b\nx"),
    ("typo04", "--\nx"),
    ("typo05", "a--b\nx"),
    ("typo06", "---\nx"),
    ("typo07", "a---b\nx"),
    ("typo08", "----\nx"),
    ("typo09", "a----b\nx"),
    ("typo10", "-----\nx"),
    ("typo11", "a-----b\nx"),
    ("typo12", "------\nx"),
    ("typo13", "a------b\nx"),
    ("typo14", "-------\nx"),
    ("typo15", "a-------b\nx"),
    ("typo16", "--------\nx"),
    ("typo17", "a--------b\nx"),
    ("typo18", "----------\nx"),
    ("typo19", "a----------b\nx"),
    ("typo20", "word-- --word\nx"),
    # ellipses (typo21-typo30)
    ("typo21", "wait... what"),
    ("typo22", "wait. . . what"),
    ("typo23", "...leading"),
    ("typo24", "trailing..."),
    ("typo25", "....."),
    ("typo26", "......"),
    ("typo27", "... . . . . . ."),
    ("typo28", ". . .. ...."),
    ("typo29", "x... ...y. . . z"),
    ("typo30", "word ... word\nx"),
    # quote forms (typo31-typo42)
    ("typo31", "``double''\nx"),
    ("typo32", "`single'\nx"),
    ("typo33", ",,low''\nx"),
    ("typo34", "``outer ``inner'' outer''\nx"),
    ("typo35", "`one\nline'\nx"),
    ("typo36", "`one\n\nline'\nx"),
    ("typo37", "a``b''c\nx"),
    ("typo38", ",,lower'' and ``upper''\nx"),
    ("typo39", "unpaired`` and ''\nx"),
    ("typo40", "``multi\nline''\nx"),
    ("typo41", "a ' b ` c\nx"),
    ("typo42", "``a''b''c''\nx"),
    # guillemets (typo43-typo48)
    ("typo43", "<<French quotes>>\nx"),
    ("typo44", "<<open only\nx"),
    ("typo45", "close only>>\nx"),
    ("typo46", "a >> b\nx"),
    ("typo47", ">> quoted line\nx"),
    ("typo48", "<<<triple>>>\nx"),
    # number and unit spacing (typo49-typo60)
    ("typo49", "1 234 567\nx"),
    ("typo50", "12 kg\nx"),
    ("typo51", "12 m\nx"),
    ("typo52", "12 Mpx\nx"),
    ("typo53", "12 foo\nx"),
    ("typo54", "12 kgx\nx"),
    ("typo55", "3.5 kg\nx"),
    ("typo56", "1 2 3 kg 4\nx"),
    ("typo57", "10 %\nx"),
    ("typo58", "100 \u00b0C\nx"),
    ("typo59", "5 km/h\nx"),
    ("typo60", "-12 34 and -7 kg\nx"),
    # collision and shield forms (typo61-typo70)
    ("typo61", "http://example.com/a--b?x=1 2\nx"),
    ("typo62", "[https://example.com Label ... --]\nx"),
    ("typo63", "[[code]]\na--b...12 kg\n[[/code]]\nx"),
    ("typo64", "[[raw]]a--b...12 kg[[/raw]]\nx"),
    ("typo65", "$a--b...12 kg$\nx"),
    ("typo66", "[!-- a--b...12 kg --]\nx"),
    ("typo67", "{{a--b...12 kg}}\nx"),
    ("typo68", "[[div style=\"a--b...12 kg\"]]x[[/div]]\nx"),
    ("typo69", "[[a href=\"http://x/a--b\"]]label[[/a]]\nx"),
    ("typo70", "[[date 123 45]]\nx"),
    # crossings with sibling inline markers (typo71-typo80)
    ("typo71", "**a--b**c--\nx"),
    ("typo72", "//a--b//c--\nx"),
    ("typo73", "__a--b__c--\nx"),
    ("typo74", "--a...b--\nx"),
    ("typo75", "##c00|a--b...12 kg##\nx"),
    ("typo76", "{{a--b}}c--\nx"),
    ("typo77", "^^a--b^^c--\nx"),
    ("typo78", ",,a--b,,c--\nx"),
    ("typo79", ",,OUTER ...INNER,, TAIL...\nx"),
    ("typo80", "a--b^^c...d,,e''\nx"),
    # line breaks and block boundaries (typo81-typo88)
    ("typo81", "a--b\nc--d\nx"),
    ("typo82", "a--b\n\nc--d\nx"),
    ("typo83", "= Heading -- ... =\nx"),
    ("typo84", "before\n----\nafter...\nx"),
    ("typo85", "* item -- ...\n* item2\nx"),
    ("typo86", "|| cell--cell || ... ||\nx"),
    ("typo87", "a--b\n> quote--tail\nx"),
    ("typo88", "[[footnote]]a--b...12 kg[[/footnote]]\nx"),
    # entity-spelled and symbolic units (typo89-typo92)
    ("typo89", "12 &euro;\nx"),
    ("typo90", "5 &micro;m\nx"),
    ("typo91", "9 \u03a9 and 3 Ohm\nx"),
    ("typo92", "20 &deg;C\nx"),
]

# Shapes whose live spelling pins cannot settle: entity spellings for every
# replacement class, the dead-code-looking triple-dash path, shields, and the
# sibling crossings that decide whether Typography sees tokenized or raw bytes.
PROBE_IDS = [
    "typo01", "typo02", "typo03", "typo04", "typo05", "typo06", "typo07",
    "typo09", "typo11", "typo13", "typo15", "typo17", "typo19", "typo20",
    "typo21", "typo22", "typo23", "typo25", "typo27", "typo29",
    "typo31", "typo32", "typo33", "typo34", "typo35", "typo36", "typo38",
    "typo43", "typo44", "typo45", "typo46", "typo47",
    "typo49", "typo50", "typo52", "typo53", "typo54", "typo56",
    "typo61", "typo63", "typo64", "typo65", "typo66", "typo67", "typo68",
    "typo71", "typo72", "typo74", "typo75", "typo77", "typo78",
    "typo81", "typo82", "typo83", "typo85",
]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    by_id = {cid: src for cid, src in CASES}
    with open(os.path.join(here, "battery.jsonl"), "w", encoding="utf-8") as fh:
        for cid, src in CASES:
            fh.write(json.dumps({"id": cid, "source": src}, ensure_ascii=False) + "\n")
    with open(os.path.join(here, "probe-cases.jsonl"), "w", encoding="utf-8") as fh:
        for cid in PROBE_IDS:
            fh.write(json.dumps({"id": cid, "source": by_id[cid]}, ensure_ascii=False) + "\n")
    print(f"wrote {len(CASES)} battery cases and {len(PROBE_IDS)} probe cases")


if __name__ == "__main__":
    main()
