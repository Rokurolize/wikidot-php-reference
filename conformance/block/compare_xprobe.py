#!/usr/bin/env python3
"""Three-way comparison of root's R2-block cross-rule interaction probes.

Compares the family-shape signature (heading levels and anchor ids, toc item
targets and list count, blockquote container count, collected footnote numbers
and literal unmatched forms) across the reference render, the shared ftml
dumper and the cached live saved-page HTML. Whole-string canonical agreement
under known frame-surface normalization is reported alongside it.
"""
import json
import re

BASE = "conformance-refphp/block/"
REF = BASE + "x-ref-render-final.jsonl"
FTM = BASE + "x-ftml-dump-final.jsonl"
LIVE = BASE + "captures-x.json"
LIVE_TAGGED = BASE + "captures-x-tagged.json"
OUT = BASE + "x-probe-compare.txt"

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
    heads = [(int(m.group(1)), m.group(2), re.sub(r"<[^>]+>", "", m.group(3)))
             for m in re.finditer(r'<h([1-6]) id="(toc\d+)"[^>]*><span>(.*?)</span></h\1>', h, re.S)]
    return {
        "head": heads,
        "toc_links": re.findall(r'href="#(toc\d+)"', h),
        "toc_lists": h.count('id="toc-list"'),
        "bq": h.count("<blockquote"),
        "fnref": re.findall(r'id="footnoteref-(\d+)"', h),
        "fnitem": re.findall(r'id="footnote-(\d+)"', h),
        "lit_toc": h.count("[[toc]]"),
        "lit_bq": h.count("[[blockquote]]"),
    }

def canon(html):
    h = html.replace("&#39;", "'").replace("<br />", "<br>")
    h = h.replace(">fold</a>", ">Fold</a>").replace(">unfold</a>", ">Unfold</a>")
    h = re.sub(r'>\s+<', '><', h)
    h = re.sub(r'<div >', '<div>', h)
    return h.strip()

ref = load(REF, "output")
ftm = load(FTM, "html")
live_all = {}
for p in (LIVE, LIVE_TAGGED):
    try:
        live_all.update(json.load(open(p, encoding="utf-8")))
    except FileNotFoundError:
        pass

rows = []
counts = {"all3": 0, "ref_live": 0, "ftm_live": 0, "ref_ftm": 0, "all_disagree": 0}
for cid in ref:
    if cid not in ftm or cid not in live_all:
        continue
    lv = live_all[cid]
    if not lv.get("valid"):
        continue
    sr, sf, sl = sig(ref[cid]), sig(ftm[cid]), sig(lv["html"])
    agree_rf, agree_rl, agree_fl = sr == sf, sr == sl, sf == sl
    if agree_rf and agree_rl and agree_fl:
        tag = "ALL3"; counts["all3"] += 1
    elif agree_rl and not agree_fl:
        tag = "REF+LIVE"; counts["ref_live"] += 1
    elif agree_fl and not agree_rl:
        tag = "FTM+LIVE"; counts["ftm_live"] += 1
    elif agree_rf and not agree_rl:
        tag = "REF+FTM"; counts["ref_ftm"] += 1
    else:
        tag = "ALL-DISAGREE"; counts["all_disagree"] += 1
    cr, cf, cl = canon(ref[cid]), canon(ftm[cid]), canon(lv["html"])
    rows.append((cid, tag, sr, sf, sl, cr == cf, cr == cl, cf == cl))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("R2-block root cross-rule interaction: three-way family-shape comparison\n")
    f.write(f"valid probes: {len(rows)}; counts: {counts}\n\n")
    for cid, tag, sr, sf, sl, crf, crl, cfl in rows:
        f.write(f"{cid:28s} {tag:14s} canon(ref==ftml)={crf} canon(ref==live)={crl} canon(ftml==live)={cfl}\n")
        if tag != "ALL3":
            f.write(f"  ref : {sr}\n  ftml: {sf}\n  live: {sl}\n")
print(f"wrote {OUT}: {len(rows)} valid probes, {counts}")
