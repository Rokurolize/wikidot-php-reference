#!/usr/bin/env python3
# Three-way comparison for the R2-INLINE3 Subscript battery: reference
# render, shared ftml dumper html, and cached live saved-page html.
# Usage: compare_live.py <ref-render.jsonl> <ftml-dump.jsonl> <captures.json> [label]
# Reports both a raw count (only the harness's two trailing newlines removed)
# and a frame-normalized count (line-break spelling and apostrophe entities
# also folded, matching the em-stage comparator), then the three-way buckets
# and per-case detail on the frame-normalized surface.
import json, sys

REF, FTML, CAP = sys.argv[1:4]
LABEL = sys.argv[4] if len(sys.argv) > 4 else ""


def jl(path, key):
    d = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        v = rec.get(key)
        if isinstance(v, str):
            v = v.replace("\\/", "/")
        d[rec["id"]] = v
    return d


ref = jl(REF, "output")
ftml = jl(FTML, "html")
caps = json.load(open(CAP, encoding="utf-8"))


def raw(s):
    if s is None:
        return None
    return s.rstrip("\n")


def frame_norm(s):
    if s is None:
        return None
    s = raw(s)
    s = s.replace("<br />", "<br>").replace("<br/>", "<br>")
    s = s.replace("&#039;", "'").replace("&#39;", "'")
    return s.strip()


ids = sorted(set(ref) | set(ftml) | set(caps))


def live_of(cid):
    c = caps.get(cid)
    if not (c and c.get("valid") and c.get("stable") and c.get("saved_source_matches")):
        return None
    return c.get("html")


def count_agree(norm):
    n = {"ref_live": 0, "ftml_live": 0, "ref_ftml": 0, "all3": 0, "no_live": 0}
    for cid in ids:
        lv = live_of(cid)
        if lv is None:
            n["no_live"] += 1
            continue
        r, f, l = norm(ref.get(cid)), norm(ftml.get(cid)), norm(lv)
        if r == l:
            n["ref_live"] += 1
        if f == l:
            n["ftml_live"] += 1
        if r == f:
            n["ref_ftml"] += 1
        if r == l == f:
            n["all3"] += 1
    return n


print(f"=== {LABEL} agreement counts over {len(ids)} cases ===")
print("RAW (only trailing newlines removed):", count_agree(raw))
print("FRAME-NORMALIZED:", count_agree(frame_norm))

buckets = {"all3": [], "ref+live": [], "ftml+live": [], "ref+ftml": [], "all_disagree": [], "no_live": []}
for cid in ids:
    lv = live_of(cid)
    if lv is None:
        buckets["no_live"].append(cid)
        continue
    r, f, l = frame_norm(ref.get(cid)), frame_norm(ftml.get(cid)), frame_norm(lv)
    if r == l and f == l:
        buckets["all3"].append(cid)
    elif r == l and not f == l:
        buckets["ref+live"].append(cid)
    elif f == l and not r == l:
        buckets["ftml+live"].append(cid)
    elif r == f and not r == l:
        buckets["ref+ftml"].append(cid)
    else:
        buckets["all_disagree"].append(cid)

print("--- frame-normalized three-way buckets ---")
for k, v in buckets.items():
    print(f"{k:14s} {len(v):2d}: {' '.join(v)}")
print("--- per-case detail (frame-normalized) ---")
for cid in ids:
    lv = live_of(cid)
    if lv is None:
        print(f"### {cid}  [no valid/stable/source-matching live capture]")
        c = caps.get(cid)
        if c:
            print("  CAP flags:", {k: c.get(k) for k in ("valid", "stable", "saved_source_matches")})
        continue
    r, f, l = frame_norm(ref.get(cid)), frame_norm(ftml.get(cid)), frame_norm(lv)
    if r == l == f:
        continue
    print(f"### {cid}")
    print(f"  REF : {r!r}")
    print(f"  FTML: {f!r}")
    print(f"  LIVE: {l!r}")
