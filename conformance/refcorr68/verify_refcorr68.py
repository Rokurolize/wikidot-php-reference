#!/usr/bin/env python3
"""Offline REFCORR68 adjudication pins.

This record intentionally has no implementation correction.  The verifier
therefore pins (a) the reference placeholder-index leaks measured on the
immutable probe matrix, (b) the recorded equality of those reference leaks
with current sandbox live leaks, (c) the token-table summaries, and (d) the
narrow canonical comparison that isolates the stale production residual to
placeholder numbering.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEAK = re.compile(r'(?<!\d)(\d{6})(?!\d)')


def first_leak(html):
    match = LEAK.search(html)
    return match.group(1) if match else None


def load_cases():
    return [json.loads(line) for line in (HERE / 'cases.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]


def run_batch(cases, mode):
    payload = ''.join(json.dumps({'id': c['id'], 'source': c['source']}, ensure_ascii=False) + '\n' for c in cases)
    proc = subprocess.run(
        ['php', str(ROOT / 'harness' / 'batch.php'), mode],
        input=payload,
        text=True,
        capture_output=True,
        cwd=ROOT,
        timeout=300,
    )
    if proc.returncode:
        sys.stderr.write(proc.stderr)
        sys.exit(proc.returncode)
    rows = {}
    for line in proc.stdout.splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row['id']] = row
    return rows


def canonical_positive_fragment(html):
    start = html.find('<div style="text-align: right;">')
    end = html.find('\n<p><strong>项目编号')
    if start < 0 or end < 0:
        raise ValueError('positive canonical markers absent')
    return '\n\n\n' + html[:start] + '<div style="text-align: right;"></div>' + html[end:] + '\n'


def mask_leaks(html):
    return LEAK.sub('@@@@@@', html)


def main():
    cases = load_cases()
    expected = json.loads((HERE / 'expected-leaks.json').read_text(encoding='utf-8'))
    matrix = json.loads((HERE / 'leak-matrix.json').read_text(encoding='utf-8'))
    captures = json.loads((HERE / 'captures.json').read_text(encoding='utf-8'))
    production = json.loads((HERE / 'production-cached-evidence.json').read_text(encoding='utf-8'))
    canonical_record = json.loads((HERE / 'canonical-comparison.json').read_text(encoding='utf-8'))
    token_rows = [json.loads(line) for line in (HERE / 'token-summary.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    token_expected = {row['id']: row for row in token_rows}

    renders = run_batch(cases, 'render')
    render_leaks = {case['id']: first_leak(renders[case['id']].get('output', '')) for case in cases}
    leak_fail = sorted(cid for cid, want in expected.items() if render_leaks.get(cid) != want)

    live_fail = []
    for cid, want in matrix['live_leaks'].items():
        if cid == 'posfull-recapture':
            continue
        got = first_leak(captures[cid]['html'])
        if got != want or got != render_leaks.get(cid):
            live_fail.append(cid)
    recapture = captures['posfull-recapture']
    recapture_ok = (
        first_leak(recapture['html']) == matrix['live_leaks']['posfull-recapture']
        and recapture['html'].count('newpage') == 0
        and recapture['stable'] is True
        and recapture['valid'] is True
        and recapture['saved_source_matches'] is True
    )

    tokens = run_batch(cases, 'tokens')
    token_fail = []
    for case in cases:
        cid = case['id']
        want = token_expected[cid]
        got_tokens = json.loads(tokens[cid]['output'])
        counts = {}
        for token in got_tokens.values():
            counts[token[0]] = counts.get(token[0], 0) + 1
        got = {'entries': len(got_tokens), 'max_key': max(map(int, got_tokens)), 'rule_counts': counts}
        if got != {'entries': want['entries'], 'max_key': want['max_key'], 'rule_counts': want['rule_counts']}:
            token_fail.append(cid)

    positive = captures['poslinks']['html']
    canonical_equal = mask_leaks(canonical_positive_fragment(positive)) == mask_leaks(production['html'])
    canonical_ok = (
        canonical_equal == canonical_record['sandbox_poslinks_canonical_masked_equals_production_cached_masked']
        and canonical_equal is True
        and first_leak(production['html']) == '274275'
        and first_leak(positive) == '271272'
    )

    print('REFCORR68 adjudication pins: %d exact-source probe cases checked' % len(cases))
    print('  reference leak pins:       %d/%d  failures=%s' % (len(expected) - len(leak_fail), len(expected), leak_fail))
    print('  sandbox live leak equality:%d/%d  failures=%s' % (len(matrix['live_leaks']) - 1 - len(live_fail), len(matrix['live_leaks']) - 1, live_fail))
    print('  token-table summaries:     %d/%d  failures=%s' % (len(cases) - len(token_fail), len(cases), token_fail))
    print('  post-link recapture:       %s' % ('pass' if recapture_ok else 'FAIL'))
    print('  cached-production isolate: %s' % ('pass' if canonical_ok else 'FAIL'))
    if leak_fail or live_fail or token_fail or not recapture_ok or not canonical_ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
