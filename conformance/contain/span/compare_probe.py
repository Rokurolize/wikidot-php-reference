#!/usr/bin/env python3
"""Three-way comparison for the R2-contain Span rule.

Compares the span signature (each <span> open tag with its attributes and its
inner text) across the reference render, the shared ftml dumper, and cached
live saved-page HTML; whole-string canonical agreement is reported alongside.
Counter-bearing collapsible/tabview ids are normalized per root's harness
audit (conformance-refphp/contain/audit/audit-findings.md). Known frame-level
surface (newline padding, <br /> spelling, <div > spacing, live ad/footer
fragments) is stripped by canon() and never scored as a Span correction. The
HTML attribute-order difference between ftml (alphabetical) and live (id
first, then source order) is deliberately left visible in the signature so
it is recorded as a frame-level later-rule surface rather than silently
normalized away.
"""
import json
import os
import re

BASE = "conformance-refphp/contain/span/"
FILES = {
    "battery": {
        "ref_pre": "ref-render-pre.jsonl",
        "ref_final": "ref-render-final.jsonl",
        "ftml": "ftml-dump-pre.jsonl",
        "live": None,
    },
    "probe": {
        "ref_pre": "ref-render-probe-pre.jsonl",
        "ref_final": "ref-render-probe-final.jsonl",
        "ftml": "ftml-dump-probe.jsonl",
        "live": "captures.json",
    },
}

def load_jsonl(path, key):
    out = {}
    try:
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            rec = json.loads(line)
            out[rec["id"]] = rec.get(key, rec.get("error", ""))
    except FileNotFoundError:
        pass
    return out

def norm_counters(h):
    h = re.sub(r'collapsible-block-\d+-', 'collapsible-block-N-', h)
    h = re.sub(r'tabview-\d+', 'tabview-N', h)
    h = re.sub(r'tab-\d+', 'tab-N', h)
    return h

def canon(h):
    h = h.replace("&#39;", "'").replace("<br />", "<br>")
    h = norm_counters(h)
    h = re.sub(r'>\s+<', '><', h)
    h = h.replace("<div >", "<div>")
    h = re.sub(r'<script\b.*?</script>', '', h, flags=re.S)
    h = re.sub(r'<style\b.*?</style>', '', h, flags=re.S)
    return h.strip()

def span_sig(h):
    h = canon(h)
    sig = []
    for m in re.finditer(r'<span\b([^>]*)>(.*?)</span>', h, re.S):
        attrs = sorted(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
        text = re.sub(r'<[^>]+>', '', m.group(2))
        sig.append((tuple(attrs), text))
    return sig

def compare(name, spec, out):
    ref_pre = load_jsonl(BASE + spec["ref_pre"], "output")
    ref_final = load_jsonl(BASE + spec["ref_final"], "output")
    ftm = load_jsonl(BASE + spec["ftml"], "html")
    live = {}
    if spec["live"]:
        try:
            live.update(json.load(open(BASE + spec["live"], encoding="utf-8")))
        except FileNotFoundError:
            pass
    refsrc = ref_final or ref_pre
    label = "final" if ref_final else "pre"
    out.append("== %s (%s reference) ==" % (name, label))
    if not live:
        cnt = {"ref_ftml_agree": 0, "disagree": 0}
        for cid in refsrc:
            if cid not in ftm:
                continue
            if canon(refsrc[cid]) == canon(ftm[cid]):
                cnt["ref_ftml_agree"] += 1
            else:
                cnt["disagree"] += 1
                out.append("  DIFF %s" % cid)
                out.append("    ref : %s" % canon(refsrc[cid])[:200])
                out.append("    ftml: %s" % canon(ftm[cid])[:200])
        out.append("  counts: " + json.dumps(cnt))
        return
    counts = {"all3": 0, "ref_live": 0, "ftm_live": 0, "ref_ftm": 0, "all_disagree": 0}
    whole = {"ref_ftml": 0, "ref_live": 0, "ftml_live": 0}
    rows = []
    for cid in refsrc:
        if cid not in ftm or cid not in live:
            continue
        lv = live[cid]
        if not lv.get("valid"):
            continue
        sr, sf, sl = span_sig(refsrc[cid]), span_sig(ftm[cid]), span_sig(norm_counters(lv["html"]))
        arf, arl, afl = sr == sf, sr == sl, sf == sl
        if arf and arl and afl:
            tag = "ALL3"; counts["all3"] += 1
        elif arl and not afl:
            tag = "REF+LIVE"; counts["ref_live"] += 1
        elif afl and not arl:
            tag = "FTM+LIVE"; counts["ftm_live"] += 1
        elif arf and not arl:
            tag = "REF+FTM"; counts["ref_ftm"] += 1
        else:
            tag = "ALL-DISAGREE"; counts["all_disagree"] += 1
        cr, cf, cl = canon(refsrc[cid]), canon(ftm[cid]), canon(lv["html"])
        whole["ref_ftml"] += cr == cf
        whole["ref_live"] += cr == cl
        whole["ftml_live"] += cf == cl
        rows.append((cid, tag, sr, sf, sl))
    out.append("  signature counts: " + json.dumps(counts))
    out.append("  whole-string canonical: " + json.dumps(whole))
    for cid, tag, sr, sf, sl in rows:
        out.append("  %s %s" % (cid, tag))
        if not (sr == sf == sl):
            out.append("     ref : %r" % (sr,))
            out.append("     ftml: %r" % (sf,))
            out.append("     live: %r" % (sl,))

def main():
    out = ["R2-contain Span three-way comparison",
           "ftml HEAD a61ae005d9e837171a3d2b91cf8fc2df7a3d8ae8 (shared dumper)", ""]
    compare("battery", FILES["battery"], out)
    out.append("")
    compare("probe", FILES["probe"], out)
    text = "\n".join(out) + "\n"
    open(BASE + "comparison.txt", "w", encoding="utf-8").write(text)
    print(text[:12000])

if __name__ == "__main__":
    main()
