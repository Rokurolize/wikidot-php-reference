#!/bin/bash
# R2-INLINE2 Emphasis: one live probe of the whole battery under the
# rule-owned prefix. Create + double-fetch capture, caching everything so
# it can be reused without another live fetch.
set -u
HERE=/home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh-r2in2/conformance-refphp/inline2/em
SKILL=/home/roku/.agents/skills/wikidot-py-operations
WRAP="$SKILL/scripts/wikidot-python"
PROBE="$SKILL/scripts/wikidot-probe"
PREFIX=muse-probe-r2in2-em-
cd "$HERE" || exit 1

echo "== create $(date -Iseconds) =="
"$WRAP" "$PROBE" create --site sandbox-for-codex --prefix "$PREFIX" \
  --from battery.jsonl --out probe-map.json > probe-create.log 2>&1
echo "create exit=$? $(date -Iseconds)"

echo "== capture $(date -Iseconds) =="
"$WRAP" "$PROBE" capture --site sandbox-for-codex \
  --map probe-map.json --out probe-captures.json > probe-capture.log 2>&1
echo "capture exit=$? $(date -Iseconds)"
echo "== done =="
