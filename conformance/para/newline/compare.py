#!/usr/bin/env python3
"""Compare reference render and ftml dumper over the same battery using two documented normalizations.

Exact: byte-for-byte HTML. Norm: factor out frame-level surface that other rules own:
  (a) <br /> -> <br> (break spelling; the surface this section settles with live),
  (b) collapse any run of whitespace between a closing '>' and an opening '<' to
      a single '\n' where both sides have a tag boundary (inter-block newline),
  (c) strip leading/trailing whitespace of the whole document.
Writes a per-case table and summary counts to compare-report.txt (and prints it).
"""
import json, os, re, sys

D = os.path.dirname(os.path.abspath(__file__))
def load(name):
    out = {}
    with open(os.path.join(D, name), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line: continue
            r = json.loads(line)
            out[r["id"]] = r
    return out

def norm(s):
    s = s.replace("<br />", "<br>")
    # collapse whitespace between tags (frame inter-block newlines/padding)
    s = re.sub(r">\s+<", ">\n<", s)
    s = s.strip()
    return s

def main():
    battery = [json.loads(l) for l in open(os.path.join(D, "battery.jsonl"), encoding="utf-8") if l.strip()]
    variants = sys.argv[1:] or ["before"]
    tables = {}
    for v in variants:
        rf = "ref-render-%s.jsonl" % v
        if not os.path.exists(os.path.join(D, rf)):
            continue
        ref = load(rf); ftml = load("ftml-dump.jsonl")
        exact = normc = both_err = 0
        rows = []
        for c in battery:
            cid = c["id"]
            ro = ref.get(cid, {}).get("output")
            re_ = ref.get(cid, {}).get("error")
            fo = ftml.get(cid, {}).get("html")
            fe = ftml.get(cid, {}).get("errors")
            if re_ or (fe and any(fe)):
                both_err += 1
            ex = (ro == fo)
            nc = (norm(ro or "") == norm(fo or ""))
            exact += ex; normc += nc
            if not nc:
                rows.append((cid, c["source"], ro, fo, norm(ro or ""), norm(fo or "")))
        tables[v] = (exact, normc, both_err, len(battery), rows)
    lines = []
    for v, (exact, normc, both_err, total, rows) in tables.items():
        lines.append("VARIANT %s: total=%d exact_agree=%d normalized_agree=%d case_errors=%d" % (v, total, exact, normc, both_err))
        for cid, src, ro, fo, nr, nf in rows:
            lines.append("  DIFF %s" % cid)
            lines.append("    src=%s" % json.dumps(src))
            lines.append("    ref=%s" % json.dumps(ro))
            lines.append("    ftm=%s" % json.dumps(fo))
            lines.append("    nrf=%s" % json.dumps(nr))
            lines.append("    nft=%s" % json.dumps(nf))
        lines.append("")
    text = "\n".join(lines) + "\n"
    open(os.path.join(D, "compare-report.txt"), "w", encoding="utf-8").write(text)
    print(text)

if __name__ == "__main__":
    main()
