#!/usr/bin/env python3
"""Three-way comparison of root's exact probe sources, not the battery forms.

Reads probe-x-cases.jsonl, x-ref-render-probe.jsonl, x-ftml-dump-probe.jsonl and
captures-x.json, printing one block per saved page with the three shapes and a
canonical-equivalence verdict. Canonicalization strips frame-level surface
(trailing spacing, <br /> versus <br>, entity apostrophes, and the stubbed Math
failure surface) so a DIFF points at an in-scope shape.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def load_jsonl(name):
    out = {}
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        if line.strip():
            rec = json.loads(line)
            out[rec["id"]] = rec
    return out


def canon(html):
    if not html:
        return ""
    s = html.replace("<br />", "<br>").replace("&#39;", "'").strip()
    s = re.sub(r'<div class="error-block">The equation has not been processed[^<]*</div>',
               '<MATH-SURFACE>', s)
    s = re.sub(r'<span class="equation-number">\(\d+\)</span>\s*'
               r'<div class="math-equation".*?</div>', '<MATH-SURFACE>', s, flags=re.S)
    s = re.sub(r'\s+', ' ', s)
    return re.sub(r'>\s+<', '><', s)


def main():
    import sys
    suffix = sys.argv[1] if len(sys.argv) > 1 else ""
    case_file = f"probe-x-{suffix}.jsonl" if suffix else "probe-x-cases.jsonl"
    ref_file = f"x-ref-render-{suffix}.jsonl" if suffix else "x-ref-render-probe.jsonl"
    ftml_file = f"x-ftml-dump-{suffix}.jsonl" if suffix else "x-ftml-dump-probe.jsonl"
    cap_file = f"captures-x-{suffix}.json" if suffix else "captures-x.json"
    cases = load_jsonl(case_file)
    ref = load_jsonl(ref_file)
    ftml = load_jsonl(ftml_file)
    cap_path = os.path.join(HERE, cap_file)
    live = json.load(open(cap_path, encoding="utf-8")) if os.path.exists(cap_path) else {}
    verdicts = {"all3": 0, "ref_live": 0, "ftml_live": 0, "all_diff": 0, "no_live": 0}
    for cid, rec in cases.items():
        r, f, c = ref.get(cid, {}), ftml.get(cid, {}), live.get(cid, {})
        rh = r.get("output", r.get("error"))
        fh, lh = f.get("html"), c.get("html")
        print("=" * 78)
        print(f"CASE {cid}  source={rec['source']!r}")
        print(f"  REF : {rh!r}"[:400])
        print(f"  FTML: {fh!r}"[:400])
        print(f"  LIVE: valid={c.get('valid')} stable={c.get('stable')} "
              f"src_match={c.get('saved_source_matches')}")
        print(f"        {lh!r}"[:400])
        if "html" not in c or c.get("valid") is False:
            verdicts["no_live"] += 1
            continue
        cr, cf, cl = canon(rh), canon(fh), canon(lh)
        same_rl, same_rf = cr in cl, cr == cf
        if same_rl and same_rf:
            verdicts["all3"] += 1
            v = "ALL3"
        elif same_rl:
            verdicts["ref_live"] += 1
            v = "REF+LIVE vs FTML"
        elif cf in cl:
            verdicts["ftml_live"] += 1
            v = "FTML+LIVE vs REF"
        else:
            verdicts["all_diff"] += 1
            v = "ALL DIFFER"
        print(f"  VERDICT: {v}")
    print("=" * 78)
    print("VERDICTS:", verdicts)


if __name__ == "__main__":
    main()
