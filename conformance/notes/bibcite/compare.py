import json, re, sys

ANCHOR = re.compile(r'<a\b[^>]*\bclass="bibcite"[^>]*>.*?</a>', re.S)
ERROR = re.compile(r'<span class="error-inline">Bibliography item <em>.*?</em> not found\.</span>', re.S)
SUFFIX = re.compile(r'(bibcite-\d+)-\d+a')

def load(path):
    out = {}
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line: continue
        d = json.loads(line)
        out[d['id']] = d
    return out

def shapes(html):
    return [m.group(0) for m in ANCHOR.finditer(html or '')] + [m.group(0) for m in ERROR.finditer(html or '')]

def canon(frag):
    s = frag.replace('&#39;', "'").replace('&#039;', "'").replace('&apos;', "'")
    s = SUFFIX.sub(r'\1', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def canon_html(html):
    s = (html or '').replace('&#39;', "'").replace('&#039;', "'")
    s = s.replace('<br />', '<br>').replace('&#10;', '\n')
    s = SUFFIX.sub(r'\1', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def report(name, ref_path, ftml_path, live_path=None):
    ref, ftml = load(ref_path), load(ftml_path)
    live = {}
    if live_path:
        for k, v in json.load(open(live_path, encoding='utf-8')).items():
            live[k] = v
    ids = list(ref)
    out = []
    out.append('=== %s ===' % name)
    out.append('cases: ref=%d ftml=%d live=%d' % (len(ref), len(ftml), len(live)))
    raw_same = shape_same = html_same = whole_same = 0
    raw_anchor_same = 0
    n_anchor = n_error = 0
    for cid in ids:
        r = ref[cid].get('output') or ''
        f = ftml[cid].get('html') or ''
        lv = live.get(cid, {}).get('html') or ''
        rs, fs, ls = shapes(r), shapes(f), shapes(lv)
        n_anchor += len([x for x in rs if 'class="bibcite"' in x])
        n_error += len([x for x in rs if 'error-inline' in x])
        sr, sf = [canon(x) for x in rs], [canon(x) for x in fs]
        whole_ok = r == f
        raw_ok = rs == fs
        shape_ok = sr == sf
        html_ok = canon_html(r) == canon_html(f)
        whole_same += whole_ok
        raw_same += raw_ok
        shape_same += shape_ok
        html_same += html_ok
        if raw_ok and rs: raw_anchor_same += 1
        if not shape_ok or (live and [canon(x) for x in ls] != sr):
            out.append('%s | ref=%s | ftml=%s%s' % (
                cid, ' ; '.join(rs) or '-', ' ; '.join(fs) or '-',
                (' | live=' + ' ; '.join(ls) if live else '')))
    out.append('raw whole-string equal: %d/%d' % (whole_same, len(ids)))
    out.append('canonicalized whole-html equal: %d/%d' % (html_same, len(ids)))
    out.append('bibcite-shape equal after quote decode + suffix mask: %d/%d' % (shape_same, len(ids)))
    out.append('bibcite-shape raw equal: %d/%d' % (raw_same, len(ids)))
    out.append('anon bibcite anchor fragments in ref: %d; error spans: %d' % (n_anchor, n_error))
    if live:
        live_valid = sum(1 for v in live.values() if v.get('valid'))
        live_stable = sum(1 for v in live.values() if v.get('stable'))
        live_src = sum(1 for v in live.values() if v.get('saved_source_matches'))
        out.append('live captures: %d valid, %d stable, %d source-matching' % (live_valid, live_stable, live_src))
        live_shape = sum(1 for cid in ids if [canon(x) for x in shapes(ref[cid].get('output') or '')] == [canon(x) for x in shapes(live.get(cid, {}).get('html') or '')])
        ftml_live_shape = sum(1 for cid in ids if [canon(x) for x in shapes(ftml[cid].get('html') or '')] == [canon(x) for x in shapes(live.get(cid, {}).get('html') or '')])
        out.append('ref-vs-live bibcite-shape equal: %d/%d' % (live_shape, len(ids)))
        out.append('ftml-vs-live bibcite-shape equal: %d/%d' % (ftml_live_shape, len(ids)))
    return '\n'.join(out) + '\n'

if __name__ == '__main__':
    name = sys.argv[1]
    ref, ftml = sys.argv[2], sys.argv[3]
    live = sys.argv[4] if len(sys.argv) > 4 else None
    text = report(name, ref, ftml, live)
    open('compare-%s.txt' % name, 'w', encoding='utf-8').write(text)
    print(text)
