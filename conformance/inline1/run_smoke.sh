#!/bin/sh
# Root's final smoke run for the R2-inline1 stage: 9-case smoke battery
# through the shared harness's transform.php render on the corrected tree.
# Usage: sh run_smoke.sh <basename>   (e.g. sh run_smoke.sh final)
set -e
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE"
TAG=${1:-final}
: > smoke-$TAG.txt
: > smoke-$TAG.err
for f in ../smoke/*.txt; do
    /usr/bin/php ../../ref-php/harness/transform.php render < "$f" >> smoke-$TAG.txt 2>> smoke-$TAG.err
done
echo "smoke-$TAG.txt $(wc -l < smoke-$TAG.txt) lines; smoke-$TAG.err $(wc -c < smoke-$TAG.err) bytes"
