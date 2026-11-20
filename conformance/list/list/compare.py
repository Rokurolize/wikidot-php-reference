#!/usr/bin/env python3
"""Compare reference render and ftml legacy HTML for the R2 List battery.

The frame-level join surface (repeated blank lines, <br /> vs <br>, and
page-edge newlines) is normalized away, following the Form/Raw stage, so
only rule-level tag and body differences are counted.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(path):
    out = {}
    with open(ROOT / path, encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rec = json.loads(line)
                out[rec["id"]] = rec
    return out


def shape(text):
    if not isinstance(text, str):
        return text or ""
    text = text.replace("\r\n", "\n").replace("<br />", "<br>")
    text = re.sub(r"\n{2,}", "\n", text)
    # Frame indentation emitted by the fossil pretty-printer is not a tag
    # difference; strip leading spaces on lines for structural comparison.
    text = "\n".join(line.lstrip(" ") for line in text.split("\n"))
    return text.strip("\n")


ref_path = sys.argv[1] if len(sys.argv) > 1 else "ref-render-before.jsonl"
ref = load(ref_path)
ftml = load("ftml-dump.jsonl")
same, diff = 0, []
for cid in sorted(ref):
    r = ref[cid].get("output", "ERR:" + ref[cid].get("error", ""))
    f = ftml.get(cid, {}).get("html", "MISSING")
    if shape(r) == shape(f):
        same += 1
    else:
        diff.append((cid, r, f))
print("total=%d shaped_same=%d diff=%d" % (len(ref), same, len(diff)))
for cid, r, f in diff:
    print("=== %s\n  ref: %r\n  ftm: %r" % (cid, r[:260], f[:260]))
