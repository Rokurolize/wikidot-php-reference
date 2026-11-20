#!/usr/bin/env python3
"""Compare reference render output with the ftml dumper and live captures.

Usage: python3 compare.py ref-render-before.jsonl [--live probes/live-accepted.jsonl]
The frame join surface (repeated blank lines, <br /> versus <br>, page-edge
newlines and fossil pretty-print leading spaces) is normalized away so that
only rule-level tag, attribute, body and whitespace differences count. The
report also gives the byte-identical count before normalization. Live captures,
when supplied, carry {"id","source","html"} records with mask applied.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(path):
    out = {}
    with open(path, encoding="utf-8") as handle:
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
    text = "\n".join(line.lstrip(" ") for line in text.split("\n"))
    return text.strip("\n")


def compare(ref, other, label):
    same, byte_same, diff = 0, 0, []
    for cid in sorted(ref):
        r = ref[cid].get("output", "ERR:" + ref[cid].get("error", ""))
        o = other.get(cid, {}).get("html", other.get(cid, {}).get("output", "MISSING"))
        if r == o:
            byte_same += 1
        if shape(r) == shape(o):
            same += 1
        else:
            diff.append((cid, r, o))
    print("vs %s: total=%d shaped_same=%d byte_same=%d diff=%d" % (label, len(ref), same, byte_same, len(diff)))
    for cid, r, o in diff:
        print("=== %s\n  ref: %r\n  %s: %r" % (cid, r[:300], label, o[:300]))
    return same, len(diff)


def main():
    args = sys.argv[1:]
    ref_path = args[0] if args else "ref-render-final.jsonl"
    live_path = None
    if "--live" in args:
        live_path = args[args.index("--live") + 1]
    ref = load(ROOT / ref_path)
    ftml = load(ROOT / "ftml-dump.jsonl")
    compare(ref, ftml, "ftml")
    if live_path:
        live = load(ROOT / live_path)
        compare(ref, live, "live")


if __name__ == "__main__":
    main()
