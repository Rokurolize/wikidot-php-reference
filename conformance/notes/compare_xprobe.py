#!/usr/bin/env python3
"""Three-way comparison of root's R2-notes cross-rule interaction probes.

Compares the family-shape signature (footnote numbering and collected items,
footnoteblock presence/title, bibliography entry numbering and order, bibcite
targets and undefined-label errors) across the reference render, the shared
ftml dumper and the cached live saved-page HTML. Whole-string canonical
agreement under frame-surface normalization is reported alongside it.
"""
import json
import re

REF = "conformance-refphp/notes/x-ref-render-final-probe.jsonl"
FTM = "conformance-refphp/notes/x-ftml-dump-final-probe.jsonl"
LIVE = "conformance-refphp/notes/captures-x.json"
OUT = "conformance-refphp/notes/x-probe-compare.txt"

def load(path, key):
    out = {}
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        out[rec["id"]] = rec.get(key, rec.get("error", ""))
    return out

def sig(html):
    h = html.replace("&#39;", "'")
    return {
        "fnref": re.findall(r'id="footnoteref-(\d+)"', h),
        "fnitem": re.findall(r'id="footnote-(\d+)"', h),
        "fnfooter": len(re.findall(r'class="footnotes-footer"', h)),
        "fntitle": re.findall(r'<div class="title">(.*?)</div>', h),
        "bibitem": re.findall(r'id="bibitem-(\d+)"', h),
        "bibcite": re.findall(r'class="bibcite" id="bibcite-(\d+)', h),
        "biberror": [m.group(1) for m in re.finditer(r'Bibliography item <em>(.*?)</em> not found', h)],
        "literal_fn": h.count("[[footnote]]"),
        "literal_bib": h.count("[[bibliography]]"),
        "literal_block": h.count("[[footnoteblock]]"),
    }

def canon(html):
    h = html.replace("&#39;", "'").replace("<br />", "<br>")
    h = re.sub(r'id="bibcite-(\d+)-[0-9a-f]+a"', r'id="bibcite-\1"', h)
    h = re.sub(r'>\s+<', '><', h)
    h = re.sub(r'<div >', '<div>', h)
    return h.strip()

ref = load(REF, "output")
ftm = load(FTM, "html")
live_all = json.load(open(LIVE, encoding="utf-8"))

rows = []
counts = {"all3": 0, "ref_live": 0, "ftm_live": 0, "ref_ftm": 0, "all_disagree": 0}
for cid in ref:
    if cid not in ftm or cid not in live_all:
        continue
    lv = live_all[cid]
    if not lv.get("valid"):
        continue
    sr, sf, sl = sig(ref[cid]), sig(ftm[cid]), sig(lv["html"])
    agree_rf = sr == sf
    agree_rl = sr == sl
    agree_fl = sf == sl
    if agree_rf and agree_rl and agree_fl:
        tag = "ALL3"
        counts["all3"] += 1
    elif agree_rl and not agree_fl:
        tag = "REF+LIVE"
        counts["ref_live"] += 1
    elif agree_fl and not agree_rl:
        tag = "FTM+LIVE"
        counts["ftm_live"] += 1
    elif agree_rf and not agree_rl:
        tag = "REF+FTM"
        counts["ref_ftm"] += 1
    else:
        tag = "ALL-DISAGREE"
        counts["all_disagree"] += 1
    cr, cf, cl = canon(ref[cid]), canon(ftm[cid]), canon(lv["html"])
    rows.append((cid, tag, sr, sf, sl, cr == cf, cr == cl, cf == cl))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("R2-notes root cross-rule interaction: three-way family-shape comparison\n")
    f.write(f"valid probes: {len(rows)}; counts: {counts}\n\n")
    for cid, tag, sr, sf, sl, crf, crl, cfl in rows:
        f.write(f"{cid:28s} {tag:14s} canon(ref==ftml)={crf} canon(ref==live)={crl} canon(ftml==live)={cfl}\n")
        if tag != "ALL3":
            f.write(f"  ref : {sr}\n  ftml: {sf}\n  live: {sl}\n")
print(f"wrote {OUT}: {len(rows)} valid probes, {counts}")
