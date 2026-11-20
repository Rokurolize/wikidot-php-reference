#!/usr/bin/env python3
# R2-INLINE2 Emphasis (rule 46) battery generator.
# Emits whole-document cases as JSONL {"id","source"} for the shared
# reference harness (batch.php render/tokens) and the one shared ftml
# dumper (r2inline2-rust-dump). Categories are deliberately spread over
# // pairs, pairing/nesting with sibling markers, unpaired/tripled markers,
# word boundaries and inside words, empty bodies, line/block crossings,
# protocol-relative URL collisions, headings, link labels, and code/raw
# shields, mirroring the brief's required coverage matrix.
import json

cases = [
    # --- plain // pairs ---
    ("em01", "//simple//"),
    ("em02", "before //emphasis// after"),
    ("em03", "//two words inside//"),
    ("em04", "a//b//c"),
    ("em05", "x //one// y //two// z"),
    # --- unpaired and tripled markers ---
    ("em06", "//unpaired"),
    ("em07", "unpaired//"),
    ("em08", "///triple///"),
    ("em09", "////four////"),
    ("em10", "//a//b//"),
    ("em11", "a//b//c//d"),
    ("em12", "////"),
    ("em13", "// //"),
    ("em14", "////em////"),
    # --- padding / word boundaries ---
    ("em15", "// padded //"),
    ("em16", "// padded//"),
    ("em17", "//padded //"),
    ("em18", "word//inside//word"),
    ("em19", "// leadingspace"),
    ("em20", "trailingspace //"),
    # --- nesting with sibling markers ---
    ("em21", "//**bold italic**//"),
    ("em22", "**//italic bold//**"),
    ("em23", "//**crossed//**"),
    ("em24", "//__underline italic__//"),
    ("em25", "//--strike italic--//"),
    ("em26", "//##red|colored italic##//"),
    ("em27", "//before **bold** after//"),
    ("em28", "//**A**// and //**B**//"),
    ("em29", "//**one **two//**"),
    ("em30", "//**Warsaw**//\n**GENIUS //DEPARTMENT//**"),
    # --- line breaks and block boundaries ---
    ("em31", "//line one\nline two//"),
    ("em32", "//line one\n\nline two//"),
    ("em33", "//text\n[[div]]\nblock\n[[/div]]//"),
    ("em34", "//text\n\n[[div]]\nblock\n[[/div]]"),
    ("em35", "* //**Title**// by author\n* //**Title2**// by author"),
    # --- protocol-relative URLs and // inside URLs / text ---
    ("em36", "//example.com/a"),
    ("em37", "//example.com/a//"),
    ("em38", "http://example.com/a"),
    ("em39", "http://example.com//path//"),
    ("em40", "visit //example.com// now"),
    ("em41", "text with a//b in it"),
    ("em42", "https://x.test/a//b//c"),
    # --- headings, link labels, code/raw shields ---
    ("em43", "= //heading italic// ="),
    ("em44", "[[http://example.com|//link label//]]"),
    ("em45", "[[page-name|//label//]]"),
    ("em46", "{{ //code literal// }}"),
    ("em47", "[[code]]\n//raw not italic//\n[[/code]]"),
    ("em48", "[[!-- //commented// --]]\n//live//"),
    ("em49", "[[em]]block italics[[/em]]"),
    ("em50", "//[[iftags +t]]X[[/iftags]]/word//"),
]

with open("battery.jsonl", "w", encoding="utf-8") as f:
    for cid, src in cases:
        f.write(json.dumps({"id": cid, "source": src}, ensure_ascii=False) + "\n")
print(f"wrote {len(cases)} cases")
