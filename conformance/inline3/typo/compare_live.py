#!/usr/bin/env python3
"""Three-way comparison of live probe captures, reference render and ftml dump.

Usage: python3 compare_live.py [ref-render-after.jsonl]
Uses compare.canon so entity spellings and frame surface are normalized away;
a residual is a substantive Stage-1 or cross-rule disagreement. Also reports
capture validity, stability and saved-source verification separately.
"""
import json
import os
import sys
from compare import canon, load

DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    reffile = sys.argv[1] if len(sys.argv) > 1 else "ref-render-after.jsonl"
    ref = load(reffile)
    ft = load("ftml-dump.jsonl")
    cap = json.load(open(os.path.join(DIR, "captures.json"), encoding="utf-8"))
    valid = [i for i, r in cap.items() if r.get("valid") and r.get("stable")
             and r.get("saved_source_matches")]
    invalid = [i for i, r in cap.items() if i not in valid]
    print(f"captures {len(cap)} valid {len(valid)} invalid/unstable/source-mismatch {len(invalid)}: {','.join(invalid)}")
    agree_all = [i for i in valid if canon(ref[i]) == canon(ft[i]) == canon(cap[i]["html"])]
    ref_live = [i for i in valid if canon(ref[i]) == canon(cap[i]["html"])]
    ft_live = [i for i in valid if canon(ft[i]) == canon(cap[i]["html"])]
    print(f"valid {len(valid)}  all3 {len(agree_all)}  ref==live {len(ref_live)}  ftml==live {len(ft_live)}")
    print("ref!=live:", ",".join(i for i in valid if i not in ref_live))
    print("ftml!=live:", ",".join(i for i in valid if i not in ft_live))
    for i in valid:
        if i not in ref_live or i not in ft_live:
            print(f"--- {i}  [{cap[i]['fullname']}]")
            print(" LIVE:", repr(cap[i]["html"]))
            print(" REF :", repr(ref[i]))
            print(" FTML:", repr(ft[i]))


if __name__ == "__main__":
    main()
