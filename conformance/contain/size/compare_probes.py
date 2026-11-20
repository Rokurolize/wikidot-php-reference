#!/usr/bin/env python3
"""Three-way structural comparison of cached live Size probes against reference and ftml."""
import importlib.machinery
import importlib.util
import json
import re
import sys

loader = importlib.machinery.SourceFileLoader(
    "wikidot_probe",
    "/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe",
)
spec = importlib.util.spec_from_loader("wikidot_probe", loader)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

def frame(s):
    s = probe.norm(s)
    s = s.replace("\r\n", "\n")
    s = s.replace("<br />", "<br>")
    s = s.replace("<div >", "<div>")
    s = s.replace("&#39;", "'")
    s = re.sub(r">\s+<", "><", s)
    return s.strip()

def load_jsonl(path, key):
    out = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            row = json.loads(line)
            out[row["id"]] = row[key]
    return out

def main():
    capdir = sys.argv[1] if len(sys.argv) > 1 else "."
    reffile = sys.argv[2] if len(sys.argv) > 2 else f"{capdir}/probe-ref-render.jsonl"
    cap = json.load(open(f"{capdir}/probe-captures.json", encoding="utf-8"))
    ref = load_jsonl(reffile, "output")
    ftm = load_jsonl(f"{capdir}/probe-ftml-dump.jsonl", "html")
    good = all(v.get("valid") and v.get("stable") and v.get("saved_source_matches") for v in cap.values())
    print(f"captures={len(cap)} all_valid_stable_srcmatch={good}")
    n = r = f = 0
    for cid, v in cap.items():
        live = frame(v["html"])
        rr = frame(ref.get(cid, ""))
        ff = frame(ftm.get(cid, ""))
        r_ok = live == rr
        f_ok = live == ff
        n += r_ok
        f += f_ok
        r += (r_ok and f_ok)
        if not (r_ok and f_ok):
            print(f"\n=== {cid} ref_live={r_ok} ftml_live={f_ok} ===")
            print(f"LIVE: {live!r}")
            print(f"REF : {rr!r}")
            print(f"FTML: {ff!r}")
    print(f"\nref==live {n}/{len(cap)}; ftml==live {f}/{len(cap)}; all-three {r}/{len(cap)}")

if __name__ == "__main__":
    main()
