#!/bin/sh
# Root-owned 9-case smoke run: the smoke battery through the corrected
# reference tree via ref-php/harness/transform.php render.
# Usage: sh run_smoke.sh pre|final
set -u
cd /home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh-r2table || exit 1
POINT="${1:-final}"
OUT="conformance-refphp/table/smoke-$POINT.txt"
ERR="conformance-refphp/table/smoke-$POINT.err"
: > "$OUT"
: > "$ERR"
for f in conformance-refphp/smoke/*.txt; do
  echo "=== $(basename "$f") ===" >> "$OUT"
  /usr/bin/php ref-php/harness/transform.php render < "$f" >> "$OUT" 2>> "$ERR"
  echo >> "$OUT"
done
echo "smoke cases: $(find conformance-refphp/smoke -name '*.txt' | wc -l)"
echo "wrote $OUT"
