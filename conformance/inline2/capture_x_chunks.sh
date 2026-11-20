#!/bin/sh
# Root-owned capture of the R2-inline2 cross-rule live probes in small chunks
# so a transient ConnectTimeout cannot discard the whole run; successful
# chunks are merged into captures-x.json (only valid, stable, source-matched).
set -u
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE" || exit 1
W=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-python
P=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe
D=.

python3 - <<'PY'
import json, os
d = "."
m = json.load(open(d + "/x-probe-map.json", encoding="utf-8"))
items = list(m.items())
for i in range(0, len(items), 9):
    chunk = dict(items[i:i+9])
    with open(f"{d}/x-probe-map-chunk-{i//9+1}.json", "w", encoding="utf-8") as f:
        json.dump(chunk, f, indent=1, ensure_ascii=False)
print("wrote", (len(items) + 8) // 9, "capture chunks")
PY

for c in $D/x-probe-map-chunk-*.json; do
  n=$(basename "$c" .json)
  for attempt in 1 2 3; do
    if $W $P capture --site sandbox-for-codex --map "$c" --out "$D/captures-$n.json" --pace 1.0 > "$D/capture-$n.log" 2>&1; then
      echo "$n attempt $attempt OK"
      break
    fi
    echo "$n attempt $attempt failed; retrying"
    sleep 5
  done
done

python3 - <<'PY'
import glob, json
d = "."
merged = {}
for p in sorted(glob.glob(d + "/captures-x-probe-map-chunk-*.json")):
    try:
        data = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        print("skip", p, e)
        continue
    for k, v in data.items():
        if v.get("valid") and v.get("stable") and v.get("saved_source_matches"):
            merged[k] = v
        else:
            print("invalid", k, "valid=", v.get("valid"), "stable=", v.get("stable"), "source=", v.get("saved_source_matches"))
with open(d + "/captures-x.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, indent=1, ensure_ascii=False)
print("merged", len(merged), "valid captures into captures-x.json")
PY
