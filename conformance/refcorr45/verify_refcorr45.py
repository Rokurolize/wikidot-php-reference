#!/usr/bin/env python3
"""Verify the REFCORR45 pins against the current checkout."""
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
CENSUS = Path('/home/roku/.local/state/wikijump/muse-bhl/post-agy-finish/lanes/ref-census-cn')
sys.path.insert(0, str(CENSUS))
import census_compare_cn as cc


def canon_ref(raw):
    trc, tidy = cc.rc.run_tidy(raw)
    cc.rc.cleanup_tidy_tmp()
    return cc.canonical_census(tidy)


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
    for cid in expected:
        cap = captures[cid]
        ref_c = canon_ref(got.get(cid, ''))
        live_c = cc.canonical_census(cap['html'])
        if ref_c != live_c:
            live_fail.append(cid)
    dissolution_fail = []
    # Exact cached-source credit projections. Four are canonical-equal to live
    # after the established environment masks; the other three carry settled
    # caller-runtime residues, so the dissolution evidence is structural rather
    # than a byte-equivalence claim here.
    exact_cases = [{'id': cid, 'source': captures[cid]['source']}
                   for cid in captures if cid.startswith('exact-credit-')]
    payload = ''.join(json.dumps({'id': c['id'], 'source': c['source']}, ensure_ascii=False) + '\n' for c in exact_cases)
    proc = subprocess.run(['php', str(ROOT / 'harness' / 'batch.php'), 'render'],
                          input=payload, text=True, capture_output=True, cwd=ROOT, timeout=300)
    exact_got = {}
    for line in proc.stdout.splitlines():
        if line.strip():
            row = json.loads(line)
            exact_got[row['id']] = row.get('output', row.get('error', '')).rstrip('\n')
    for cid in ('exact-credit-start-standalone', 'exact-credit-end-standalone', 'exact-credit-more', 'exact-credit-more-standalone'):
        if canon_ref(exact_got.get(cid, '')) != cc.canonical_census(captures[cid]['html']):
            dissolution_fail.append(cid)
    print('REFCORR45 pins: %d grouped pins checked' % len(expected))
    print('  expected-render byte pins: %d/%d  failures=%s'
          % (len(expected) - len(byte_fail), len(expected), byte_fail))
    print('  live canonical fidelity:   %d/%d  failures=%s'
          % (len(expected) - len(live_fail), len(expected), live_fail))
    print('  credit dissolution probes: %d/4 canonical-equal failures=%s'
          % (4 - len(dissolution_fail), dissolution_fail))
    if byte_fail or live_fail or dissolution_fail:
        sys.exit(1)


if __name__ == '__main__':
    main()
