#!/bin/sh
# Root's R2-inline2 cross-rule live probes. Creates and captures saved
# anonymous page views under muse-probe-r2in2-x-. Run from anywhere; paths
# are absolute so the one-second pacing survives a fresh shell.
set -e
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE"
PY=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-python
PROBE=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe

"$PY" "$PROBE" create --site sandbox-for-codex \
    --prefix muse-probe-r2in2-x- --from x-probe-cases.jsonl \
    --out x-probe-map.json --pace 1.0 > probe-x-create.log 2>&1
# The single whole-map capture died once on a transient ConnectTimeout, so
# capture in chunks with retries; capture_x_chunks.sh merges only captures
# that are valid, stable and saved-source-matching.
sh ./capture_x_chunks.sh > capture-x-chunks.log 2>&1
echo "probe create/capture complete"
