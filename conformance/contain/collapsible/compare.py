import json
import re
import sys

# Rule-level structural comparator for the R2-contain Collapsible stage.
# Masked: counter-bearing element ids (Collapsible::$count and Tabview's
# counter leak across batch cases; root audit conformance-refphp/contain/audit/
# audit-findings.md), the <br /> vs <br> spelling, HTML entity spellings for
# apostrophes, and all inter-tag whitespace (the live serializer's pretty-print
# newlines are frame-level surface owned by later rules). Nesting, tag names,
# class names, attributes and text are left intact.

def norm(html):
    s = html
    s = re.sub(r'collapsible-block-\d+', 'collapsible-block-N', s)
    s = re.sub(r'tabview-(?:\d+|[0-9a-f]{16,})', 'tabview-N', s)
    s = re.sub(r'tab-\d+', 'tab-N', s)
    s = re.sub(r'<br\s*/>', '<br>', s)
    s = s.replace('&#039;', "'").replace('&#39;', "'")
    s = re.sub(r'>\s+<', '><', s)
    return s.strip()

def load_jsonl(path, key='output'):
    out = {}
    for line in open(path):
        d = json.loads(line)
        out[d['id']] = d.get(key, d.get('html', d.get('error', '')))
    return out

def load_captures(path):
    d = json.load(open(path))
    return {k: v['html'] for k, v in d.items() if v.get('valid')}

def load_tokens(path):
    out = {}
    for line in open(path):
        d = json.loads(line)
        try:
            toks = json.loads(d['output'])
        except Exception:
            toks = d.get('output', '')
        if isinstance(toks, dict):
            # token ids are a leaking static counter; compare values only
            out[d['id']] = sorted(json.dumps(v, sort_keys=True, ensure_ascii=False)
                                  for v in toks.values())
        else:
            out[d['id']] = toks
    return out

def compare_sets(name, left, right):
    ids = sorted(set(left) & set(right))
    agree = [i for i in ids if norm(left[i]) == norm(right[i])]
    disagree = [i for i in ids if norm(left[i]) != norm(right[i])]
    raw = [i for i in ids if left[i] == right[i]]
    print(f"{name}: {len(agree)}/{len(ids)} structural, {len(raw)}/{len(ids)} raw")
    if disagree:
        print("  disagree:", ", ".join(disagree))
    return agree, disagree

if __name__ == '__main__':
    base = sys.argv[1] if len(sys.argv) > 1 else '.'
    rf_before = load_jsonl(f'{base}/ref-render-before.jsonl')
    rf_after = load_jsonl(f'{base}/ref-render-after.jsonl')
    ftml = load_jsonl(f'{base}/ftml-dump.jsonl', 'html')
    live = load_captures(f'{base}/probe-captures.json')
    print("=== BATTERY (reference vs ftml dumper) ===")
    compare_sets('before vs ftml', rf_before, ftml)
    compare_sets('after  vs ftml', rf_after, ftml)
    changed = [i for i in sorted(rf_before) if rf_before[i] != rf_after[i]]
    print('render changed cases:', len(changed), ', '.join(changed))
    tb = load_tokens(f'{base}/ref-tokens-before.jsonl')
    ta = load_tokens(f'{base}/ref-tokens-after.jsonl')
    tchanged = [i for i in sorted(tb) if tb[i] != ta[i]]
    print('token value changed cases:', len(tchanged), ', '.join(tchanged))
    print("=== PROBES (three-way) ===")
    rfp = load_jsonl(f'{base}/ref-probe-render.jsonl')
    rfp_after = load_jsonl(f'{base}/ref-probe-render-after.jsonl')
    fp = load_jsonl(f'{base}/ftml-probe-dump.jsonl', 'html')
    compare_sets('probe ref-before vs live', rfp, live)
    compare_sets('probe ref-after  vs live', rfp_after, live)
    compare_sets('probe ftml       vs live', fp, live)
