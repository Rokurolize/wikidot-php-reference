#!/usr/bin/env python3
"""Verify the REFCORR70 Module-before-Raw pins against the current checkout."""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = 'þmodule "Rate"þ'
WIDGET_RE = re.compile(r'<div class="page-rate-widget-box">.*?</div>', re.S)


def rate_widget(capture_html):
    widgets = WIDGET_RE.findall(capture_html)
    if not widgets:
        raise RuntimeError('capture has no Rate widget')
    if len(set(widgets)) != 1:
        raise RuntimeError('capture Rate widgets differ')
    return widgets[0]


def substitute_rate_modules(render, widget):
    out = []
    rest = render
    while MARKER in rest:
        before, rest = rest.split(MARKER, 1)
        out.append(before)
        out.append(widget)
    out.append(rest)
    return ''.join(out)


def main():
    cases = [json.loads(l) for l in (HERE / 'cases.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    expected = json.loads((HERE / 'expected.json').read_text(encoding='utf-8'))
    captures = json.loads((HERE / 'captures.json').read_text(encoding='utf-8'))
    payload = ''.join(json.dumps({'id': c['id'], 'source': c['source']}, ensure_ascii=False) + '\n' for c in cases)
    proc = subprocess.run(['php', str(ROOT / 'harness' / 'batch.php'), 'render'], input=payload,
                          text=True, capture_output=True, cwd=ROOT, timeout=300)
    if proc.returncode:
        sys.stderr.write(proc.stderr)
        sys.exit(proc.returncode)
    got = {}
    for line in proc.stdout.splitlines():
        if line.strip():
            row = json.loads(line)
            got[row['id']] = row.get('output', row.get('error', '')).rstrip('\n')

    byte_fail = [cid for cid, want in expected.items() if got.get(cid) != want]
    unstable = [cid for cid, cap in captures.items()
                if not (cap.get('stable') and cap.get('saved_source_matches') and cap.get('valid'))]

    direct_ids = ['emptyraw', 'nonemptyraw', 'code-before', 'code-after', 'module-bodyraw']
    direct_fail = [cid for cid in direct_ids if got.get(cid) != captures[cid]['html']]

    module_ids = ['module-emptyraw', 'module-nonemptyraw']
    module_fail = []
    module_count_fail = []
    for cid in module_ids:
        cap = captures[cid]['html']
        widget = rate_widget(cap)
        if got[cid].count(MARKER) != cap.count('page-rate-widget-box'):
            module_count_fail.append(cid)
        if substitute_rate_modules(got[cid], widget) != cap:
            module_fail.append(cid)

    exact = got.get('exact', '')
    exact_cap = captures['exact']['html']
    exact_structure_fail = []
    if exact.count(MARKER) != exact_cap.count('page-rate-widget-box'):
        exact_structure_fail.append('module-count')
    if '.alt-block' in exact:
        exact_structure_fail.append('unexpected-code-insertion')
    if exact == exact_cap:
        exact_structure_fail.append('residue-unexpectedly-closed')

    print('REFCORR70 pins: %d grouped/exact pins checked' % len(expected))
    print('  capture validity:                %d/%d  failures=%s' % (len(captures) - len(unstable), len(captures), unstable))
    print('  expected-render byte pins:       %d/%d  failures=%s' % (len(expected) - len(byte_fail), len(expected), byte_fail))
    print('  direct exact live fidelity:      %d/%d  failures=%s' % (len(direct_ids) - len(direct_fail), len(direct_ids), direct_fail))
    print('  Rate-module structural fidelity: %d/%d  failures=%s' % (len(module_ids) - len(module_fail), len(module_ids), module_fail))
    print('  Rate-module token counts:        %d/%d  failures=%s' % (len(module_ids) - len(module_count_fail), len(module_ids), module_count_fail))
    print('  exact-control module structure:  %s  failures=%s' % ('pass' if not exact_structure_fail else 'fail', exact_structure_fail))
    print('  named residue: exact control still leaks reference digits 68/917 where live leaks 70/937 (+2 invisible token-count residue)')
    if byte_fail or unstable or direct_fail or module_fail or module_count_fail or exact_structure_fail:
        sys.exit(1)


if __name__ == '__main__':
    main()
