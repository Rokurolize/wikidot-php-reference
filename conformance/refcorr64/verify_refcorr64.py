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


def mask_module_placeholder(html, replacement=''):
    return re.sub(r'þmodule.*?þ', replacement, html, flags=re.S)


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
    rate_fail = []
    css_fail = []
    multi_live = cells(captures['multi-opaque-anchor']['html'])
    rate_widget = re.search(r'(<div class="page-rate-widget-box">.*?</div>)\s*$', multi_live[7], re.S).group(1)
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
    for cid, wanted in cell_expectations['rate_module_expansion_exact_cells'].items():
        ref_cells = cells(got.get(cid, ''))
        live_cells = cells(captures[cid]['html'])
        for cell in wanted:
            if cell > len(ref_cells) or cell > len(live_cells):
                rate_fail.append(f'{cid}:{cell}')
                continue
            expanded = ref_cells[cell - 1].replace('þmodule "Rate"þ', rate_widget)
            if expanded != live_cells[cell - 1]:
                rate_fail.append(f'{cid}:{cell}')
    for cid, wanted in cell_expectations['css_empty_module_masked_canonical_cells'].items():
        ref_cells = cells(got.get(cid, ''))
        live_cells = cells(captures[cid]['html'])
        for cell in wanted:
            if cell > len(ref_cells) or cell > len(live_cells):
                css_fail.append(f'{cid}:{cell}')
                continue
            masked = mask_module_placeholder(ref_cells[cell - 1])
            if cc.canonical_census(masked) != cc.canonical_census(live_cells[cell - 1]):
                css_fail.append(f'{cid}:{cell}')

    exact_total = sum(len(v) for v in cell_expectations['exact_cells'].values())
    canonical_total = sum(len(v) for v in cell_expectations['canonical_cells'].values())
    rate_total = sum(len(v) for v in cell_expectations['rate_module_expansion_exact_cells'].values())
    css_total = sum(len(v) for v in cell_expectations['css_empty_module_masked_canonical_cells'].values())
    print('REFCORR64 pins: %d grouped pins checked' % len(expected))
    print('  expected-render byte pins: %d/%d  failures=%s' % (len(expected) - len(byte_fail), len(expected), byte_fail))
    print('  exact live-cell fidelity:    %d/%d  failures=%s' % (exact_total - len(exact_fail), exact_total, exact_fail))
    print('  canonical live-cell fidelity:%d/%d  failures=%s' % (canonical_total - len(canonical_fail), canonical_total, canonical_fail))
    print('  rate-expansion live fidelity:%d/%d  failures=%s' % (rate_total - len(rate_fail), rate_total, rate_fail))
    print('  css-empty masked canonical:  %d/%d  failures=%s' % (css_total - len(css_fail), css_total, css_fail))
    if byte_fail or exact_fail or canonical_fail or rate_fail or css_fail:
        sys.exit(1)


if __name__ == '__main__':
    main()
