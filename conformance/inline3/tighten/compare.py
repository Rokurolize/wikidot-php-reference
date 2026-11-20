#!/usr/bin/env python3
"""Compare reference render variants and the shared ftml dumper for the
R2-inline3 Tighten battery.

Two equivalence notions are reported.

  exact: byte-for-byte HTML. This is always low because the shared harness
         appends two trailing newlines to every render and spells line breaks
         <br /> where the dumper spells them <br>, and because the reference
         emits newlines between block tags the dumper does not.

  norm:  a FRAME NORMALIZER that removes only rendering-frame padding owned by
         earlier/later rules, not Tighten-layer output. It (a) strips leading
         and trailing whole-document whitespace (the harness's two appended
         newlines), (b) canonicalises <br /> to <br> (line-break spelling,
         routed as M70), and (c) collapses runs of whitespace BETWEEN tags to
         a single newline (inter-block padding, routed as M69). It deliberately
         does NOT collapse whitespace inside text nodes, so leading/trailing
         spaces inside spans and spaces exposed by empty-pair deletion remain
         visible as real disagreements for this rule to rule on.

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
    """The documented frame normalizer (see module docstring)."""
    s = (s or "").replace("<br />", "<br>")
    s = re.sub(r">\s+<", ">\n<", s)
    return s.strip()


def ws_collapse(s):
    """A looser normalizer used only as context: also folds in-text runs."""
    return re.sub(r"\s+", " ", norm(s))


def main():
    battery = [json.loads(l) for l in open(os.path.join(D, "battery.jsonl"), encoding="utf-8") if l.strip()]
    variants = sys.argv[1:] or ["before", "after"]
    ftml = load("ftml-dump.jsonl")
    lines = []
    for v in variants:
        rf = "ref-render-%s.jsonl" % v
        if not os.path.exists(os.path.join(D, rf)):
            continue
        ref = load(rf)
        exact = normc = wsc = botherr = 0
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
            wc = ws_collapse(ro) == ws_collapse(fo)
            exact += ex
            normc += nc
            wsc += wc
            if not nc:
                rows.append((cid, c["source"], ro, fo, norm(ro), norm(fo)))
        lines.append("VARIANT %s: total=%d exact_agree=%d frame_norm_agree=%d "
                     "intext_ws_agree=%d case_errors=%d" % (
                         v, len(battery), exact, normc, wsc, botherr))
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
    print(text[:6000])


if __name__ == "__main__":
    main()
