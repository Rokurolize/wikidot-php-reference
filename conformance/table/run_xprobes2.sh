#!/bin/sh
# Root's R2-table follow-up cross-rule live probes (handed off by the Table
# owner: strong clipping at a cell boundary, [[ul]] and [[div]] inside a
# simple cell, plus nearby variants). Same root prefix muse-probe-r2table-x-.
set -e
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE"
PY=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-python
PROBE=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe

python3 - <<'PY'
import json
rows = [json.loads(l) for l in open('xbattery2.jsonl', encoding='utf-8') if l.strip()]
with open('x2-probe-cases.jsonl', 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps({'id': r['id'], 'source': r['source']}, ensure_ascii=False) + '\n')
PY

"$PY" "$PROBE" create --site sandbox-for-codex \
    --prefix muse-probe-r2table-x- --from x2-probe-cases.jsonl \
    --out x2-probe-map.json --pace 1.0 > probe-x2-create.log 2>&1
"$PY" "$PROBE" capture --site sandbox-for-codex \
    --map x2-probe-map.json --out captures-x2.json --pace 1.0 \
    > probe-x2-capture.log 2>&1
echo "follow-up probe create/capture complete"
