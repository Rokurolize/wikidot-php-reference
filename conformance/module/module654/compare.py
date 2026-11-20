#!/usr/bin/env python3
"""Compare reference-render, ftml-dump and live-capture outputs over the battery.

Prints one line per case with a coarse disposition. The only normalization is
frame-level surface: <br /> vs <br>, the non-breaking space ftml's preproc
inserts after an opener, and trailing paragraph padding. The \\xFE module
marker and ftml's serving-layer placeholders (TODO: module, <style>) are
reported as surface, not as matching-level divergences.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    out = {}
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            out[rec["id"]] = rec
    return out


def frame_norm(s):
    if not isinstance(s, str):
        return str(s)
    return (s.replace("<br />", "<br>").replace("\xa0", " ")
             .rstrip("\n"))


def main():
    ref_name = sys.argv[1] if len(sys.argv) > 1 else "ref-render-before.jsonl"
    ref = load(ref_name)
    ftml = load("ftml-dump.jsonl")
    battery = load("battery.jsonl")
    counts = {"match": 0, "surface": 0, "matching_divergence": 0}
    for cid in battery:
        r = ref.get(cid, {})
        f = ftml.get(cid, {})
        rout = r.get("output", "ERR:" + str(r.get("error", "")))
        fout = f.get("html", "")
        rn, fn = frame_norm(rout), frame_norm(fout)
        rtok = "ERR" if "error" in r else (
            "MARKER" if "\xfe" in rout else (
                "ERRBLOCK" if "error-block" in rout else "LITERAL"))
        ftok = "ERRBLOCK" if "error-block" in fout else (
            "TODO" if "TODO: module" in fout else (
                "STYLE" if "<style" in fout else "LITERAL"))
        surface = ("\xfe" in rout or "TODO: module" in fout
                   or "<style" in fout)
        if rn == fn:
            kind = "match"
        elif surface:
            kind = "surface"
        else:
            kind = "matching_divergence"
        counts[kind] += 1
        print(f"{kind:20s} {cid:38s} REF[{rtok:8s}] FTML[{ftok:8s}]"
              f" errs={len(f.get('errors', []))}")
    print("COUNTS", counts, "total", len(battery))


if __name__ == "__main__":
    main()
