#!/usr/bin/env python3
"""Three-way comparison for root's R2-contain cross-rule interaction probes.

Usage: python3 compare_xprobe.py pre|final
Compares a family-shape signature (span/size/color/strike open shapes, div
containers, collapsible blocks, tabview and tab structure, footnote refs and
items, literal unmatched constructs, visible text) across the reference
render, the shared ftml dumper and cached live saved-page HTML at a given
stage point. Whole-string canonical agreement under known frame-surface
normalization is reported alongside it. Random element ids in all three
sides are masked before comparison.
"""
import importlib.machinery
import importlib.util
import json
import re
import sys

OUT_DIR = __import__("os").path.dirname(__import__("os").path.abspath(__file__))
POINT = sys.argv[1] if len(sys.argv) > 1 else "pre"
REF = OUT_DIR + "/x-ref-render-" + POINT + ".jsonl"
FTM = OUT_DIR + "/x-ftml-dump-" + POINT + ".jsonl"
LIVE = [OUT_DIR + "/captures-x.json", OUT_DIR + "/captures-x-tagged.json"]
OUTPUT = OUT_DIR + "/x-probe-compare-" + POINT + ".txt"

loader = importlib.machinery.SourceFileLoader(
    "wikidot_probe", "/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe")
spec = importlib.util.spec_from_loader("wikidot_probe", loader)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

def load(path, key):
    out = {}
    try:
        fh = open(path, encoding="utf-8")
    except FileNotFoundError:
        return out
    for line in fh:
        if not line.strip():
            continue
        rec = json.loads(line)
        out[rec["id"]] = rec.get(key, rec.get("error", ""))
    return out

ref = load(REF, "output")
ftm = load(FTM, "html")
# The five tagged-alpha iftags cases were published as separate live pages;
# their local counterparts were rendered from x-tagged-battery.jsonl, which
# carries the same "-tagged" ids and tags=["alpha"].
ref.update(load(OUT_DIR + "/x-ref-tagged-render-" + POINT + ".jsonl", "output"))
ftm.update(load(OUT_DIR + "/x-ftml-tagged-dump.jsonl", "html"))
live_all = {}
for path in LIVE:
    try:
        live_all.update(json.load(open(path, encoding="utf-8")))
    except FileNotFoundError:
        pass

def mask(s):
    s = probe.norm(s)
    s = re.sub(r"collapsible-block-[0-9a-fA-F-]+", "collapsible-block-X", s)
    s = re.sub(r"(id=\"[^\"]*?(?:tab|collaps)[^\"]*?\")", lambda m: re.sub(r"[0-9a-f]{3,}", "X", m.group(1)), s, flags=re.I)
    return s

def sig(s):
    h = mask(s)
    spans = []
    for m in re.finditer(r"<span\b([^>]*)>", h):
        a = m.group(1)
        cls = re.search(r"class=\"([^\"]*)\"", a)
        sty = re.search(r"style=\"([^\"]*)\"", a)
        spans.append(("c=" + (cls.group(1) if cls else ""),
                      "s=" + (sty.group(1) if sty else "")))
    divs = []
    for m in re.finditer(r"<div\b([^>]*)>", h):
        a = m.group(1)
        cls = re.search(r"class=\"([^\"]*)\"", a)
        divs.append("d=" + (cls.group(1) if cls else ""))
    return {
        "spans": spans,
        "divs": divs,
        "coll": h.count("collapsible-block-X") + h.count("collapsible-block"),
        "coll_show": bool(re.search(r"show block|\+ show|show=show", h)),
        "tabs_nav": h.count("<li"),
        "tabs_body": h.count("wiki-tab-X") + h.count("yui-content"),
        "fnref": re.findall(r"footnoteref-(X|\d+)", h),
        "fnitem": re.findall(r"footnote-(X|\d+)", h),
        "lit": {k: h.count(k) for k in ("[[div", "[[span", "[[size", "[[collapsible",
                                        "[[tab", "[[iftags", "@@", "[[code", "[[footnote") if h.count(k)},
        "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).strip()[:600],
    }

def canon(s):
    h = mask(s)
    h = h.replace("<br />", "<br>").replace("<div >", "<div>")
    h = re.sub(r">\s+<", "><", h)
    return h.strip()

# These two battery cases were authored with tags=["alpha"] but the untagged
# live pages of the same source necessarily have no alpha tag, so comparing
# them untagged is a tag/source mismatch rather than a behavior divergence.
# Their tagged counterparts (x13-...-tagged, x14-...-tagged) are the valid
# comparisons and are retained.
TAG_MISMATCH = {"x13-iftags-active-div", "x14-iftags-suppressed-coll"}

rows = []
counts = {"all3": 0, "ref_live": 0, "ftm_live": 0, "ref_ftm": 0, "all_disagree": 0}
for cid in ref:
    if cid in TAG_MISMATCH:
        continue
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
    rows.append((cid, tag, cr == cf, cr == cl, cf == cl, sr, sf, sl))

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("R2-contain root cross-rule interaction: three-way comparison (" + POINT + ")\n")
    f.write(f"valid probes: {len(rows)}; signature counts: {counts}\n")
    f.write("excluded as tag/source mismatches: x13-iftags-active-div, x14-iftags-suppressed-coll "
            "(authored with tags=['alpha'] but created as untagged live pages; their -tagged counterparts are compared)\n\n")
    f.write("canon counts: ref==ftml " + str(sum(1 for r in rows if r[2])) +
            ", ref==live " + str(sum(1 for r in rows if r[3])) +
            ", ftml==live " + str(sum(1 for r in rows if r[4])) + "\n\n")
    for cid, tag, crf, crl, cfl, sr, sf, sl in rows:
        f.write(f"{cid:34s} {tag:14s} canon(r=f)={crf} canon(r=l)={crl} canon(f=l)={cfl}\n")
        if tag != "ALL3":
            f.write(f"  ref : {sr}\n  ftml: {sf}\n  live: {sl}\n")
print("wrote", OUTPUT, len(rows), "valid probes", counts)
