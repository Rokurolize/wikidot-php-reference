#!/usr/bin/env python3
"""Verify the REFCORR35 pins against the current checkout.

Run from anywhere:  python3 conformance/refcorr35/verify_refcorr35.py

Checks, for each of the six labeled shapes captured in the single grouped
sandbox probe:
  1. the batch render equals the retained expected render (byte regression
     pin), and
  2. the batch render canonically agrees with the cached live page fragment
     (live-fidelity pin). canon() is the repository's compare_x.py rule:
     collapse whitespace between tags and strip outer whitespace.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CASES = HERE / 'cases.jsonl'
EXPECTED = HERE / 'expected.json'
CAPTURES = HERE / 'captures.json'


def canon(s):
    return re.sub(r'>\s+<', '><', s.strip())


def main():
    cases = [json.loads(l) for l in CASES.read_text(encoding='utf-8').splitlines() if l.strip()]
    expected = json.loads(EXPECTED.read_text(encoding='utf-8'))
    captures = json.loads(CAPTURES.read_text(encoding='utf-8'))
    payload = ''.join(json.dumps(c, separators=(',', ':')) + '\n' for c in cases)
    proc = subprocess.run(['php', str(ROOT / 'harness' / 'batch.php'), 'render'],
                          input=payload, text=True, capture_output=True, cwd=ROOT, timeout=300)
    if proc.returncode:
        sys.stderr.write(proc.stderr)
        sys.exit(proc.returncode)
    got = {}
    for line in proc.stdout.splitlines():
        if line.strip():
            row = json.loads(line)
            got[row['id']] = row.get('output', '').rstrip('\n')

    byte_fail = []
    live_fail = []
    for cid, want in expected.items():
        if got.get(cid) != want:
            byte_fail.append((cid, want, got.get(cid)))
    for cid, cap in captures.items():
        if canon(got.get(cid, '')) != canon(cap['html']):
            live_fail.append((cid, canon(cap['html']), canon(got.get(cid, ''))))

    print('REFCORR35 pins: %d shapes checked' % len(expected))
    print('  expected-render byte pins: %d/%d  failures=%s'
          % (len(expected) - len(byte_fail), len(expected), [f[0] for f in byte_fail]))
    print('  live canonical fidelity:   %d/%d  failures=%s'
          % (len(captures) - len(live_fail), len(captures), [f[0] for f in live_fail]))
    for cid, want, actual in byte_fail:
        print('BYTE FAIL', cid)
        print('  want:', repr(want))
        print('  got :', repr(actual))
    for cid, want, actual in live_fail:
        print('LIVE FAIL', cid)
        print('  live:', repr(want))
        print('  ref :', repr(actual))
    if byte_fail or live_fail:
        sys.exit(1)


if __name__ == '__main__':
    main()
