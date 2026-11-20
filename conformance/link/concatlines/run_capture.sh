#!/usr/bin/env bash
# Capture the live probes in small chunks so a transient Wikidot 503 only
# costs one chunk, and retry each chunk up to four times. The bundled
# wikidot-probe CLI is used unchanged; only its --map input is sliced.
set -u
cd "$(dirname "$0")"
WRAP=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-python
PROBE=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe
python3 - <<'PY'
import json
m = json.load(open('probe-map.json', encoding='utf-8'))
ids = list(m)
for n, i in enumerate(range(0, len(ids), 7), 1):
    part = {k: m[k] for k in ids[i:i+7]}
    with open('map-part%d.json' % n, 'w', encoding='utf-8') as f:
        json.dump(part, f, ensure_ascii=False)
print('chunks', (len(ids) + 6) // 7, 'of', len(ids))
PY
for n in 1 2 3 4 5; do
  [ -f "map-part$n.json" ] || continue
  for attempt in 1 2 3 4; do
    echo "chunk $n attempt $attempt $(date -Is)" >> probe-capture-chunks.log
    if $WRAP "$PROBE" capture --site sandbox-for-codex --map "map-part$n.json" --out "captures-part$n.json" --pace 1.0 >> probe-capture-chunks.log 2>&1; then
      echo "chunk $n OK $(date -Is)" >> probe-capture-chunks.log
      break
    fi
    sleep 8
  done
done
python3 - <<'PY'
import glob, json
merged = {}
for p in sorted(glob.glob('captures-part*.json')):
    merged.update(json.load(open(p, encoding='utf-8')))
with open('captures.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
    f.write('\n')
print('merged', len(merged))
print('valid', sum(1 for v in merged.values() if v.get('valid')))
PY
