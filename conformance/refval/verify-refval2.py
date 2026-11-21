#!/usr/bin/env python3
"""REFVAL2 post-correction verification.

Compares, per rule:
  1. battery movement: ref-render-after.jsonl (pre-correction) vs
     ref-render-corrected.jsonl.
  2. corrected probe renders vs live captures, under the adjudication
     normalizations recorded in each rule's SECTION.md:
       frame: trim + collapse blank-line runs; unwrap a lone error-block
              div from its <p> wrapper (Stage 2 div-in-p surface); drop the
              fossil template's trailing space before an anchor's '>'.
       gallery: campaign norm() + serving masks (wdfiles host, probe page
              name, gallery-box-<n> id, with-lb class, lightbox scripts,
              pretty-print whitespace, gallery-image-size-* img class).
       file: frame + href base normalization (live's wdfiles host and the
              current page's local--files prefix are serving-supplied).
  3. supplementary probe renders vs their live captures, same rules.
"""
import json, re, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))

def loadj(path):
    out = {}
    for l in open(path):
        l = l.strip()
        if not l:
            continue
        d = json.loads(l)
        out[d['id']] = d
    return out

def frame(t):
    t = t.strip()
    t = re.sub(r'\n\s*\n', '\n', t)
    t = t.replace('" >', '">')
    m = re.fullmatch(r'<p>(<div class="error-block">.*?</div>)</p>', t, flags=re.S)
    if m:
        t = m.group(1)
    if 'error-block' in t:
        # Stage 2 splits paragraphs around block-level error divs and
        # drops empty paragraphs; compare the token-level content.
        t = t.replace('<p></p>', '')
        t = t.replace('<p>', '').replace('</p>', '')
        t = re.sub(r'>\s+', '>', t)
        t = re.sub(r'\s+<', '<', t)
        t = t.strip()
    if t == '<p></p>':
        t = ''
    return t

def cnorm(t):
    t = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), t)
    t = t.replace("&nbsp;", "\u00a0")
    t = re.sub(r"\b(wiki-tab-|wiki-tabview-|wiki-tab-0-)[0-9a-f-]{4,}", r"\1X", t)
    t = re.sub(r'data-(delta|timestamp)="[^"]*"', "", t)
    t = re.sub(r"time_\d+", "time_X", t)
    t = re.sub(r"<script[^>]*>.*?</script>", "", t, flags=re.S)
    t = t.replace(' class="newpage"', "")
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def gnorm(t, pageprefix):
    t = cnorm(t)
    t = re.sub(r' id="gallery-box-\d+"', "", t)
    t = t.replace('> <', '><')
    t = t.replace("https://sandbox-for-codex.wdfiles.com", "")
    t = re.sub(r"/(local--files|local--resized-images)/" + pageprefix + r"p\d+/", r"/\1//", t)
    t = re.sub(r"/(local--files|local--resized-images)/" + pageprefix + r"(pg\d+)/", r"/\1//", t)
    t = t.replace(' class="with-lb"', "")
    t = re.sub(r' class="gallery-image-size-\w+"', "", t)
    t = t.replace('" >', '">')
    t = t.replace(' />', '/>')
    return t

def fnorm(t, page):
    t = frame(t)
    t = t.replace("https://sandbox-for-codex.wdfiles.com/local--files/" + page + "/", "/")
    t = t.replace("https://sandbox-for-codex.wdfiles.com", "")
    return t

def out(d, pid):
    e = d.get(pid, {})
    return e.get('output', '') if 'error' not in e else '<ERROR: ' + e['error'] + '>'

def main():
    for rule in ('gallery', 'user', 'button', 'embed', 'social', 'file'):
        rd = os.path.join(ROOT, rule)
        after = loadj(os.path.join(rd, 'ref-render-after.jsonl'))
        corr = loadj(os.path.join(rd, 'ref-render-corrected.jsonl'))
        moved = [pid for pid in sorted(set(after) | set(corr))
                 if after.get(pid, {}).get('output', after.get(pid, {}).get('error')) != corr.get(pid, {}).get('output', corr.get(pid, {}).get('error'))]
        print(f"== {rule}: battery movement after->corrected: {len(moved)} {moved}")
        caps = json.load(open(os.path.join(rd, 'captures.json')))
        bad = []
        for pid in sorted(caps):
            a = out(corr, pid)
            h = caps[pid]['html']
            if rule == 'gallery':
                ok = gnorm(a, 'muse-probe-refval-gallery-') == gnorm(h, 'muse-probe-refval-gallery-')
            elif rule == 'file':
                ok = fnorm(a, caps[pid]['fullname']) == fnorm(h, caps[pid]['fullname'])
            elif rule == 'user':
                ok = None  # environment-bound render; see SECTION.md
            elif rule == 'social':
                ok = None  # handoff marker; adjudicated in SECTION.md
            else:
                ok = frame(a) == frame(h)
            if ok is False:
                bad.append(pid)
        if rule in ('button', 'embed', 'file', 'gallery'):
            print(f"   corrected probes vs live: {len(caps) - len(bad)}/{len(caps)} agree; disagree: {bad}")
        # supplementary
        supp_path = os.path.join(rd, 'supplementary-render.jsonl')
        if os.path.exists(supp_path):
            supp = loadj(supp_path)
            scaps = {}
            for f in os.listdir(rd):
                if f.startswith('probes') and f.endswith('-captures.json') and f != 'probes5-captures.json':
                    scaps.update(json.load(open(os.path.join(rd, f))))
            sbad = []
            for pid in sorted(scaps):
                a = out(supp, pid)
                h = scaps[pid]['html']
                if rule == 'gallery':
                    ok = gnorm(a, 'muse-probe-refval2-gallery-') == gnorm(h, 'muse-probe-refval2-gallery-')
                elif rule == 'file':
                    ok = fnorm(a, scaps[pid]['fullname']) == fnorm(h, scaps[pid]['fullname'])
                else:
                    ok = frame(a) == frame(h)
                if not ok:
                    sbad.append(pid)
            print(f"   supplementary vs live: {len(scaps) - len(sbad)}/{len(scaps)} agree; disagree: {sbad}")

def probes5():
    # misc probes fb01/fb02 (button) and ff01 (file) have their own render
    # file, evidence/button/probes5-render.jsonl.
    rd = os.path.join(ROOT, 'button')
    rend = loadj(os.path.join(rd, 'probes5-render.jsonl'))
    bcaps = json.load(open(os.path.join(rd, 'probes5-captures.json')))
    fcaps = json.load(open(os.path.join(ROOT, 'file', 'probes5-captures.json')))
    ok = all(frame(out(rend, pid)) == frame(bcaps[pid]['html']) for pid in ('fb01', 'fb02'))
    ok = ok and 'Say &quot;hi&quot;' in out(rend, 'ff01') and 'Say &quot;hi&quot;' in fcaps['ff01']['html']
    print(f"== misc probes5 (fb01, fb02, ff01): {'all agree' if ok else 'DISAGREE'}")

if __name__ == '__main__':
    main()
    probes5()
