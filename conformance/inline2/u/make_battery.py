#!/usr/bin/env python3
"""Generate the R2-inline2 Underline (rule 47) whole-document battery.

Each record is {"id","source"} as consumed by both the shared reference
harness ref-php/harness/batch.php and the one shared ftml dumper. Sources are
kept as literal Wikitext; a parallel battery-notes.md records intent.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# (id, source, intent)
CASES = [
    ("u01", "__simple__", "basic __ pair"),
    ("u02", "__Underline__ test", "basic pair then trailing text (native pin)"),
    ("u03", "lead __mid__ tail", "pair embedded mid-line"),
    ("u04", "__a__ and __b__", "two pairs on one line"),
    ("u05", "__a b c__", "space-bearing body"),
    ("u06", "x__a__y", "pair inside a word, markers at non-boundaries"),

    ("u07", "__a **b** c__", "underline outer, strong inner"),
    ("u08", "__a //b// c__", "underline outer, emphasis inner"),
    ("u09", "__a --b-- c__", "underline outer, strike inner"),
    ("u10", "__a ##red|b## c__", "underline outer, color inner"),
    ("u11", "__a ##red|b c## d__", "underline outer, spaced color body inner"),
    ("u12", "**a __b__ c**", "strong outer, underline inner"),
    ("u13", "//italic __b__ c//", "emphasis outer, underline inner"),
    ("u14", "--a __b-- c__", "crossed strike/underline close (corpus pin)"),
    ("u15", "##red|a __b__## c", "color outer, underline inner"),
    ("u16", "__A --B **C__ X-- Y**", "crossed underline/strike/strong (corpus pin)"),
    ("u17", "**A __B ##red|C** X__ Y##", "crossed strong/underline/color (corpus pin)"),

    ("u18", "__unmatched", "unpaired opener"),
    ("u19", "unmatched__", "unpaired closer"),
    ("u20", "___triple", "tripled opener"),
    ("u21", "triple___", "tripled closer"),
    ("u22", "____", "empty pair (four underscores)"),
    ("u23", "a____b", "empty pair inside a word"),
    ("u24", "______", "six-underscore run"),
    ("u25", "x________y", "eight-underscore run (corpus pin)"),
    ("u26", "______ ______", "empty pair run plus spaced run (corpus pin)"),
    ("u27", "______x", "six-underscore run before content (corpus pin)"),
    ("u28", "__a___b__", "tripled marker inside a pair"),

    ("u29", "__ word__", "leading-space body (padded open)"),
    ("u30", "__word __", "trailing-space body (padded close)"),
    ("u31", "__ word __", "both-padded body"),
    ("u32", "__a __ b__", "padded inner marker skipped (corpus pin)"),
    ("u33", "a__b__c", "pair wholly inside a word"),
    ("u34", "__-punct-__", "punctuation body"),
    ("u35", "__a_b__", "single underscore inside body"),

    ("u36", "__a\nb__", "pair crossing a single line break"),
    ("u37", "x__a\n__y", "newline inside pair, break plus space (corpus pin)"),
    ("u38", "__a\n\nb__", "pair crossing a blank line / paragraph break"),
    ("u39", "__a\n+++ heading\nb__", "pair crossing a heading boundary"),
    ("u40", "__a\n[[div]]x[[/div]]b__", "pair crossing a div block"),
    ("u41", "__a\n* b\nc__", "pair crossing a list boundary"),

    ("u42", "foo_bar_baz", "single-underscore identifier, no pair"),
    ("u43", "__init__", "dunder identifier form"),
    ("u44", "some_variable_name __paired__ x", "identifier plus a real pair"),
    ("u45", "[[code]]__not underlined__[[/code]]", "code block shield"),
    ("u46", "{{{ __raw__ }}}", "raw block shield"),
    ("u47", "inline `__code__` tail", "backtick inline code shield"),

    ("u48", "+++ __heading__", "underline inside heading"),
    ("u49", "++ __a__ and __b__", "two pairs inside a heading"),
    ("u50", '[[a href="http://x"]]__label__[[/a]]', "underline inside anchor label"),
    ("u51", "[__label__ http://x]", "underline inside described-link label"),
    ("u52", '[[a href="#x"]]__a\nb__[[/a]]', "underline crossing newline in anchor"),

    ("u53", "x__##red| ##y__z", "whitespace/color hoist (corpus pin)"),
    ("u54", "__x [[/div]] y__", "stray close block inside pair (corpus pin)"),
    ("u55", "a __ b", "two padded single markers, no valid pair"),
    ("u56", "__a__\n__b__", "two pairs on consecutive lines"),
    ("u57", "____a____", "empty-pair runs adjacent to content"),
    ("u58", "______[[/span]]", "empty run with stray close (corpus pin)"),
    ("u59", "> __quoted__", "underline in blockquote"),
    ("u60", "|| __head__ ||\n|| __cell__ ||", "underline in table cells"),
]


def main():
    with open(os.path.join(HERE, "battery.jsonl"), "w", encoding="utf-8") as f:
        for cid, src, _ in CASES:
            f.write(json.dumps({"id": cid, "source": src}, ensure_ascii=False) + "\n")
    with open(os.path.join(HERE, "battery-notes.md"), "w", encoding="utf-8") as f:
        f.write("# R2-inline2 Underline battery notes\n\n")
        for cid, src, intent in CASES:
            shown = src.replace("\\", "\\\\").replace("\n", "\\n")
            f.write(f"- {cid}: {intent} | source: `{shown}`\n")
    print(f"wrote {len(CASES)} cases")


if __name__ == "__main__":
    main()
