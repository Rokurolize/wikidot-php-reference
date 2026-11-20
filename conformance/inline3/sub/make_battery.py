#!/usr/bin/env python3
# R2-INLINE3 Subscript (rule 51) battery generator.
# Emits whole-document cases as JSONL {"id","source"} for the shared
# reference harness (batch.php render/tokens) and the one shared ftml
# dumper (r2inline3-rust-dump). Categories follow the per-rule brief:
# plain ,, pairs at word boundaries and inside words; ordinary prose
# commas and comma runs (the collision forms); padded, half-padded and
# empty bodies; unpaired and tripled/quadrupled markers; nesting and
# source-order crossings with sibling markers (##color|, **, //, __,
# --, {{}}, ^^); line-break and paragraph-break crossings; block
# boundaries (heading, list, quote, code, raw, div); link labels,
# table cells and typography em-dash/ellipsis seams. Stable ids
# sub01..sub55. probe-cases.jsonl is the same set, for one live pass.
import json

cases = [
    # --- plain ,, pairs: word boundaries and inside words ---
    ("sub01", ",,simple,,"),
    ("sub02", "before ,,subscript,, after"),
    ("sub03", "word,,inside,,word"),
    ("sub04", "a,,b,,c"),
    ("sub05", "x ,,one,, y ,,two,, z"),
    ("sub06", ",,two words inside,,"),
    # --- ordinary prose commas and comma runs (collision forms) ---
    ("sub07", "one, two, three"),
    ("sub08", "word,, word,, word"),
    ("sub09", "a,, b"),
    ("sub10", "a,,b,, c"),
    ("sub11", ",,a ,, b,,"),
    ("sub12", ",,,a,,,"),
    ("sub13", ",,,,four,,,,"),
    ("sub14", "a,,b,,,"),
    ("sub15", ",,,a,,"),
    ("sub16", "Smith,, Jones,, and Doe"),
    ("sub17", "list: a, b,, c, d"),
    ("sub18", "a, ,,b,, c"),
    # --- padded, half-padded and empty bodies ---
    ("sub19", ",,,,"),
    ("sub20", "A,,,,B"),
    ("sub21", ",, padded ,,"),
    ("sub22", ",, padded,,"),
    ("sub23", ",,padded ,,"),
    ("sub24", ",,a,,"),
    ("sub25", ",, , ,"),
    # --- unpaired and tripled/quadrupled markers ---
    ("sub26", ",,unpaired"),
    ("sub27", "unpaired,,"),
    ("sub28", ",,,triple,,,"),
    ("sub29", ",,a,,b,,"),
    ("sub30", ",,,,,five,,,,,"),
    # --- nesting with sibling markers ---
    ("sub31", ",,**bold sub**,,"),
    ("sub32", "**,,sub bold,,**"),
    ("sub33", ",,^^super sub^^,,"),
    ("sub34", ",,//italic sub//,,"),
    ("sub35", ",,##red|colored sub##,,"),
    ("sub36", ",,__underline sub__,,,"),
    ("sub37", ",,--strike sub--,,"),
    ("sub38", ",,{{mono sub}},,"),
    ("sub39", ",,OUTER ^^INNER,, TAIL^^"),
    ("sub40", ",,A **B,, X** Y"),
    ("sub41", "--OUTER ,,INNER-- TAIL,,"),
    # --- line-break and paragraph-break crossings ---
    ("sub42", "a,,x\n,,.b"),
    ("sub43", "x,,a\n,,y"),
    ("sub44", ",,line one\nline two,,"),
    ("sub45", ",,line one\n\nline two,,"),
    # --- block boundaries: heading, list, quote, code, raw, div ---
    ("sub46", "= ,,heading,, ="),
    ("sub47", "* ,,list item,,"),
    ("sub48", "[[code]]\n,,raw sub,,\n[[/code]]"),
    ("sub49", "[[div]]\n,,block sub,,\n[[/div]]"),
    ("sub50", "> ,,quote sub,,"),
    # --- link labels, table cells, typography seams, url collision ---
    ("sub51", "[[http://example.com|,,label,,]]"),
    ("sub52", "|| ,,cell,, ||"),
    ("sub53", "See ,,https://example.com/a,, end"),
    ("sub54", ",,em—dash…ellipsis,,"),
    ("sub55", ",,a,, — ,,b,,"),
]

for name in ("battery.jsonl", "probe-cases.jsonl"):
    with open(name, "w", encoding="utf-8") as f:
        for cid, src in cases:
            f.write(json.dumps({"id": cid, "source": src}, ensure_ascii=False) + "\n")
print(f"wrote {len(cases)} cases to battery.jsonl and probe-cases.jsonl")
