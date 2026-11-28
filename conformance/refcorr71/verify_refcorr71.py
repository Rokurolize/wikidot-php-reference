#!/usr/bin/env python3
"""Verify the REFCORR71 measurement pins against the current checkout."""
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

CASES = HERE / 'cases.jsonl'
EXPECTED = HERE / 'expected.json'
EXPECTED_TOKENS = HERE / 'expected-tokens.json'
CAPTURES = HERE / 'captures.json'


def run_batch(mode, cases):
    payload = ''.join(json.dumps({'id': c['id'], 'source': c['source']}, ensure_ascii=False) + '\n' for c in cases)
    proc = subprocess.run(['php', str(ROOT / 'harness' / 'batch.php'), mode],
                          input=payload, text=True, capture_output=True, cwd=ROOT, timeout=300)
    if proc.returncode:
        sys.stderr.write(proc.stderr)
        sys.exit(proc.returncode)
    got = {}
    for line in proc.stdout.splitlines():
        if line.strip():
            row = json.loads(line)
            got[row['id']] = row.get('output', row.get('error', ''))
    return got


def mask_listpages_box(text):
    out = []
    pos = 0
    needle = '<div class="list-pages-box">'
    while True:
        start = text.find(needle, pos)
        if start < 0:
            out.append(text[pos:])
            break
        out.append(text[pos:start])
        inner = start + len(needle)
        depth = 1
        end = len(text)
        for match in re.finditer(r'<div\b|</div>', text[inner:]):
            depth += 1 if match.group(0) == '<div' else -1
            if depth == 0:
                end = inner + match.end()
                break
        out.append('<div class="module-occurrence"></div>')
        pos = end
    return ''.join(out)


def premask_live(text):
    return mask_listpages_box(text)


def premask_reference(text):
    return re.sub(r'þmodule\s+"ListPages".*?þ', '<div class="module-occurrence"></div>', text, flags=re.S)


def main():
    cases = [json.loads(l) for l in CASES.read_text(encoding='utf-8').splitlines() if l.strip()]
    expected = json.loads(EXPECTED.read_text(encoding='utf-8'))
    expected_tokens = json.loads(EXPECTED_TOKENS.read_text(encoding='utf-8'))
    captures = json.loads(CAPTURES.read_text(encoding='utf-8'))

    got_render = run_batch('render', cases)
    got_tokens = run_batch('tokens', cases)
    byte_fail = [cid for cid, want in expected.items() if got_render.get(cid, '').rstrip('\n') != want]
    token_fail = [cid for cid, want in expected_tokens.items() if got_tokens.get(cid) != want]

    canonical_fail = []
    tidy_fail = []
    for cid, cap in captures.items():
        # Exactly one purifyHtml/libtidy-equivalent pass for the reference side.
        tidy_rc, ref_tidy = cc.rc.run_tidy(got_render.get(cid, '').rstrip('\n'))
        cc.rc.cleanup_tidy_tmp()
        if tidy_rc != 0:
            tidy_fail.append(cid)
            continue
        live_c = cc.canonical_census(premask_live(cap['html']))
        ref_c = cc.canonical_census(premask_reference(ref_tidy))
        if live_c != ref_c:
            canonical_fail.append(cid)

    # Probe-instrumented parser-boundary oracles. These do not compare serving
    # internals; they check the unique bytes that decide body capture versus
    # attr swallowing or literal residue.
    oracle_fail = []
    oracle_expectations = {
        'lp-controls': [
            ('custom_LC_PROPER_BODY', 'LC-PROPER-BODY probe mod-basic', True),
            ('custom_LC_NESTED_CONTROL', 'LC-NESTED-CONTROL probe mod-basic', True),
            ('custom_LC_END_CONTROL', 'LC-END-CONTROL probe mod-basic', True),
            ('unattributed_inline_literal', '[[module ListPages]][[/module]]', True),
            ('empty_closer_residue', '[[/module]]', True),
        ],
        'lp-bodytext-inline': [
            ('inline_body_not_rendered_as_custom_body', 'LBODY probe mod-basic', False),
            ('inline_body_not_left_outside', 'LBODY %%title%%', False),
            ('after_sentinel', 'LBT-AFTER', True),
        ],
        'lp-nested-div-adjacent': [
            ('nested_body_left_outside', 'LNDBODY %%title%%', True),
            ('adjacent_closer_literal', '[[/module]]', True),
            ('after_sentinel', 'LND-AFTER', True),
        ],
        'lp-noclose-inline-end': [
            ('no_close_construct_literal', '[[module ListPages name=&quot;muse-probe-r2mod-module-mod-basic&quot; separate=&quot;no&quot;]]LNOCLOSE-BODY %%title%%', True),
        ],
    }
    for cid, checks in oracle_expectations.items():
        html_text = captures[cid]['html']
        for label, needle, wanted in checks:
            if (needle in html_text) is not wanted:
                oracle_fail.append(f'{cid}:{label}')

    # The decisive token-level pins: inline empty and inline body bytes are in
    # attr, never module_body, while the adjacent nested closer leaves body empty.
    token_rows = {cid: json.loads(got_tokens.get(cid, '{}')) for cid in expected_tokens}
    def first_module(cid):
        for _, token in token_rows[cid].items():
            if token[0] == 'Module':
                return token[1]
        return {}
    token_semantics_fail = []
    for cid, suffix in (
        ('lp-immediate-middle', ']][[/module'),
        ('lp-immediate-end', ']][[/module'),
        ('lp-bodytext-inline', ']]LBODY %%title%%[[/module'),
    ):
        mod = first_module(cid)
        if not mod.get('attr', '').endswith(suffix) or mod.get('module_body') != '':
            token_semantics_fail.append(cid)
    if first_module('lp-nested-div-adjacent').get('module_body') != '':
        token_semantics_fail.append('lp-nested-div-adjacent')

    print('REFCORR71 pins: %d grouped pins covering 12 shape cells' % len(expected))
    print('  expected-render byte pins: %d/%d  failures=%s' % (len(expected) - len(byte_fail), len(expected), byte_fail))
    print('  expected-token byte pins:  %d/%d  failures=%s' % (len(expected_tokens) - len(token_fail), len(expected_tokens), token_fail))
    print('  one-purify live fidelity:  %d/%d  failures=%s tidy=%s' % (len(captures) - len(canonical_fail), len(captures), canonical_fail, tidy_fail))
    print('  parser-boundary oracles:   %s' % ('pass' if not oracle_fail else 'failures=' + repr(oracle_fail)))
    print('  token attr/body semantics: %s' % ('pass' if not token_semantics_fail else 'failures=' + repr(token_semantics_fail)))
    if byte_fail or token_fail or canonical_fail or tidy_fail or oracle_fail or token_semantics_fail:
        sys.exit(1)


if __name__ == '__main__':
    main()
