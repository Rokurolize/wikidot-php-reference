#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    cases = [json.loads(l) for l in (HERE / 'cases.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    expected = json.loads((HERE / 'expected.json').read_text(encoding='utf-8'))
    captures = json.loads((HERE / 'captures.json').read_text(encoding='utf-8'))
    payload = ''.join(json.dumps({'id': c['id'], 'source': c['source']}, ensure_ascii=False) + '\n' for c in cases)
    proc = subprocess.run(['php', str(ROOT / 'harness' / 'batch.php'), 'render'], input=payload, text=True, capture_output=True, cwd=ROOT, timeout=300)
    if proc.returncode:
        sys.stderr.write(proc.stderr)
        sys.exit(proc.returncode)
    got = {}
    for line in proc.stdout.splitlines():
        if line.strip():
            row = json.loads(line)
            got[row['id']] = row.get('output', row.get('error', '')).rstrip('\n')

    byte_fail = [cid for cid, want in expected.items() if got.get(cid) != want]
    live_fail = [cid for cid, cap in captures.items() if got.get(cid) != cap['html']]
    print('REFCORR65 pins: %d grouped pins checked' % len(expected))
    print('  expected-render byte pins: %d/%d  failures=%s' % (len(expected) - len(byte_fail), len(expected), byte_fail))
    print('  exact live fidelity:       %d/%d  failures=%s' % (len(captures) - len(live_fail), len(captures), live_fail))
    if byte_fail or live_fail:
        sys.exit(1)


if __name__ == '__main__':
    main()
