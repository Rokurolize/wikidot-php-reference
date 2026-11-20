#!/usr/bin/env python3
"""Compare reference render variants and the ftml dumper over the Email battery.

Exact is byte-for-byte HTML. Norm strips whole-document leading/trailing frame
whitespace and collapses runs of whitespace between tags to one newline, so that
frame-level padding owned by later rules does not hide Email-layer differences.
Writes a per-case table and summary counts to compare-report.txt.
"""
import json
import os
import re
import sys

D = os.path.dirname(os.path.abspath(__file__))


def load(name):
    out = {}
    with open(os.path.join(D, name), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            out[r["id"]] = r
    return out


def norm(s):
    s = re.sub(r">\s+<", ">\n<", s or "")
    return s.strip()


def main():
    battery = [json.loads(l) for l in open(os.path.join(D, "battery.jsonl"), encoding="utf-8") if l.strip()]
    variants = sys.argv[1:] or ["before"]
    ftml = load("ftml-dump.jsonl")
    lines = []
    for v in variants:
        rf = "ref-render-%s.jsonl" % v
        if not os.path.exists(os.path.join(D, rf)):
            continue
        ref = load(rf)
        exact = normc = botherr = 0
        rows = []
        for c in battery:
            cid = c["id"]
            ro = ref.get(cid, {}).get("output")
            re_ = ref.get(cid, {}).get("error")
            fo = ftml.get(cid, {}).get("html")
            fe = ftml.get(cid, {}).get("errors")
            if re_ or (fe and any(fe)):
                botherr += 1
            ex = ro == fo
            nc = norm(ro) == norm(fo)
            exact += ex
            normc += nc
            if not nc:
                rows.append((cid, c["source"], ro, fo, norm(ro), norm(fo)))
        lines.append("VARIANT %s: total=%d exact_agree=%d normalized_agree=%d case_errors=%d" % (
            v, len(battery), exact, normc, botherr))
        for cid, src, ro, fo, nr, nf in rows:
            lines.extend([
                "  DIFF %s" % cid,
                "    src=%s" % json.dumps(src, ensure_ascii=False),
                "    ref=%s" % json.dumps(ro, ensure_ascii=False),
                "    ftm=%s" % json.dumps(fo, ensure_ascii=False),
                "    nrf=%s" % json.dumps(nr, ensure_ascii=False),
                "    nft=%s" % json.dumps(nf, ensure_ascii=False),
            ])
        lines.append("")
    text = "\n".join(lines) + "\n"
    with open(os.path.join(D, "compare-report.txt"), "w", encoding="utf-8") as fh:
        fh.write(text)
    print(text)


if __name__ == "__main__":
    main()
