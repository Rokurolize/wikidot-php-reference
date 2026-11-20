#!/usr/bin/env python3
"""Compare a reference-render capture with the shared ftml dumper over the same
JSONL battery, raw and under frame-level normalization. Usage:
  python3 compare_battery.py ref-render-before.jsonl ftml-dump-before.jsonl
"""
import json
import os
import re
import sys

DIR = os.path.dirname(os.path.abspath(__file__))


def canon(html):
    if html is None:
        return ""
    h = html.rstrip()
    h = h.replace("<br />", "<br>").replace("<hr />", "<hr>")
    h = h.replace(' class="newpage"', "")
    h = re.sub(r'(style="color: #[0-9a-fA-F]{3,6});"', r'\1"', h)
    return re.sub(r"\s+", "", h)


def load(name):
    with open(os.path.join(DIR, name), encoding="utf-8") as fh:
        return {r["id"]: r.get("output", r.get("html", r.get("error", "")))
                for r in (json.loads(l) for l in fh if l.strip())}


def main():
    ref, ftml = load(sys.argv[1]), load(sys.argv[2])
    ids = sorted(ref)
    raw = [i for i in ids if str(ref[i]).strip() == str(ftml.get(i, "")).strip()]
    can = [i for i in ids if canon(ref[i]) == canon(ftml.get(i, ""))]
    print(f"raw {len(raw)}/{len(ids)}  canonical {len(can)}/{len(ids)}")
    print("raw residual:", ",".join(i for i in ids if i not in raw))
    print("canonical residual:", ",".join(i for i in ids if i not in can))
    for i in ids:
        if i not in can:
            print(f"--- {i}\n REF : {ref[i]!r}\n FTML: {ftml.get(i)!r}")


if __name__ == "__main__":
    main()
