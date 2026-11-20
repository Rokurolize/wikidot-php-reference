#!/usr/bin/env python3
"""Emit the R2-inline3 Tt (monospace) whole-document battery as JSONL.

Each record is {"id": ..., "source": ...}. Case ids tt01.. are stable and are
also used as live-probe page slugs under muse-probe-r2in3-tt-. The cases cover
the fossil /{{({*?.*}*?)}}/U first-fit monospace form: basic pairs and padding,
the inherited em46 padding surface ({{ //code literal// }}), pairing and
nesting with the sibling inline markers (##color|, **, //, __, --), unpaired
and tripled markers, markers at word boundaries and inside words, empty and
vanishing bodies, the exact-zero and closing-brace-run forms, single and double
line breaks, block boundaries (quote, div, code, header, native list), and
code/raw/url shields. Newlines in sources are encoded by json.dumps.
"""
import json

CASES = [
    # Basic pairs, adjacency, word boundaries
    ("tt01", "{{mono}}"),
    ("tt02", "abc {{mono}} def"),
    ("tt03", "ab{{mono}}cd"),
    ("tt04", "{{a}} {{b}}"),
    ("tt05", "{{a}}{{b}}"),
    ("tt06", "before {{x}} after {{y}} tail"),
    # Padding surface (inherited em46 residual)
    ("tt07", "{{ //code literal// }}"),
    ("tt08", "{{ text}}"),
    ("tt09", "{{text }}"),
    ("tt10", "{{ text }}"),
    ("tt11", "before {{   a  **b**  c   }} after"),
    ("tt12", "{{x }}{{ y}}"),
    ("tt13", "before{{ x}}after"),
    ("tt14", "{{\ttext}}"),
    ("tt15", "{{text\t}}"),
    ("tt16", "{{ x }}after"),
    # Empty and vanishing bodies
    ("tt17", "{{}}"),
    ("tt18", "{{ }}"),
    ("tt19", "{{   }}"),
    ("tt20", "{{0}}"),
    ("tt21", "A{{0}}B"),
    ("tt22", "{{00}}"),
    ("tt23", "{{-0}}"),
    ("tt24", "{{0.0}}"),
    # Closing-brace runs and nested openers
    ("tt25", "{{x}}}}tail"),
    ("tt26", "{{x }}}}tail"),
    ("tt27", "{{x}}}}}}tail"),
    ("tt28", "{{outer {{ inner }} tail}}"),
    ("tt29", "{{a {{b}} c}} {{d}}"),
    # Sibling marker nesting and crossing
    ("tt30", "{{**bold**}}"),
    ("tt31", "**{{mono}}**"),
    ("tt32", "{{//italic//}}"),
    ("tt33", "{{__under__}}"),
    ("tt34", "{{--strike--}}"),
    ("tt35", "{{##red|color##}}"),
    ("tt36", "##red|{{mono}}##"),
    ("tt37", "{{a **b** c}}"),
    # Unpaired and tripled markers
    ("tt38", "{{mono"),
    ("tt39", "mono}}"),
    ("tt40", "{{{mono}}}"),
    ("tt41", "{{ x"),
    ("tt42", "{{ x }"),
    ("tt43", "}}Fail\n{{Fail\n\nparagraph? }}"),
    # Line breaks
    ("tt44", "{{a\nb}}"),
    ("tt45", "{{a\n\nb}}"),
    ("tt46", "{{a\nb\nc}}"),
    ("tt47", "{{a}}\n{{b}}"),
    # Block boundaries
    ("tt48", "> {{quoted}}"),
    ("tt49", "{{a\n* item\nb}}"),
    ("tt50", "[[div]]\n{{a}}\n[[/div]]"),
    ("tt51", "= {{heading}}"),
    # Shields
    ("tt52", "[[code]]\n{{not mono}}\n[[/code]]"),
    ("tt53", "[[raw]]{{not mono}}[[/raw]]"),
    ("tt54", "{{person@scp.foundation}}"),
    ("tt55", "See {{https://example.com/a}}. end"),
]

with open("battery.jsonl", "w", encoding="utf-8") as fh:
    for case_id, source in CASES:
        fh.write(json.dumps({"id": case_id, "source": source}, ensure_ascii=False) + "\n")
print(f"wrote {len(CASES)} cases")
