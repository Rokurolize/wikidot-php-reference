#!/bin/sh
# Root's second, focused R2-inline3 cross-rule live-probe campaign. The first
# pass created x01..x50 before AMC throttling aborted it; this pass creates 33
# curated unprobed seams (monospace shielding, typography inside markers,
# super/subscript body shapes, Tighten whitespace, pipeline-final composition
# and container boundaries) at a slower pace, then chunk-captures them.
set -e
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE"
PY=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-python
PROBE=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe

"$PY" "$PROBE" create --site sandbox-for-codex \
    --prefix muse-probe-r2in3-x- --from x-probe-cases-2.jsonl \
    --out x-probe-map-2.json --pace 2.0 > probe-x2-create.log 2>&1
python3 - <<'PY'
import json
m = json.load(open('x-probe-map-2.json', encoding='utf-8'))
items = list(m.items())
for i in range(0, len(items), 9):
    with open(f'x-probe-map2-chunk-{i//9+1}.json', 'w', encoding='utf-8') as f:
        json.dump(dict(items[i:i+9]), f, indent=1, ensure_ascii=False)
print('wrote', (len(items)+8)//9, 'second-pass capture chunks')
PY
for c in ./x-probe-map2-chunk-*.json; do
  n=$(basename "$c" .json)
  for attempt in 1 2 3; do
    if "$PY" "$PROBE" capture --site sandbox-for-codex --map "$c" \
         --out "captures-$n.json" --pace 1.0 > "capture-$n.log" 2>&1; then
      echo "$n attempt $attempt OK"
      break
    fi
    echo "$n attempt $attempt failed; retrying"
    sleep 5
  done
done
python3 - <<'PY'
import glob, json
merged = {}
for p in sorted(glob.glob('./captures-x-probe-map2-chunk-*.json')):
    try:
        data = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        print('skip', p, e); continue
    for k, v in data.items():
        if v.get('valid') and v.get('stable') and v.get('saved_source_matches'):
            merged[k] = v
        else:
            print('invalid', k)
json.dump(merged, open('captures-x-2.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('merged', len(merged), 'valid second-pass captures into captures-x-2.json')
PY
echo "second probe campaign complete"
