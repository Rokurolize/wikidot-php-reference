#!/usr/bin/env python3
"""Three-way Freelink live-probe comparison: reference (before/after), ftml
dumper, and frozen live captures. argv[1] selects the reference file (default
ref-probe-render-after.jsonl). Normalizes the known frame surface (newpage
class from the reference existence callback, trailing newlines, br spelling)
so the table shows substantive divergences."""
import json
import os
import re
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
REF_FILE = sys.argv[1] if len(sys.argv) > 1 else "ref-probe-render-after.jsonl"

def load(name):
    with open(os.path.join(DIR, name), encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]

def canon(html):
    if html is None:
        return ""
    h = html.replace('class="newpage"', '').replace('<br />', '<br>')
    return re.sub(r'\s+', '', h)

def main():
    ref = {r["id"]: r.get("output", r.get("error", "")) for r in load(REF_FILE)}
    ftml = {r["id"]: r.get("html", str(r.get("errors"))) for r in load("ftml-probe-dump.jsonl")}
    caps = json.load(open(os.path.join(DIR, "captures.json"), encoding="utf-8"))
    extra_caps = json.load(open(os.path.join(DIR, "captures-extra.json"), encoding="utf-8"))
    caps.update(extra_caps)
    ref.update({r["id"]: r.get("output", r.get("error", ""))
                for r in load("ref-probe-extra-render-after.jsonl")})
    print(f"reference file: {REF_FILE}")
    counts = {"all3": 0, "ref_live": 0, "ftml_live": 0, "all_diff": 0}
    for cid, cap in caps.items():
        r, f, l = ref.get(cid, "<missing>"), ftml.get(cid, "<missing>"), cap.get("html", "<missing>")
        rc, fc, lc = canon(r), canon(f), canon(l)
        if rc == fc == lc:
            tag, key = "ALL3", "all3"
        elif rc == lc:
            tag, key = "REF+LIVE", "ref_live"
        elif fc == lc:
            tag, key = "FTML+LIVE", "ftml_live"
        else:
            tag, key = "ALL-DIFF", "all_diff"
        counts[key] += 1
        print(f"[{tag}] {cid}")
        print(f"  src : {cap['source']!r}")
        print(f"  REF : {r!r}")
        print(f"  FTML: {f!r}")
        print(f"  LIVE: {l!r}")
    print(f"SUMMARY {counts}  total={len(caps)}")

if __name__ == "__main__":
    main()
