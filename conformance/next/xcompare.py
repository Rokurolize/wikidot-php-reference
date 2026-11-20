#!/usr/bin/env python3
"""Three-way view of root's cross-rule battery: reference, ftml, live.

Reads xbattery.jsonl, x-ref-render-final.jsonl (or the pre-correction
x-ref-render-pre.jsonl passed as argv[1]), x-ftml-dump-final.jsonl (or
x-ftml-dump-pre.jsonl), and captures-x.json, printing one block per case with
the three shapes, validity flags, and a coarse canonical-equivalence verdict.
The canonicalizer strips frame-level surface (trailing block spacing, <br />
vs <br>, ftml's odate time_/format_ classes versus live's odate widget, the
math image widget versus the harness stub error block) so that a DIFF flags
an in-scope shape rather than a known surface difference.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_jsonl(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return {}
    out = {}
    for line in open(path, encoding="utf-8"):
        if line.strip():
            rec = json.loads(line)
            out[rec["id"]] = rec
    return out


def canon(html):
    if not html:
        return ""
    s = html.replace("<br />", "<br>").strip()
    s = re.sub(r'<span class="odate[^"]*">(.*?)</span>', r'<span class="odate">\1</span>', s)
    s = re.sub(r'<div class="error-block">The equation has not been processed[^<]*</div>',
               '<MATH-SURFACE>', s)
    s = re.sub(r'<span class="equation-number">\(\d+\)</span>\s*<div class="math-equation".*?</div>',
               '<MATH-SURFACE>', s, flags=re.S)
    s = re.sub(r'\s+', ' ', s)
    return s


def main():
    ref_suffix = sys.argv[1] if len(sys.argv) > 1 else "final"
    ftml_suffix = sys.argv[2] if len(sys.argv) > 2 else "final"
    cases = {r["id"]: r for r in
             (json.loads(l) for l in open(os.path.join(HERE, "xbattery.jsonl"), encoding="utf-8"))}
    ref_path = os.path.join(HERE, f"x-ref-render-{ref_suffix}.jsonl")
    ftml_path = os.path.join(HERE, f"x-ftml-dump-{ftml_suffix}.jsonl")
    ref = load_jsonl(os.path.basename(ref_path))
    ftml = load_jsonl(os.path.basename(ftml_path))
    cap_path = os.path.join(HERE, "captures-x.json")
    live = json.load(open(cap_path, encoding="utf-8")) if os.path.exists(cap_path) else {}
    for cid, rec in cases.items():
        r = ref.get(cid, {})
        f = ftml.get(cid, {})
        c = live.get(cid, {})
        rh, fh, lh = r.get("output", r.get("error")), f.get("html"), c.get("html")
        print("=" * 78)
        print(f"CASE {cid}  source={rec['source']!r}  tags={rec.get('tags')}")
        print(f"  REF : {rh!r}"[:400])
        print(f"  FTML: {fh!r} errors={len(f.get('errors', []))}"[:400])
        print(f"  LIVE: valid={c.get('valid')} stable={c.get('stable')} "
              f"src_match={c.get('saved_source_matches')}")
        print(f"        {lh!r}"[:400])
        if rh is not None and fh is not None:
            print(f"  CANON ref-vs-ftml: {'SAME' if canon(rh) == canon(fh) else 'DIFF'}")


if __name__ == "__main__":
    main()
