#!/usr/bin/env python3
"""Three-way Freelink battery comparison. Reads battery.jsonl plus the chosen
reference render file and the ftml dumper file from this directory, prints a
per-case side-by-side table and a summary. `argv[1]` selects the reference file
(default ref-render-after.jsonl). Shape comparison canonicalizes the known
frame-level surface differences: the reference leaves trailing newlines, and
the ftml dumper has no page-existence notion so it never emits newpage class.
Neither is treated as a Freelink rule divergence."""
import json
import os
import re
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
REF_FILE = sys.argv[1] if len(sys.argv) > 1 else "ref-render-after.jsonl"

def load(name):
    out = {}
    with open(os.path.join(DIR, name), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            out[rec["id"]] = rec
    return out

def canon(html):
    if html is None:
        return None
    h = re.sub(r'\s+', '', html)
    h = h.replace('class="newpage"', '')
    return h

def main():
    battery = load("battery.jsonl")
    ref = load(REF_FILE)
    ftml = load("ftml-dump.jsonl")
    stats = {"all3": 0, "ref_ftml": 0, "ftml_only": 0, "ref_only": 0, "none": 0}
    rows = []
    for cid, case in battery.items():
        r = ref.get(cid, {})
        f = ftml.get(cid, {})
        rout = r.get("output", r.get("error", ""))
        fout = f.get("html", f.get("errors", ""))
        rc, fc = canon(rout), canon(fout)
        if rc == fc:
            stats["all3"] += 1
            tag = "REF=FTML"
        else:
            stats["none"] += 1
            tag = "DIFF"
        rows.append((cid, tag, case["source"], rout, fout))
    print(f"reference file: {REF_FILE}")
    print(f"shape agreement ref vs ftml: {stats['all3']}/{len(battery)}; differing {stats['none']}")
    print("=" * 100)
    for cid, tag, src, rout, fout in rows:
        print(f"[{tag}] {cid}: {src!r}")
        print(f"   REF : {rout!r}")
        print(f"   FTML: {fout!r}")

if __name__ == "__main__":
    main()
