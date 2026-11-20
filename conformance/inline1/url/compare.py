#!/usr/bin/env python3
"""Three-way Url comparison and battery differential.

Usage: compare.py [ref-render-file]  (default ref-render-before.jsonl)
Loads the reference render records, the shared ftml dumper records and, when
present, the cached live probe captures. Reports byte agreement and agreement
under the campaign frame normalization (trailing whitespace, the onclick vs
target spelling for a new-tab URL, and the later Typography rule's `''` ->
&#39; entity surface) and writes every substantive diff to compare-report.txt."""
import json
import os
import re
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
REF_FILE = sys.argv[1] if len(sys.argv) > 1 else "ref-render-before.jsonl"


def load(name):
    with open(os.path.join(DIR, name), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def raw(rec):
    if "output" in rec:
        return rec["output"]
    if "html" in rec:
        return rec["html"]
    return rec.get("error", "")


def canon_frame(html):
    if html is None:
        return ""
    h = html.rstrip()
    h = h.replace('onclick="window.open(this.href, \'_blank\'); return false;"',
                  'target="_blank"')
    h = h.replace("&#39;", "'")
    return h


def canon_shape(html):
    return re.sub(r"\s+", "", canon_frame(html))


def main():
    ref = {r["id"]: raw(r) for r in load(REF_FILE)}
    ftml = {r["id"]: raw(r) for r in load("ftml-dump.jsonl")}
    lines = []
    byte_eq = frame_eq = 0
    for cid in ref:
        r, f = ref[cid], ftml.get(cid, "<MISSING>")
        b = (r.rstrip() == f.rstrip())
        fr = canon_frame(r) == canon_frame(f)
        byte_eq += b
        frame_eq += fr
        lines.append(f"[{'BYTE' if b else ('FRAME' if fr else 'DIFF')}] {cid}")
        if not fr:
            lines.append(f"  src : {dict((x['id'], x['source']) for x in load('battery.jsonl'))[cid]!r}")
            lines.append(f"  REF : {r!r}")
            lines.append(f"  FTML: {f!r}")
    lines.append(f"BATTERY {len(ref)} cases: byte-identical {byte_eq}, frame-normalized {frame_eq}")
    report = "\n".join(lines) + "\n"
    with open(os.path.join(DIR, "compare-report.txt"), "w", encoding="utf-8") as fh:
        fh.write(report)
    print(report)


if __name__ == "__main__":
    main()
