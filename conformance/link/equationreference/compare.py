#!/usr/bin/env python3
"""Compare reference and ftml eref renderings over a battery or probe set.

Usage: compare.py REF_RENDER.jsonl FTML_DUMP.jsonl [REPORT.txt]

The report separates raw HTML agreement from agreement on the eref shape
(anchor targets and displayed numbers, plus leftover literal eref syntax),
because the harness leaves paragraph/newline padding and the reference emits
a literal single quote where ftml/live serialize it as &#39;.  Those are
frame-level surfaces owned by later rules, not Equationreference divergences.
"""
import json
import re
import sys
from pathlib import Path

ANCHOR = re.compile(r'<a class="eref"[^>]*?>([^<]*)</a>')
TARGET = re.compile(r"scrollToReference\('equation-([^']*)'\)")


def load(path):
    return {r["id"]: r for r in (json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip())}


def canonical(html):
    h = html.replace("&#39;", "'").replace("&#039;", "'")
    h = h.replace("<br />", "<br>").replace("<br/>", "<br>")
    h = re.sub(r"\n+$", "", h)
    return h


def shape(html):
    h = canonical(html)
    targets = TARGET.findall(h)
    numbers = ANCHOR.findall(h)
    anchors = list(zip(targets, numbers)) if len(targets) == len(numbers) else (targets, numbers)
    literal = h.count("[[eref")
    return {"anchors": anchors, "literal_eref": literal}


def body(rec, side):
    if side == "ref":
        return rec.get("output", rec.get("error", ""))
    return rec.get("html", rec.get("error", ""))


def main():
    ref = load(sys.argv[1])
    ftm = load(sys.argv[2])
    report = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    lines = []
    raw = shape_agree = canonical_agree = substantive = 0
    disagreements = []
    for cid in sorted(set(ref) & set(ftm), key=lambda x: (int(x[1:]) if x[1:].isdigit() else x)):
        r, f = body(ref[cid], "ref"), body(ftm[cid], "ftml")
        sr, sf = shape(r), shape(f)
        exact = r == f
        canon = canonical(r) == canonical(f)
        same = sr == sf
        raw += exact
        canonical_agree += canon
        if same:
            shape_agree += 1
        else:
            substantive += 1
            disagreements.append((cid, sr, sf, r, f))
        lines.append(f"{cid}\traw={int(exact)}\tcanon={int(canon)}\tshape={int(same)}\tref={json.dumps(sr)}\tftml={json.dumps(sf)}")
    lines.append(f"TOTAL cases={len(set(ref)&set(ftm))} raw={raw} canonical={canonical_agree} shape={shape_agree} substantive={substantive}")
    for cid, sr, sf, r, f in disagreements:
        lines.append(f"DISAGREE {cid}\n  ref shape={json.dumps(sr)}\n  ftml shape={json.dumps(sf)}\n  ref html={r!r}\n  ftml html={f!r}")
    out = "\n".join(lines) + "\n"
    if report:
        report.write_text(out, encoding="utf-8")
        print(f"wrote {report}: raw={raw} canonical={canonical_agree} shape={shape_agree} substantive={substantive}")
    else:
        print(out)


if __name__ == "__main__":
    main()
