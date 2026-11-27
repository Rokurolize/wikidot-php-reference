#!/usr/bin/env python3
"""Verify the REFCORR46 pins against the current checkout."""
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


def mask_html_src(s):
    return re.sub(
        r'(<iframe\b(?:(?!>).)*\bclass="[^"]*html-block-iframe[^"]*"(?:(?!>).)*\bsrc=")[^"]*(")',
        r'\1HTML_BLOCK_SRC\2', s)


def canon_ref(raw):
    trc, tidy = cc.rc.run_tidy(raw)
    cc.rc.cleanup_tidy_tmp()
    return mask_html_src(cc.canonical_census(tidy))


def canon_live(raw):
    return mask_html_src(cc.canonical_census(raw))


def main():
    cases = [json.loads(l) for l in CASES.read_text(encoding='utf-8').splitlines() if l.strip()]
    expected = json.loads(EXPECTED.read_text(encoding='utf-8'))
    captures = json.loads(CAPTURES.read_text(encoding='utf-8'))
    payload = ''.join(json.dumps({'id': c['id'], 'source': c['source']}, ensure_ascii=False) + '\n'
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
    capture_invalid = []
    for cid, want in expected.items():
        if got.get(cid) != want:
            byte_fail.append(cid)
    for cid in expected:
        cap = captures[cid]
        if not (cap.get('valid') and cap.get('stable') and cap.get('saved_source_matches')):
            capture_invalid.append(cid)
        if canon_ref(got.get(cid, '')) != canon_live(cap['html']):
            live_fail.append(cid)
    print('REFCORR46 pins: %d grouped probe pins covering 38 shape cells' % len(expected))
    print('  expected-render byte pins: %d/%d  failures=%s'
          % (len(expected) - len(byte_fail), len(expected), byte_fail))
    print('  live canonical fidelity:   %d/%d  failures=%s'
          % (len(expected) - len(live_fail), len(expected), live_fail))
    print('  capture validity:          %d/%d  failures=%s'
          % (len(expected) - len(capture_invalid), len(expected), capture_invalid))
    if byte_fail or live_fail or capture_invalid:
        sys.exit(1)


if __name__ == '__main__':
    main()
