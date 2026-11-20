#!/bin/sh
# Root-owned final smoke run: the 9-case smoke battery through the corrected
# reference tree via ref-php/harness/transform.php render. Run from the worktree
# root after all three rule sections have landed.
set -u
cd /home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh-r2mod || exit 1
OUT=conformance-refphp/module/smoke-final.txt
: > "$OUT"
for f in conformance-refphp/smoke/*.txt; do
  echo "=== $(basename "$f") ===" >> "$OUT"
  /usr/bin/php ref-php/harness/transform.php render < "$f" >> "$OUT" 2>> conformance-refphp/module/smoke-final.err
  echo >> "$OUT"
done
echo "smoke cases: $(find conformance-refphp/smoke -name '*.txt' | wc -l)"
echo "wrote $OUT"
