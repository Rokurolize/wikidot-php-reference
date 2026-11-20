#!/usr/bin/env python3
"""Generate root's R2-para follow-up interaction battery (xbattery2.jsonl).

Focused cases the main battery could not own: the scored span opener
[[span_]] that the CONTAIN stage routed as a paragraph-suppression question,
in isolation and at block seams; the fossil's [[image ...]]caption[[/image]]
caption form with a trailing sentinel so live cannot trim the shape away;
and the image-inside-paragraph wrapper seam that the stage-start comparison
showed as the largest reference-side interaction gap.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xbattery2.jsonl")

IMG = "[[image http://example.com/a.png]]"

cases = []


def add(cid, source):
    cases.append({"id": cid, "source": source})


# Scored span (the actual R2-CONTAIN residual form).
add("x2-01-scored-span-alone", "[[span_]]100[[/span]]")
add("x2-02-scored-span-with-text", "before\n[[span_]]100[[/span]]\nafter")
add("x2-03-scored-span-in-div", "[[div]]\n[[span_]]100[[/span]]\n[[/div]]")
add("x2-04-scored-span-then-block", "[[span_]]100[[/span]]\n[[div]]x[[/div]]")
add("x2-05-scored-span-then-heading", "[[span_]]100[[/span]]\n= H =\ntext")

# Image caption form with a sentinel so nothing is trimmed on save.
add("x2-06-image-caption-sentinel", IMG + "caption here[[/image]]\n\nsentinel")
add("x2-07-image-caption-link-sentinel", IMG + "click [[http://example.com|here]][[/image]]\n\nsentinel")
add("x2-08-aligned-image-caption-sentinel", "[[=image http://example.com/a.png]]cap[[/image]]\n\nsentinel")
add("x2-09-image-in-paragraph-sentinel", "lead " + IMG + " tail\n\nsentinel")
add("x2-10-image-after-break-sentinel", "line one\n" + IMG + "\nline two\n\nsentinel")

# Image and table wrapper seams with a trailing sentinel.
add("x2-11-text-table-sentinel", "lead\n|| a || b ||\ntail\n\nsentinel")
add("x2-12-text-deflist-sentinel", "lead\n: term : definition\ntail\n\nsentinel")

with open(OUT, "w", encoding="utf-8") as f:
    for c in cases:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
print("wrote", OUT, len(cases), "cases")
