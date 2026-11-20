#!/usr/bin/env python3
"""Three-way view of root's cross-rule battery: reference, ftml, live.

Reads xbattery.jsonl, x-ref-render-<suffix>.jsonl, x-ftml-dump-<suffix>.jsonl
and captures-x.json, printing one block per case with the three shapes,
validity flags and a coarse canonical-equivalence verdict. The canonicalizer
strips frame-level surface (trailing block spacing, <br /> versus <br>, ftml's
rendered equation widget versus the harness's deliberate LatexRenderer failure
block, and entity-versus-literal apostrophes) so a DIFF flags an in-scope
shape rather than a known out-of-scope serving or frame difference.
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
    s = html.replace("<br />", "<br>").replace("&#39;", "'").strip()
    s = re.sub(r'<div class="error-block">The equation has not been processed[^<]*</div>',
               '<MATH-SURFACE>', s)
    s = re.sub(r'<span class="equation-number">\(\d+\)</span>\s*'
               r'<div class="math-equation".*?</div>', '<MATH-SURFACE>', s, flags=re.S)
    s = re.sub(r'\s+', ' ', s)
    return re.sub(r'>\s+<', '><', s)


def main():
    ref_suffix = sys.argv[1] if len(sys.argv) > 1 else "final"
    ftml_suffix = sys.argv[2] if len(sys.argv) > 2 else "final"
    cases = {r["id"]: r for r in
             (json.loads(l) for l in open(os.path.join(HERE, "xbattery.jsonl"), encoding="utf-8"))}
    ref = load_jsonl(f"x-ref-render-{ref_suffix}.jsonl")
    ftml = load_jsonl(f"x-ftml-dump-{ftml_suffix}.jsonl")
    cap_path = os.path.join(HERE, "captures-x.json")
    live = json.load(open(cap_path, encoding="utf-8")) if os.path.exists(cap_path) else {}
    for cid, rec in cases.items():
        r, f, c = ref.get(cid, {}), ftml.get(cid, {}), live.get(cid, {})
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
        if lh and rh is not None:
            print(f"  CANON ref-vs-live: {'SAME' if canon(rh) in canon(lh) else 'DIFF'}")


if __name__ == "__main__":
    main()
