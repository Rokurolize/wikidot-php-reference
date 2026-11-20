#!/usr/bin/env python3
"""Compare reference and ftml outputs over the Bibitem battery."""
import json
import re
import sys

suffix = sys.argv[1] if len(sys.argv) > 1 else "before"


def load(p):
    return {r["id"]: r for r in (json.loads(l) for l in open(p, encoding="utf-8"))}


ref = load(f"ref-render-{suffix}.jsonl")
ft = load("ftml-dump.jsonl")
toks = load(f"ref-tokens-{suffix}.jsonl")


def shape(html):
    """Bibitem-family shape: bibitem divs, bibcite anchors, error spans, literal leftovers."""
    h = html.replace("\n", " ")
    divs = re.findall(r'<div class="bibitem"[^>]*>.*?</div>', h)
    cites = re.findall(r'<a href="javascript:;"[^>]*class="bibcite"[^>]*>.*?</a>', h)
    errs = re.findall(r'<span class="error-inline">.*?</span>', h)
    return divs + cites + errs


def bibitems_only(html):
    h = html.replace("\n", " ")
    return re.findall(r'<div class="bibitem"[^>]*>.*?</div>', h)


def bitokens(t):
    out = json.loads(t) if isinstance(t, str) else t
    if isinstance(out, dict):
        out = [out[k] for k in sorted(out, key=lambda x: int(x))]
    return [v for v in out if v[0] == "Bibitem"]


raw_eq = shape_eq = bi_eq = tok_eq = 0
rows = []
for cid in sorted(ref):
    r = ref[cid].get("output", ref[cid].get("error", ""))
    f = ft[cid].get("html", json.dumps(ft[cid].get("errors")))
    t = toks[cid].get("output", toks[cid].get("error", ""))
    re_ok = r == f
    sh_ok = shape(r) == shape(f)
    bi_ok = bibitems_only(r) == bibitems_only(f)
    tk_ok = bitokens(t) == bitokens(load(f"ref-tokens-before.jsonl")[cid].get("output", ""))
    raw_eq += re_ok
    shape_eq += sh_ok
    bi_eq += bi_ok
    tok_eq += tk_ok
    rows.append((cid, re_ok, sh_ok, bi_ok, bitokens(t)))

print(f"=== {suffix} ===")
print(f"raw whole-string agreement: {raw_eq}/{len(ref)}")
print(f"bibitem-family shape agreement: {shape_eq}/{len(ref)}")
print(f"bibitem div agreement: {bi_eq}/{len(ref)}")
print(f"Bibitem tokens vs before: {tok_eq}/{len(ref)}")
print("--- shape disagreements ---")
for cid, re_ok, sh_ok, bi_ok, bt in rows:
    if not sh_ok:
        print(f"  {cid}: raw={re_ok} bibitemdiv={bi_ok} tokens={bt}")
        print("    REF:", shape(ref[cid].get("output", "")))
        print("    FT :", shape(ft[cid].get("html", "")))
print("--- bibitem-div disagreements ---")
for cid, re_ok, sh_ok, bi_ok, bt in rows:
    if not bi_ok:
        print(f"  {cid}: REF={bibitems_only(ref[cid].get('output',''))}")
        print(f"        FT ={bibitems_only(ft[cid].get('html',''))}")
