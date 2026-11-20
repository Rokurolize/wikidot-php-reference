#!/bin/sh
# Root's R2-inline3 cross-rule live probes. Creates and captures saved
# anonymous page views under muse-probe-r2in3-x- from the 108-case
# interaction battery, in chunks so transient failures cannot discard the run.
set -e
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE"
PY=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-python
PROBE=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe

"$PY" "$PROBE" create --site sandbox-for-codex \
    --prefix muse-probe-r2in3-x- --from xbattery.jsonl \
    --out x-probe-map.json --pace 1.0 > probe-x-create.log 2>&1
sh ./capture_x_chunks.sh > capture-x-chunks.log 2>&1
echo "probe create/capture complete"
