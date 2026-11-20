#!/usr/bin/env python3
"""Three-way probe report: live (cached capture) vs reference vs ftml dumper.

Rewrites probe-cases.jsonl from the verified cached sources, applies the
campaign norm() masking (random tab/tabview ids, dates, scripts) plus the
strict structural pass, and reports agreement at raw, norm and struct levels."""
import json, re, importlib.machinery, importlib.util

loader = importlib.machinery.SourceFileLoader(
    "wikidot_probe", "/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe")
spec = importlib.util.spec_from_loader("wikidot_probe", loader)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

def norm(s):
    return probe.norm(s)

def struct(s):
    s = norm(s)
    s = s.replace("<br />", "<br>").replace("<div >", "<div>")
    s = re.sub(r">\s+<", "><", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def load(path, key):
    out = {}
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        out[r["id"]] = r.get(key, r.get("error", "MISSING"))
    return out

caps = json.load(open("probe-captures.json"))
with open("probe-cases.jsonl", "w", encoding="utf-8") as f:
    for k, v in caps.items():
        f.write(json.dumps({"id": k, "source": v["source"]}, ensure_ascii=False) + "\n")

ref = load("ref-probe-render-before.jsonl", "output")
ftml = load("ftml-probe-dump.jsonl", "html")
ids = sorted(caps)
print(f"probes={len(ids)}")
counts = {"all3": 0, "ref_live": 0, "ftml_live": 0, "ref_ftml": 0, "none": 0}
for k in ids:
    live = caps[k]["html"]
    r, f = ref.get(k, "MISSING"), ftml.get(k, "MISSING")
    sr, sf, sl = struct(r), struct(f), struct(live)
    eq_rl, eq_fl, eq_rf = sr == sl, sf == sl, sr == sf
    key = "all3" if eq_rl and eq_fl else "ref_live" if eq_rl else "ftml_live" if eq_fl else "ref_ftml" if eq_rf else "none"
    counts[key] += 1
    print(f"{k}: {key} (ref_live={eq_rl} ftml_live={eq_fl} ref_ftml={eq_rf})")
    if key != "all3":
        print("  LIVE:", repr(sl)[:320])
        print("  REF :", repr(sr)[:320])
        print("  FTL :", repr(sf)[:320])
print("counts:", counts)
