#!/usr/bin/env python3
"""Verify REFCORR34 inline-scope edge whitespace ownership across pipeline stages."""
import json, subprocess, sys, os
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
cases=[
    {
        'id':'r34-strong-span-leading',
        'source':'**[[span style="color: rgb(0, 117, 200)"]] 바다 매미 소리 들어봤어?[[/span]]**',
        'html':'<p><strong><span style="color: rgb(0, 117, 200)">바다 매미 소리 들어봤어?</span></strong></p>',
    },
    {
        'id':'r34-strong-span-trailing',
        'source':'**[[span style="color: rgb(0, 117, 200)"]]6개월 전 나는 휴학 신청을 내고 여행 중이었다. [[/span]]**',
        'html':'<p><strong><span style="color: rgb(0, 117, 200)">6개월 전 나는 휴학 신청을 내고 여행 중이었다.</span></strong></p>',
    },
    {
        'id':'r34-size-underline-list',
        'source':'# a\n# [[size 0%]]__ [[/size]]\n# b\n# [[size 0%]]__ [[/size]]',
        'html':'<ol>\n<li>a</li>\n<li><span style="font-size:0%;">__</span></li>\n<li>b</li>\n<li><span style="font-size:0%;">__</span></li>\n</ol>',
    },
    {
        'id':'r34-size-edge-midtext',
        'source':'A[[size 60%]] x [[/size]]B',
        'html':'<p>A <span style="font-size:60%;">x</span> B</p>',
    },
]
payload=''.join(json.dumps({'id':c['id'],'source':c['source']},ensure_ascii=False,separators=(',',':'))+'\n' for c in cases)
p=subprocess.run(['php','harness/batch.php','render'],input=payload,text=True,capture_output=True,cwd=ROOT)
if p.returncode:
    sys.stderr.write(p.stderr); sys.exit(p.returncode)
rows={}
for line in p.stdout.splitlines():
    if line.strip():
        row=json.loads(line); rows[row['id']]=row.get('output','').rstrip('\n')
failed=[]
for c in cases:
    got=rows.get(c['id'])
    if got!=c['html']:
        failed.append((c['id'],c['html'],got))
if failed:
    for cid,want,got in failed:
        print('FAIL',cid); print('want:',repr(want)); print('got :',repr(got))
    sys.exit(1)
print('REFCORR34 pins: %d/%d exact'%(len(cases),len(cases)))
