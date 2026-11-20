#!/bin/bash
# Capture the focused Toc live probes in small batches so a transient Wikidot
# 503 loses at most one batch. Each batch is retried up to 5 times.
set -u
cd /home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh-r2block/conformance-refphp/block/toc || exit 1
W=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-python
P=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe
mkdir -p capout
for map in capmap/map*.json; do
    b=$(basename "$map" .json)
    ok=0
    for attempt in 1 2 3 4 5; do
        if $W $P capture --site sandbox-for-codex --map "$map" --out "capout/${b}.json" --pace 2.0 >"capout/${b}.attempt${attempt}.log" 2>&1; then
            echo "$b OK attempt $attempt"
            ok=1
            break
        fi
        echo "$b attempt $attempt failed; retrying"
        sleep 5
    done
    if [ "$ok" = 0 ]; then echo "$b FAILED all attempts"; fi
done
echo "batches done"
