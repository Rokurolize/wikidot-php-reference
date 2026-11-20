#!/usr/bin/env python3
"""Compare the reference HTML/tokens with the ftml dumper HTML per case."""
import json
import re
import sys

BASE = "/home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh-r2notes/conformance-refphp/notes/bibliography/"


def load(path):
    out = {}
    with open(BASE + path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            out[row["id"]] = row
    return out


ref = load("ref-render-before.jsonl")
ftml = load("ftml-dump.jsonl")
order = [json.loads(l)["id"] for l in open(BASE + "battery.jsonl", encoding="utf-8") if l.strip()]


def norm(s):
    """Normalize known frame-level / other-rule differences to expose rule shape."""
    s = s or ""
    # bibcite id random suffix is a Bibcite render matter (owned by bibcite owner)
    s = re.sub(r'id="bibcite-(\d+)-[0-9a-f]+"', r'id="bibcite-\1"', s)
    return s


def shape(s):
    s = norm(s)
    wrappers = s.count('class="bibitems"')
    titles = re.findall(r'<div class="title">(.*?)</div>', s)
    titles = [t for t in titles]
    items = re.findall(r'class="bibitem" id="bibitem-([^"]*)">([0-9]+)\. ?(.*?)</div>', s)
    return wrappers, titles, items


modes = sys.argv[1:] or ["shape"]
for cid in order:
    r = ref.get(cid, {})
    f = ftml.get(cid, {})
    ro = r.get("output") or ("ERROR:" + r.get("error", "") if "error" in r else "")
    fo = f.get("html") or ""
    if "shape" in modes:
        rs, fs = shape(ro), shape(fo)
        flag = "OK " if rs == fs else "DIFF"
        print(f"{flag} {cid:38s} ref(w={rs[0]},t={rs[1]},n={len(rs[2])}) ftml(w={fs[0]},t={fs[1]},n={len(fs[2])})")
        if rs != fs:
            print(f"      ref items={rs[2]}")
            print(f"      ftl items={fs[2]}")
    if "full" in modes:
        print(f"===== {cid} =====")
        print("REF:", norm(ro))
        print("FTL:", norm(fo))
        print()
