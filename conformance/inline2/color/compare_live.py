#!/usr/bin/env python3
"""Compare live saved-page captures against reference render and ftml dump.

Usage: compare_live.py CAPTURES.json REF_RENDER.jsonl FTML_DUMP.jsonl OUT.txt
For each case it reports the live page-content HTML, the reference output, and
the ftml dumper output, plus the first color style each side emits. The probe
tool's standard norm() masks per-render noise before comparison.
"""
import importlib.machinery
import importlib.util
import json
import re
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

STYLE = re.compile(r'style="color: ([^"]*)"')

def styles(html):
    if html is None:
        return []
    return STYLE.findall(html)

def norm(html):
    return probe.norm(html) if html is not None else None

lines = ["case | live-valid | live-style | ref-style | ftml-style | live==ref(norm) | live==ftml(norm)"]
both = 0
for cid in sorted(captures, key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
    cap = captures[cid]
    live = cap.get("html")
    r, f = ref.get(cid), dump.get(cid)
    lr = norm(live) == norm(r)
    lf = norm(live) == norm(f)
    both += 1 if lr else 0
    lines.append(
        f"{cid} | {cap.get('valid')} | {styles(live)} | {styles(r)} | {styles(f)} | {lr} | {lf}"
    )
    lines.append(f"  LIVE: {(live or '')[:400]!r}")
with open(out_path, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
print(f"wrote {len(captures)} rows to {out_path}; live==ref(norm) count={both}")
