#!/usr/bin/env python3
"""Three-way Superscript live-probe comparison: reference, shared ftml dumper
and cached anonymous saved-page captures. `canon` removes the known frame-level
surface (line-break spelling, inter-block newlines) and the Colortext owner's
trailing-semicolon style surface so that a residual is substantive."""
import json
import os
import re

DIR = os.path.dirname(os.path.abspath(__file__))


def canon(html):
    if html is None:
        return ""
    h = html.rstrip()
    h = h.replace("<br />", "<br>").replace("<hr />", "<hr>")
    h = h.replace(' class="newpage"', "")
    h = re.sub(r'(style="color: #[0-9a-fA-F]{3,6});"', r'\1"', h)
    return re.sub(r"\s+", "", h)


def load_jsonl(name):
    with open(os.path.join(DIR, name), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def main():
    ref = {r["id"]: r.get("output", r.get("error", ""))
           for r in load_jsonl("ref-probe-render.jsonl")}
    ftml = {r["id"]: r.get("html", str(r.get("errors")))
            for r in load_jsonl("ftml-probe-dump.jsonl")}
    caps = json.load(open(os.path.join(DIR, "captures.json"), encoding="utf-8"))
    counts = {"all3": 0, "ref_live": 0, "ftml_live": 0, "all_diff": 0}
    invalid = []
    for cid, cap in sorted(caps.items()):
        if not cap.get("valid"):
            invalid.append(cid)
        r, f, l = ref.get(cid, "<MISSING>"), ftml.get(cid, "<MISSING>"), cap.get("html", "<MISSING>")
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
        print(f"[{tag}] {cid}  valid={cap.get('valid')} stable={cap.get('stable')} srcmatch={cap.get('saved_source_matches')}")
        print(f"  src : {cap.get('source')!r}")
        print(f"  REF : {r!r}")
        print(f"  FTML: {f!r}")
        print(f"  LIVE: {l!r}")
    print(f"SUMMARY {counts} total={len(caps)} invalid={invalid}")


if __name__ == "__main__":
    main()
