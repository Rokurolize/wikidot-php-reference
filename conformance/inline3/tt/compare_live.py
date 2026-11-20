#!/usr/bin/env python3
"""Three-way comparison of live saved-page captures, reference render, ftml dump.

Usage: compare_live.py CAPTURES.json REF_RENDER.jsonl FTML_DUMP.jsonl OUT.txt
Uses the campaign-standard probe.norm() masker for all three sides, so the
harness trailing newlines, attribute ordering, numeric entities and render-noise
ids do not drive the buckets. The raw (unnormalized) strings are also retained
in the report for frame-level diagnosis.
"""
import importlib.machinery
import importlib.util
import json
import sys

loader = importlib.machinery.SourceFileLoader(
    "wikidot_probe", "/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe")
spec = importlib.util.spec_from_loader("wikidot_probe", loader)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

captures_path, ref_path, dump_path, out_path = sys.argv[1:5]

def load_jsonl(path, key):
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            rows[r["id"]] = r.get(key)
    return rows

captures = json.load(open(captures_path, encoding="utf-8"))
ref = load_jsonl(ref_path, "output")
dump = load_jsonl(dump_path, "html")

def norm(html):
    return probe.norm(html) if html is not None else None

lines = ["case | valid | stable | srcmatch | bucket | L==R | L==F | R==F"]
buckets = {}
lr = lf = rf = 0
valid = 0
for cid in sorted(captures, key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
    cap = captures[cid]
    live = cap.get("html")
    r, f = ref.get(cid), dump.get(cid)
    nl, nr, nf = norm(live), norm(r), norm(f)
    L, R, F = nl == nr, nl == nf, nr == nf  # L: live==ref, R: live==ftml, F: ref==ftml
    lr += L; lf += R; rf += F
    valid += 1 if cap.get("valid") else 0
    if L and R:
        bucket = "all-three"
    elif L and not R:
        bucket = "ref+live"
    elif R and not L:
        bucket = "ftml+live"
    elif F and not L:
        bucket = "ref+ftml"
    else:
        bucket = "all-differ"
    buckets[bucket] = buckets.get(bucket, 0) + 1
    lines.append(
        f"{cid} | {cap.get('valid')} | {cap.get('stable')} | "
        f"{cap.get('saved_source_matches')} | {bucket} | {L} | {F} | {R}"
    )
    lines.append(f"  LIVE(raw): {(live or '')[:500]!r}")
    lines.append(f"  REF (raw): {(r or '')[:500]!r}")
    lines.append(f"  FTML(raw): {(f or '')[:500]!r}")
    if not (L and F):
        lines.append(f"  LIVE(norm): {nl!r}")
        lines.append(f"  REF (norm): {nr!r}")
        lines.append(f"  FTML(norm): {nf!r}")
summary = (
    f"total={len(captures)} valid={valid} buckets={buckets} "
    f"pairwise_live_ref={lr} pairwise_live_ftml={lf} pairwise_ref_ftml={rf}"
)
lines.insert(0, summary)
with open(out_path, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
print(summary)
