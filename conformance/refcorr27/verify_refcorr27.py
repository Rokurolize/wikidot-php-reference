#!/usr/bin/env python3
"""Verify the REFCORR27 legacy regression pins."""
import json, subprocess, sys, os
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
BASE=os.path.dirname(__file__)
cases=[]
for line in open(os.path.join(BASE,'cases.jsonl'),encoding='utf8'):
    cases.append(json.loads(line))
payload=''.join(json.dumps(c,ensure_ascii=False,separators=(',',':'))+'\n' for c in cases)
p=subprocess.run(['php','harness/batch.php','render'],input=payload,text=True,capture_output=True,cwd=ROOT)
if p.returncode:
    sys.stderr.write(p.stderr); sys.exit(p.returncode)
expected=json.load(open(os.path.join(BASE,'expected.json'),encoding='utf8'))
failed=[]
seen=set()
for line in p.stdout.splitlines():
    row=json.loads(line); cid=row['id']; seen.add(cid)
    got=row.get('output','').rstrip('\n')
    want=expected[cid]['html'].rstrip('\n')
    if got!=want:
        failed.append((cid,want,got))
missing=set(expected)-seen
if missing or failed:
    for cid in sorted(missing): print('MISSING',cid)
    for cid,want,got in failed:
        print('FAIL',cid); print('want:',repr(want)); print('got :',repr(got))
    sys.exit(1)
print('REFCORR27 pins: %d/%d exact'%(len(expected),len(expected)))
