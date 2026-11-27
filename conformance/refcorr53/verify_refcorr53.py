#!/usr/bin/env python3
import json,re,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CENSUS=Path('/home/roku/.local/state/wikijump/muse-bhl/post-agy-finish/lanes/ref-census-cn')
sys.path.insert(0,str(CENSUS))
import census_compare_cn as cc

def canon(raw): return cc.canonical_census(raw)
def extract_div(html,start):
    depth=0
    for m in re.finditer(r'<div\b|</div>',html[start:]):
        if m.group(0)=='<div': depth+=1
        else:
            depth-=1
            if depth==0: return html[start:start+m.end()]
    raise ValueError('unclosed div')
def footnote_item(html,n=1):
    m=re.search(r'<div class="footnote-footer" id="footnote-%d">'%n,html)
    if not m: raise ValueError('missing footnote item %d'%n)
    return extract_div(html,m.start())
def main():
    cases=[json.loads(l) for l in (HERE/'cases.jsonl').read_text(encoding='utf8').splitlines() if l.strip()]
    expected=json.loads((HERE/'expected.json').read_text(encoding='utf8'))
    captures=json.loads((HERE/'captures.json').read_text(encoding='utf8'))
    payload=''.join(json.dumps({'id':c['id'],'source':c['source']},ensure_ascii=False)+'\n' for c in cases)
    proc=subprocess.run(['php',str(ROOT/'harness'/'batch.php'),'render'],input=payload,text=True,capture_output=True,cwd=ROOT,timeout=300)
    if proc.returncode:
        sys.stderr.write(proc.stderr); sys.exit(proc.returncode)
    got={}
    kinds={c['id']:c.get('kind','full-page') for c in cases}
    for line in proc.stdout.splitlines():
        if line.strip():
            row=json.loads(line); out=row.get('output',row.get('error','')).rstrip('\n')
            if kinds[row['id']]=='footnote-item': out=footnote_item(out,1)
            got[row['id']]=out
    byte_fail=[]; live_fail=[]; capture_invalid=[]; raw_equal=[]
    for cid,want in expected.items():
        if got.get(cid)!=want: byte_fail.append(cid)
        cap=captures[cid]
        if not (cap.get('valid') and cap.get('stable') and cap.get('saved_source_matches')): capture_invalid.append(cid)
        if canon(got.get(cid,''))!=canon(cap['html']): live_fail.append(cid)
        if got.get(cid,'')==cap['html']: raw_equal.append(cid)
    print('REFCORR53 pins: %d reduced grouped-cell/exact pins checked'%len(expected))
    print('  expected-render byte pins: %d/%d  failures=%s'%(len(expected)-len(byte_fail),len(expected),byte_fail))
    print('  live canonical fidelity:   %d/%d  failures=%s'%(len(expected)-len(live_fail),len(expected),live_fail))
    print('  capture validity:          %d/%d  failures=%s'%(len(expected)-len(capture_invalid),len(expected),capture_invalid))
    print('  exact raw served bytes:    %d/%d  equal=%s'%(len(raw_equal),len(expected),raw_equal))
    if byte_fail or live_fail or capture_invalid: sys.exit(1)
if __name__=='__main__': main()
