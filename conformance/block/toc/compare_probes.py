#!/usr/bin/env python3
"""Compare live saved-page captures, the corrected/uncorrected reference and the
shared ftml dumper over the focused Toc probe set, on the TOC-owned surface.

Usage: python3 compare_probes.py <ref-render-file>
"""
import json
import sys

BASE = "/home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh-r2block/conformance-refphp/block/toc"
exec(open(f"{BASE}/compare_battery.py").read().split("def main()")[0])


def main():
    ref_path = sys.argv[1] if len(sys.argv) > 1 else f"{BASE}/ref-render-final.jsonl"
    caps = json.load(open(f"{BASE}/captures.json", encoding="utf-8"))
    ref = load(ref_path)
    ftml = load(f"{BASE}/ftml-probe-dump.jsonl")
    ids = [json.loads(l)["id"] for l in open(f"{BASE}/probe_cases.jsonl", encoding="utf-8") if l.strip()]
    stats = {"all3": 0, "ref_live": 0, "ftml_live": 0, "ref_ftml": 0, "none": 0}
    for cid in ids:
        c = caps[cid]
        live = c["html"]
        rh = ref[cid].get("output", "")
        fh = ftml[cid].get("html", "")
        sigs = [entries(x) for x in (rh, fh, live)]
        chromes = [chrome(toc_box(x)) for x in (rh, fh, live)]
        r_ok, f_ok = sigs[0] == sigs[2] and chromes[0] == chromes[2], sigs[1] == sigs[2] and chromes[1] == chromes[2]
        if r_ok and f_ok:
            stats["all3"] += 1
        elif r_ok:
            stats["ref_live"] += 1
        elif f_ok:
            stats["ftml_live"] += 1
        elif sigs[0] == sigs[1] and chromes[0] == chromes[1]:
            stats["ref_ftml"] += 1
        else:
            stats["none"] += 1
        if not (r_ok and f_ok):
            print(f"=== {cid} (valid={c.get('valid')} stable={c.get('stable')} srcmatch={c.get('saved_source_matches')}) ===")
            print("  ref chrome :", chromes[0])
            print("  ftml chrome:", chromes[1])
            print("  live chrome:", chromes[2])
            if not (sigs[0] == sigs[1] == sigs[2]):
                print("  ref entries :", sigs[0])
                print("  ftml entries:", sigs[1])
                print("  live entries:", sigs[2])
    print("STATS", stats, "total", len(ids))


if __name__ == "__main__":
    main()
