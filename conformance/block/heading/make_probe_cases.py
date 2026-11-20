#!/usr/bin/env python3
# Generate the focused live-probe source set. One {id, source} per line.
# These settle shapes the battery and the ftml corpus pins cannot settle
# against the fossil by themselves; live is definitionally correct.
import json

cases = []

def add(cid, source):
    cases.append({"id": cid, "source": source})

# The no-toc *-suffixed form and its effect on the anchor-id counter.
add("p01-notoc-single", "+* no toc one")
add("p02-notoc-interleaved", "+ A\n+* B\n++ C")
add("p09-toc-excludes-notoc", "[[toc]]\n+ A\n++* skip\n++ B")

# Repeated heading text and anchor-id sequencing.
add("p03-same-text", "+ Same\n+ Same\n+ Same")
add("p18-toc-anchors", "[[toc]]\n+ A\n++ B\n+++ C")

# Malformed forms and near-misses.
add("p04-nospace", "+No space")
add("p05-seven", "+++++++ seven")
# p16-empty-body ("+ ") and p12-trailing-spaces ("++ trailing  ") were both
# attempted and could not be saved: Wikidot strips trailing whitespace on save,
# so read-back verification failed. That is a serving-layer save-normalization
# fact; both shapes remain covered by battery h40 and h41 instead. p12 now
# probes an internal double space, which survives the save round trip.
add("p12-internal-space", "++ a  b")
add("p13-double-space", "++  two spaces after prefix")

# Heading text with inline markup, links and entities.
add("p06-inline-em", "+ My //header//")
add("p07-external-link", "+ See [[http://example.com|the site]]")
add("p08-entities", "+ A & B < C > D \"quote\" 'apos'")
add("p11-unicode", "+ Héading 中文 🎉")

# Level and adjacent-block shapes.
add("p10-level6", "++++++ h6")
add("p14-adjacent-div", "+ H\n[[div]]\nd\n[[/div]]")
add("p15-div-barrier", "+ [[div]]\nd[[/div]]")
add("p17-notoc-repeat", "+* Same\n++* Same")

with open("probe-cases.jsonl", "w", encoding="utf-8") as fh:
    for case in cases:
        fh.write(json.dumps(case, ensure_ascii=False) + "\n")
print(f"wrote {len(cases)} probe cases")
