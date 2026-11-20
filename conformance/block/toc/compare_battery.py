#!/usr/bin/env python3
"""Compare the three sides of the R2-block Toc battery on the TOC-owned surface.

Reads ref-render-<tag>.jsonl, ref-tokens-<tag>.jsonl, ftml-dump.jsonl and an
optional live-capture file, and reports per-case agreement on (a) the TOC box
chrome and (b) the ordered TOC entry signature (margin, href, text). Frame
whitespace between tags and before '>' is canonicalized away because Tighten /
purifyHtml (later rules) owns it; case and entity bytes are NOT normalized, so
the fold/unfold labels and attribute surfaces remain visible.
"""
import json
import re
import sys

BASE = "/home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh-r2block/conformance-refphp/block/toc"

ENTRY = re.compile(r'<div style="margin-left: (\d+)em;"><a href="([^"]*)">(.*?)</a></div>')


def canon(s):
    s = re.sub(r'>\s+<', '><', s)
    s = re.sub(r'\s+>', '>', s)
    return s.strip()


def toc_box(html):
    """Return the first <div id="toc"...> ... box, balanced by div depth."""
    s = canon(html)
    i = s.find('<div id="toc"')
    if i < 0:
        return ""
    depth = 0
    j = i
    while j < len(s):
        o = s.find('<div', j)
        c = s.find('</div>', j)
        if c < 0:
            break
        if o >= 0 and o < c:
            depth += 1
            j = o + 4
        else:
            depth -= 1
            j = c + 6
            if depth == 0:
                return s[i:j]
    return s[i:]


def entries(html):
    return [(m.group(1), m.group(2), m.group(3)) for m in ENTRY.finditer(canon(html))]


def chrome(box):
    return box.split('<div id="toc-list">')[0] if '<div id="toc-list">' in box else box


def load(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        out[r["id"]] = r
    return out


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "before"
    ref = load(f"{BASE}/ref-render-{tag}.jsonl")
    ftml = load(f"{BASE}/ftml-dump.jsonl")
    ids = [json.loads(l)["id"] for l in open(f"{BASE}/battery.jsonl", encoding="utf-8") if l.strip()]
    eb = cb = both = 0
    ediff, cdiff = [], []
    for cid in ids:
        rh = ref[cid].get("output", "")
        fh = ftml[cid].get("html", "")
        re_, fe_ = entries(rh), entries(fh)
        rb, fb = toc_box(rh), toc_box(fh)
        rc, fc = chrome(rb), chrome(fb)
        if re_ == fe_:
            eb += 1
        else:
            ediff.append((cid, re_, fe_))
        if rc == fc:
            cb += 1
        else:
            cdiff.append((cid, rc, fc))
        if re_ == fe_ and rc == fc:
            both += 1
    print(f"tag={tag} cases={len(ids)} entries_agree={eb} chrome_agree={cb} both_agree={both}")
    print("--- entry signature disagreements ---")
    for cid, re_, fe_ in ediff:
        print(f"{cid}\n  ref :{re_}\n  ftml:{fe_}")
    print("--- chrome disagreements ---")
    for cid, rc, fc in cdiff:
        print(f"{cid}\n  ref :{rc}\n  ftml:{fc}")


if __name__ == "__main__":
    main()
