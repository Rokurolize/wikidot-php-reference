#!/usr/bin/env python3
"""Generate R2-PARA paragraph-owner live probe cases.

Every source is LF-only, has no trailing newline and no trailing whitespace:
Wikidot strips trailing whitespace on save, which would break
saved_source_matches. Tabs appear only inside lines. The two probe groups set
the two routed open items: (A) whether the flow-text whitespace collapse is
paragraph-owned, and (B) whether the score span / scored opener suppresses the
paragraph wrapper. Group C gives same-owner controls for paragraph formation.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe-cases.jsonl")

cases = []


def add(cid, source):
    cases.append({"id": cid, "source": source})


# A. Whitespace-run collapse: does it happen with no paragraph wrapper?
add("p01-tab-flow", "TABSTART word1\tword2 TABEND")
add("p02-tab-in-scored-span", "[[span_]]word1\tword2[[/span]]")
add("p03-tab-in-plain-span", "[[span]]word1\tword2[[/span]]")
add("p04-tab-in-code", "[[code]]word1\tword2[[/code]]")
add("p05-multispace-flow", "word1    word2")
add("p06-tab-near-edges", "A\tword\tB")
add("p07-multispace-in-scored-span", "[[span_]]word1    word2[[/span]]")

# B. Score-span paragraph suppression.
add("p08-scored-span-alone", "[[span_]]X[[/span]]")
add("p09-score-class-span-alone", '[[span class="score"]]100[[/span]]')
add("p10-score-class-with-text", 'before\n[[span class="score"]]100[[/span]]\nafter')
add("p11-scored-span-with-text", "before\n[[span_]]X[[/span]]\nafter")
add("p12-score-class-inline", 'A [[span class="score"]]100[[/span]] B')
add("p13-plain-span-alone", "[[span]]X[[/span]]")
add("p14-other-class-span-alone", '[[span class="other"]]X[[/span]]')
add("p15-score-class-in-div", '[[div]]\n[[span class="score"]]100[[/span]]\n[[/div]]')
add("p16-score-class-double-blank", 'before\n\n[[span class="score"]]100[[/span]]\n\nafter')
add("p17-scored-span-double-blank", "before\n\n[[span_]]X[[/span]]\n\nafter")

# C. Paragraph-formation controls in this owner's matching space.
add("p18-two-paragraphs", "first\n\nsecond")
add("p19-blank-then-text", "A\n\nlead")
add("p20-text-then-blank", "tail\n\nEND")
add("p21-blank-run", "a\n\n\n\nb")
add("p22-tab-in-line", "a\nb\tc\n\nc")
add("p23-heading-then-text", "= Heading =\n\ntext")
add("p24-div-then-text", "[[div]]block[[/div]]\n\ntext")
add("p25-code-then-text", "[[code]]\ncode\n[[/code]]\n\ntext")
add("p26-single-newline", "line one\nline two")

with open(OUT, "w", encoding="utf-8") as f:
    for c in cases:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
print("wrote", OUT, len(cases), "cases")
