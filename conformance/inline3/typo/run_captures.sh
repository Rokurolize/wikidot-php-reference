#!/usr/bin/env bash
# Chunked, retrying live capture. Every attempt's stdout+stderr is kept.
set -u
PY=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-python
PROBE=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe
for chunk in capture-map-*.json; do
  n=${chunk%.json}
  ok=0
  for attempt in 1 2 3; do
    out=${n}.json
    log=${n}-attempt-${attempt}.log
    "$PY" "$PROBE" capture --site sandbox-for-codex --map "$chunk" --out "$out" > "$log" 2>&1
    rc=$?
    if [ $rc -eq 0 ] && [ -s "$out" ]; then
      echo "$chunk ok on attempt $attempt"
      ok=1
      break
    fi
    echo "$chunk attempt $attempt failed rc=$rc; log retained: $log"
    sleep 5
  done
  if [ $ok -eq 0 ]; then echo "$chunk EXHAUSTED"; fi
done
python3 merge_captures.py
