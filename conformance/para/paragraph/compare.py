#!/usr/bin/env python3
"""Compare the paragraph battery across the reference (before/after), the
shared ftml dumper and the cached live probe captures.

Three normalizations are reported so no frame-level difference is mistaken for
a Paragraph-rule difference:

  raw    - exact bytes.
  N1     - frame join surface factored out: trailing document whitespace
           stripped, whitespace-only gaps between adjacent block tags removed,
           and the Newline/Horiz rules' `<br />`/`<hr />` spellings mapped to
           the pins' `<br>`/`<hr>`. Whitespace RUNS inside text are kept, so
           the routed tab-collapse question stays visible.
  N2     - N1 plus the Stage 2 purifyHtml whitespace-run collapse (any run of
           spaces/tabs in text becomes one space), used only to show what is
           left once that frame-level surface is also factored out.

A per-case report and the summary counts are written to compare-report.txt.
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    out = {}
    path = os.path.join(BASE, name)
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        out[rec["id"]] = rec.get("output", rec.get("html", rec.get("error")))
    return out


def n1(s):
    if not isinstance(s, str):
        return s
    s = s.strip()
    s = re.sub(r">\s*<", "><", s)
    s = s.replace("<br />", "<br>").replace("<hr />", "<hr>")
    return s


def n2(s):
    if not isinstance(s, str):
        return s
    s = n1(s)
    # Collapse whitespace runs only in text nodes, leaving tag interiors alone.
    return re.sub(r">([^<>]*)<", lambda m: ">" + re.sub(r"[ \t]+", " ", m.group(1)) + "<", s)


def n3(s):
    """N2 plus the live serving layer's `<br> ` versus the pins' `<br>\\n`
    tail surface, which belongs to the Newline/Tighten frame rules."""
    if not isinstance(s, str):
        return s
    return re.sub(r"(<br>)\s*", r"\1", n2(s))


def count_agree(a, b, ids, norm):
    return sum(1 for i in ids if i in a and i in b and norm(a[i]) == norm(b[i]))


def main():
    before = load(sys.argv[1] if len(sys.argv) > 1 else "ref-render-before.jsonl")
    after = load(sys.argv[2] if len(sys.argv) > 2 else "ref-render-after.jsonl")
    ftml = load("ftml-dump.jsonl")
    ids = [json.loads(l)["id"] for l in open(os.path.join(BASE, "battery.jsonl"), encoding="utf-8")]
    lines = []
    for label, norm in (("raw", lambda s: s), ("N1", n1), ("N2", n2)):
        lines.append(
            "%s: ref-before vs ftml %d/%d, ref-after vs ftml %d/%d, "
            "ref-before vs ref-after %d/%d"
            % (label,
               count_agree(before, ftml, ids, norm), len(ids),
               count_agree(after, ftml, ids, norm), len(ids),
               count_agree(before, after, ids, norm), len(ids)))
    lines.append("")
    for i in ids:
        if i not in after or i not in ftml:
            continue
        same1 = n1(after[i]) == n1(ftml[i])
        same2 = n2(after[i]) == n2(ftml[i])
        lines.append("%s N1=%s N2=%s" % (i, "agree" if same1 else "DIFF", "agree" if same2 else "DIFF"))
        if not same1:
            lines.append("  REF: %r" % after[i])
            lines.append("  DMP: %r" % ftml[i])
    text = "\n".join(lines) + "\n"
    open(os.path.join(BASE, "compare-report.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
