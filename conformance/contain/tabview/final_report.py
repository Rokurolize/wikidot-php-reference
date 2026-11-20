#!/usr/bin/env python3
"""Final consistent before/after and three-way reports for the Tabview section."""
import json, re, importlib.machinery, importlib.util

loader = importlib.machinery.SourceFileLoader(
    "wikidot_probe", "/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe")
spec = importlib.util.spec_from_loader("wikidot_probe", loader)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

def norm(s):
    return probe.norm(s)

def struct(s):
    s = norm(s).replace("<br />", "<br>").replace("<div >", "<div>")
    return re.sub(r"\s+", " ", re.sub(r">\s+<", "><", s)).strip()

def load(path, key):
    out = {}
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        out[r["id"]] = r.get(key, r.get("error", "MISSING"))
    return out

refb = load("ref-render-before.jsonl", "output")
refa = load("ref-render-after.jsonl", "output")
ftml = load("ftml-dump.jsonl", "html")

lines = []
lines.append("BATTERY reference-vs-ftml (ids normalized for tab/tabview counters; struct also removes frame whitespace, <div >, <br />):")
for label, R in [("before", refb), ("after", refa)]:
    ids = sorted(set(R) & set(ftml))
    raw = sum(R[i] == ftml[i] for i in ids)
    nm = sum(norm(R[i]) == norm(ftml[i]) for i in ids)
    st = sum(struct(R[i]) == struct(ftml[i]) for i in ids)
    lines.append(f"  {label}: ids={len(ids)} raw={raw} norm={nm} struct={st}")
common = sorted(set(refb) & set(refa) & set(ftml))
lines.append(f"  common-53 before struct={sum(struct(refb[i])==struct(ftml[i]) for i in common)}/{len(common)} after struct={sum(struct(refa[i])==struct(ftml[i]) for i in common)}/{len(common)}")

changed = [i for i in sorted(refa) if norm(refb.get(i, "MISSING")) != norm(refa[i])]
lines.append(f"  render changed by corrections (norm, excluding counter/whitespace): {len(changed)}: {', '.join(changed)}")

def reports(capfile, reffile, ftfile, title):
    caps = json.load(open(capfile))
    ref = load(reffile, "output")
    ft = load(ftfile, "html")
    lines.append("")
    lines.append(title)
    counts = {"all3": 0, "ref_live": 0, "ftml_live": 0, "ref_ftml": 0, "none": 0}
    for k in sorted(caps):
        sr, sf, sl = struct(ref.get(k, "MISSING")), struct(ft.get(k, "MISSING")), struct(caps[k]["html"])
        rl, fl, rf = sr == sl, sf == sl, sr == sf
        key = "all3" if rl and fl else "ref_live" if rl else "ftml_live" if fl else "ref_ftml" if rf else "none"
        counts[key] += 1
        lines.append(f"  {k}: {key} (ref_live={rl} ftml_live={fl} ref_ftml={rf})")
        if key != "all3":
            lines.append("    LIVE: " + repr(sl)[:340])
            lines.append("    REF : " + repr(sr)[:340])
            lines.append("    FTL : " + repr(sf)[:340])
    lines.append("  counts: " + str(counts))

for capfile, reffile, ftfile, title in [
    ("probe-captures.json", "ref-probe-render-before.jsonl", "ftml-probe-dump.jsonl", "PROBES before three-way:"),
    ("probe-captures.json", "ref-probe-render-after.jsonl", "ftml-probe-dump.jsonl", "PROBES after three-way:"),
    ("probe-captures2.json", "ref-probe2-render-after.jsonl", "ftml-probe2-dump.jsonl", "FOLLOW-UP PROBES after three-way:"),
]:
    reports(capfile, reffile, ftfile, title)

text = "\n".join(lines) + "\n"
open("compare-final.txt", "w").write(text)
print(text)
