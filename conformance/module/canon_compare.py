import json, os, re
def canon(s):
    if not isinstance(s,str): s=str(s)
    s=s.replace("\r\n","\n").replace("<br />","<br>").replace("\xa0"," ")
    s=re.sub(r"\xfe[^\xfe]*\xfe","MARKER",s)
    s=re.sub(r"TODO: module [A-Za-z]+","TODO",s)
    if "page-rate-widget-box" in s: s="WIDGET"
    s=s.replace(' rel="noopener noreferrer"','')
    s=re.sub(r"\n{2,}","\n",s)
    return s.strip("\n")
def load(p): return {r["id"]:r for r in map(json.loads,open(p))}
for d,cap in [("modulepre","captures.json"),("module","captures.json"),("module654","captures-partial.json")]:
    base=f"conformance-refphp/module/{d}/"
    cases={}
    for fn in ["probe-cases.jsonl","probe-cases2.jsonl"]:
        if os.path.exists(base+fn): cases.update(load(base+fn))
    rfs=[f for f in os.listdir(base) if f.startswith("ref-probe-render") and f.endswith(".jsonl")]
    rf=sorted(rfs)[-1]
    ref=load(base+rf); ftm=load(base+"ftml-probe-dump.jsonl")
    live=json.load(open(base+cap))
    c={"all":0,"rl":0,"fl":0,"rf":0,"valid":0}
    for cid,lv in live.items():
        if not lv.get("valid"): continue
        c["valid"]+=1
        r=canon(ref.get(cid,{}).get("output", ref.get(cid,{}).get("error","")))
        f=canon(ftm.get(cid,{}).get("html","")); l=canon(lv.get("html",""))
        a_rl,a_fl,a_rf=(r==l),(f==l),(r==f)
        c["rl"]+=a_rl; c["fl"]+=a_fl; c["rf"]+=a_rf; c["all"]+=a_rl and a_fl and a_rf
        if not a_rl: print(f"  {d} {cid}: ref={r[:80]!r} live={l[:80]!r} ftml={f[:80]!r}")
    print(f"{d}: probes={len(cases)} captured={len(live)} valid={c['valid']} all3={c['all']} ref==live={c['rl']} ftml==live={c['fl']} ref==ftml={c['rf']} (ref file {rf})")
