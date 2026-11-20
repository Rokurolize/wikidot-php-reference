#!/usr/bin/env bash
# Chunked, retrying live capture for the R2-inline3 Tighten campaign.
# A full-map capture hit httpx.ConnectTimeout after 7 pages; the failed log is
# retained as probe-capture-failed.log. Each chunk is captured up to three
# times, and a chunk is accepted only when every record is valid, stable and
# source-matched. Per-attempt logs are retained. Valid chunk records plus the
# three follow-up campaign records are merged into captures.json.
set -u
cd "$(dirname "$0")" || exit 1
PY=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-python
PROBE=/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe
rm -f chunk-accepted-*.json

accept_count=0
for n in 1 2 3 4 5 6 7 8; do
  map="probe-map-chunk-$n.json"
  [ -f "$map" ] || continue
  ok=0
  for attempt in 1 2 3; do
    out="captures-chunk-$n-attempt$attempt.json"
    log="capture-chunk-$n-attempt$attempt.log"
    "$PY" "$PROBE" capture --site sandbox-for-codex --map "$map" --out "$out" --pace 0.6 > "$log" 2>&1
    rc=$?
    if [ $rc -eq 0 ] && [ -f "$out" ]; then
      good=$(python3 - "$out" <<'PYEOF'
import json,sys
try:
    d=json.load(open(sys.argv[1]))
except Exception:
    print('0'); raise SystemExit
print('1' if d and all(v.get('valid') and v.get('stable') and v.get('saved_source_matches') is True for v in d.values()) else '0')
PYEOF
)
      if [ "$good" = "1" ]; then
        cp "$out" "chunk-accepted-$n.json"
        ok=1
        echo "chunk $n accepted on attempt $attempt"
        break
      fi
    fi
    echo "chunk $n attempt $attempt failed rc=$rc; retrying"
  done
  if [ $ok -eq 0 ]; then
    echo "chunk $n NOT accepted after 3 attempts"
  fi
done

python3 - <<'PYEOF'
import json,glob
merged={}
for f in sorted(glob.glob('chunk-accepted-*.json')):
    d=json.load(open(f))
    for k,v in d.items():
        if v.get('valid') and v.get('stable') and v.get('saved_source_matches') is True:
            merged[k]=v
for f in ['captures-extra.json']:
    try:
        d=json.load(open(f))
    except Exception:
        continue
    for k,v in d.items():
        if v.get('valid') and v.get('stable') and v.get('saved_source_matches') is True:
            merged[k]=v
json.dump(merged,open('captures.json','w'),indent=1,ensure_ascii=False)
print('merged valid/stable/source-matched captures:',len(merged))
print('ids:',','.join(sorted(merged)))
PYEOF
