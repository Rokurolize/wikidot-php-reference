#!/usr/bin/env python3
"""Verify the REFCORR41 pins against the current checkout."""
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
CENSUS = Path('/home/roku/.local/state/wikijump/muse-bhl/post-agy-finish/lanes/ref-census-jp')
sys.path.insert(0, str(CENSUS))
import census_compare_jp as ccjp


def canon_verifier(s):
    s = s.replace('&nbsp;', ' ')
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'>\s+<', '><', s)
    return s.strip()


def canon_ref(raw):
    trc, tidy = ccjp.rc.run_tidy(raw)
    ccjp.rc.cleanup_tidy_tmp()
    return ccjp.canonical_census(tidy)


def main():
    cases = [json.loads(l) for l in CASES.read_text(encoding='utf-8').splitlines() if l.strip()]
    expected = json.loads(EXPECTED.read_text(encoding='utf-8'))
    captures = json.loads(CAPTURES.read_text(encoding='utf-8'))
    payload = ''.join(json.dumps({k: c[k] for k in ('id', 'source')}, ensure_ascii=False) + '\n'
                      for c in cases)
    proc = subprocess.run(['php', str(ROOT / 'harness' / 'batch.php'), 'render'],
                          input=payload, text=True, capture_output=True, cwd=ROOT, timeout=300)
    if proc.returncode:
        sys.stderr.write(proc.stderr)
        sys.exit(proc.returncode)
    got = {}
    for line in proc.stdout.splitlines():
        if line.strip():
            row = json.loads(line)
            got[row['id']] = row.get('output', row.get('error', '')).rstrip('\n')

    byte_fail = []
    live_fail = []
    for cid, want in expected.items():
        if got.get(cid) != want:
            byte_fail.append(cid)
    for cid, cap in captures.items():
        ref_c = canon_verifier(canon_ref(got.get(cid, '')))
        live_c = canon_verifier(ccjp.canonical_census(cap['html']))
        if ref_c != live_c:
            live_fail.append(cid)
    print('REFCORR41 pins: %d grouped pins checked' % len(expected))
    print('  expected-render byte pins: %d/%d  failures=%s'
          % (len(expected) - len(byte_fail), len(expected), byte_fail))
    print('  live canonical fidelity:   %d/%d  failures=%s'
          % (len(captures) - len(live_fail), len(captures), live_fail))
    if byte_fail or live_fail:
        sys.exit(1)


if __name__ == '__main__':
    main()
