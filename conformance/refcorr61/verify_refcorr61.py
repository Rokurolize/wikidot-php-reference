#!/usr/bin/env python3
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CENSUS = Path('/home/roku/.local/state/wikijump/muse-bhl/post-agy-finish/lanes/ref-census-jp')
sys.path.insert(0, str(CENSUS))
import census_compare_jp as cc


def cells(html):
    return [p.strip() for p in re.split(r'<hr />\n?', html) if p.strip()]


def mask_module_placeholder(html):
    return re.sub(r'þmodule.*?þ', '', html, flags=re.S)


def main():
    cases = [json.loads(l) for l in (HERE / 'cases.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    expected = json.loads((HERE / 'expected.json').read_text(encoding='utf-8'))
    captures = json.loads((HERE / 'captures.json').read_text(encoding='utf-8'))
    cell_expectations = json.loads((HERE / 'cell-expectations.json').read_text(encoding='utf-8'))
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
    exact_fail = []
    canonical_fail = []
    for cid, wanted in cell_expectations['exact_cells'].items():
        ref_cells = cells(got.get(cid, ''))
        live_cells = cells(captures[cid]['html'])
        for cell in wanted:
            if cell > len(ref_cells) or cell > len(live_cells) or ref_cells[cell - 1] != live_cells[cell - 1]:
                exact_fail.append(f'{cid}:{cell}')
    for cid, wanted in cell_expectations['canonical_cells'].items():
        ref_cells = cells(got.get(cid, ''))
        live_cells = cells(captures[cid]['html'])
        for cell in wanted:
            if cell > len(ref_cells) or cell > len(live_cells) or cc.canonical_census(ref_cells[cell - 1]) != cc.canonical_census(live_cells[cell - 1]):
                canonical_fail.append(f'{cid}:{cell}')
    masked_fail = []
    for cid, wanted in cell_expectations['module_placeholder_masked_canonical_cells'].items():
        ref_cells = cells(got.get(cid, ''))
        live_cells = cells(captures[cid]['html'])
        for cell in wanted:
            if cell > len(ref_cells) or cell > len(live_cells) or cc.canonical_census(mask_module_placeholder(ref_cells[cell - 1])) != cc.canonical_census(live_cells[cell - 1]):
                masked_fail.append(f'{cid}:{cell}')

    exact_total = sum(len(v) for v in cell_expectations['exact_cells'].values())
    canonical_total = sum(len(v) for v in cell_expectations['canonical_cells'].values())
    masked_total = sum(len(v) for v in cell_expectations['module_placeholder_masked_canonical_cells'].values())
    print('REFCORR61 pins: %d grouped pins checked' % len(expected))
    print('  expected-render byte pins: %d/%d  failures=%s' % (len(expected) - len(byte_fail), len(expected), byte_fail))
    print('  exact live-cell fidelity:    %d/%d  failures=%s' % (exact_total - len(exact_fail), exact_total, exact_fail))
    print('  canonical live-cell fidelity:%d/%d  failures=%s' % (canonical_total - len(canonical_fail), canonical_total, canonical_fail))
    print('  masked module-cell fidelity: %d/%d  failures=%s' % (masked_total - len(masked_fail), masked_total, masked_fail))
    if byte_fail or exact_fail or canonical_fail or masked_fail:
        sys.exit(1)


if __name__ == '__main__':
    main()
