#!/bin/bash
set -e
cd "$(dirname "$0")"
W=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-python
P=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe
echo "[strong-probe] create start $(date -Is)"
$W $P create --site sandbox-for-codex --prefix muse-probe-r2in2-strong- --from probe-cases.jsonl --out probe-map.json > probe-create.log 2>&1
echo "[strong-probe] create done $(date -Is)"
$W $P capture --site sandbox-for-codex --map probe-map.json --out captures.json > probe-capture.log 2>&1
echo "[strong-probe] capture done $(date -Is)"
