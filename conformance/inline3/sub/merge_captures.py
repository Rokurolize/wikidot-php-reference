#!/usr/bin/env python3
# Merge any chunked wikidot-probe capture files into one cached capture map.
# Only records that are valid, stable across both independent fetches and
# byte-identical to the saved source on readback are kept. A later chunk's
# record wins over an earlier one for the same id. Usage:
#   merge_captures.py <out.json> <chunk1.json> [chunk2.json ...]
import json, sys

out = sys.argv[1]
merged = {}
for path in sys.argv[2:]:
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"skip {path}: {e}")
        continue
    for cid, rec in data.items():
        if rec.get("valid") and rec.get("stable") and rec.get("saved_source_matches"):
            merged[cid] = rec
        else:
            print(f"skip invalid record {cid} from {path}")
json.dump(merged, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"merged {len(merged)} valid/stable/source-matching records into {out}")
