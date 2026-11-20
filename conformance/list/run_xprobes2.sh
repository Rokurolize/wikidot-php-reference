#!/bin/sh
# Root's R2-list cross-rule live probes, phase 2. The first create run stopped
# at x30 because Wikidot strips trailing whitespace on save, so the bare-marker
# and trailing-space cases are re-authored here as their saved-page-normalized
# forms (x30n ... x36n, matching xbattery2.jsonl). Phase 1 pages x01-x29 are
# captured separately in captures-x.json. Prefix stays muse-probe-r2list-x-.
set -e
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE"
PY=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-python
PROBE=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe

"$PY" "$PROBE" create --site sandbox-for-codex \
    --prefix muse-probe-r2list-x- --from x-probe-cases2.jsonl \
    --out x-probe-map2.json --pace 1.0 > probe-x2-create.log 2>&1
"$PY" "$PROBE" capture --site sandbox-for-codex \
    --map x-probe-map2.json --out captures-x2.json --pace 1.0 \
    > probe-x2-capture.log 2>&1
echo "phase-2 probe create/capture complete"
