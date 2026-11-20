#!/usr/bin/env python3
"""Three-way comparison for root's R2-list cross-rule interaction battery.

Usage: python3 compare_x.py pre|final
Compares a family-shape signature (ul/ol/dl/dt/dd structure, list nesting
order, literal unmatched constructs, inline span shapes and visible text)
across the reference render, the shared ftml dumper and cached live saved-page
HTML. Whole-string canonical agreement under known frame-surface
normalization is reported alongside. Random element ids are masked.
"""
import importlib.machinery
import importlib.util
import json
import os
import re
import sys

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
POINT = sys.argv[1] if len(sys.argv) > 1 else "pre"
REF = [OUT_DIR + "/x-ref-render-" + POINT + ".jsonl",
       OUT_DIR + "/x2-ref-render.jsonl" if POINT == "pre" else OUT_DIR + "/x2-ref-render-final.jsonl"]
FTM = [OUT_DIR + "/x-ftml-dump.jsonl", OUT_DIR + "/x2-ftml-dump.jsonl"]
LIVE = [OUT_DIR + "/captures-x.json", OUT_DIR + "/captures-x2.json"]
OUTPUT = OUT_DIR + "/x-compare-" + POINT + ".txt"

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


ref = {}
for path in REF:
    ref.update(load(path, "output"))
ftm = {}
for path in FTM:
    ftm.update(load(path, "html"))
live_all = {}
for path in LIVE:
    try:
        live_all.update(json.load(open(path, encoding="utf-8")))
    except FileNotFoundError:
        pass


def mask(s):
    s = probe.norm(s)
    s = re.sub(r"collapsible-block-[0-9a-fA-F-]+", "collapsible-block-X", s)
    s = re.sub(r"(id=\"[^\"]*?(?:tab|collaps|bibcite|footnote)[^\"]*?\")",
               lambda m: re.sub(r"[0-9a-f]{3,}", "X", m.group(1)), s, flags=re.I)
    return s


def sig(s):
    h = mask(s)
    tags = re.findall(r"<(/?)(ul|ol|dl|li|dt|dd)\b", h)
    spans = []
    for m in re.finditer(r"<span\b([^>]*)>", h):
        a = m.group(1)
        cls = re.search(r"class=\"([^\"]*)\"", a)
        sty = re.search(r"style=\"([^\"]*)\"", a)
        spans.append(("c=" + (cls.group(1) if cls else ""),
                      "s=" + (sty.group(1) if sty else "")))
    return {
        "tags": tags,
        "spans": spans,
        "lit": {k: h.count(k) for k in ("[[div", "[[span", "[[size", "[[collapsible",
                                        "[[tab", "[[iftags", "[[code", "[[footnote",
                                        "[[bibliography", "[[/bibliography") if h.count(k)},
        "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).strip()[:600],
    }


def canon(s):
    h = mask(s)
    h = h.replace("<br />", "<br>").replace("<div >", "<div>")
    h = re.sub(r">\s+<", "><", h)
    return h.strip()


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
    rows.append((cid, tag, cr == cf, cr == cl, cf == cl, sr, sf, sl))

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("R2-list root cross-rule interaction: three-way comparison (" + POINT + ")\n")
    f.write(f"valid probes: {len(rows)}; signature counts: {counts}\n")
    f.write("canon counts: ref==ftml " + str(sum(1 for r in rows if r[2])) +
            ", ref==live " + str(sum(1 for r in rows if r[3])) +
            ", ftml==live " + str(sum(1 for r in rows if r[4])) + "\n\n")
    for cid, tag, crf, crl, cfl, sr, sf, sl in rows:
        f.write(f"{cid:34s} {tag:14s} canon(r=f)={crf} canon(r=l)={crl} canon(f=l)={cfl}\n")
        if tag != "ALL3":
            f.write(f"  ref : {sr}\n  ftml: {sf}\n  live: {sl}\n")
print("wrote", OUTPUT, len(rows), "valid probes", counts)
