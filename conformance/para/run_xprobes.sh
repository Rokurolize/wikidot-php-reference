#!/bin/sh
# Root's R2-para cross-rule live probes. Creates and captures saved anonymous
# page views under muse-probe-r2para-x-. Run from anywhere; paths are absolute.
set -e
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE"
PY=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-python
PROBE=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe

python3 - <<'PY'
import json
rows = [json.loads(l) for l in open('xbattery.jsonl', encoding='utf-8') if l.strip()]
with open('x-probe-cases.jsonl', 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps({'id': r['id'], 'source': r['source']}, ensure_ascii=False) + '\n')
PY

"$PY" "$PROBE" create --site sandbox-for-codex \
    --prefix muse-probe-r2para-x- --from x-probe-cases.jsonl \
    --out x-probe-map.json --pace 1.0 > probe-x-create.log 2>&1
"$PY" "$PROBE" capture --site sandbox-for-codex \
    --map x-probe-map.json --out captures-x.json --pace 1.0 \
    > probe-x-capture.log 2>&1
echo "probe create/capture complete"
