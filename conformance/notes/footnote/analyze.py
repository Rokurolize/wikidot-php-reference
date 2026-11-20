#!/usr/bin/env python3
"""Compare reference render vs ftml dump over the footnote battery, focused on
the footnoteref anchors the Footnote rule owns. The only normalization applied
is the known frame-level surface &#39; -> ' so genuine rule divergences stand out.
"""
import json, re, sys

FN = "/home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh-r2notes/conformance-refphp/notes/footnote"


def load(path):
    out = {}
    order = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            out[r["id"]] = r
            order.append(r["id"])
    return out, order


def anchors(s):
    return re.findall(r'<sup class="footnoteref">.*?</sup>', s, re.S)


def norm(s):
    return s.replace("&#39;", "'")


def main(refpath, ftmpath, report):
    before, order = load(refpath)
    ftml, _ = load(ftmpath)
    battery, border = load(FN + "/battery.jsonl")
    identical = 0
    mismatches = []
    with open(report, "w", encoding="utf-8") as rep:
        rep.write("Footnote rule differential: %s vs %s (Layout::Wikidot)\n" % (refpath.split("/")[-1], ftmpath.split("/")[-1]))
        rep.write("Normalization on every comparison: &#39; -> ' (known frame-level surface, candidate finding; not a reference bug).\n\n")
        for cid in border:
            if cid not in before or cid not in ftml:
                continue
            b = before[cid].get("output") or ""
            t = ftml[cid].get("html") or ""
            nb = [norm(x) for x in anchors(b)]
            nt = [norm(x) for x in anchors(t)]
            if nb == nt:
                identical += 1
                continue
            kind = "COUNT" if len(nb) != len(nt) else "SHAPE"
            mismatches.append(cid)
            rep.write("MISMATCH %s (%s): ref=%d ftml=%d\n" % (cid, kind, len(nb), len(nt)))
            for i in range(max(len(nb), len(nt))):
                rb = nb[i] if i < len(nb) else "<none>"
                rt = nt[i] if i < len(nt) else "<none>"
                if rb != rt:
                    rep.write("  ref [%d]: %s\n  ftm [%d]: %s\n" % (i, rb, i, rt))
        total = identical + len(mismatches)
        rep.write("\nSummary: %d/%d cases have identical footnoteref-anchor sequences after &#39; normalization; %d mismatched.\n" % (identical, total, len(mismatches)))
    print("identical=%d mismatched=%d (%s)" % (identical, len(mismatches), ",".join(mismatches)))


if __name__ == "__main__":
    ref = sys.argv[1] if len(sys.argv) > 1 else FN + "/ref-render-before.jsonl"
    ftm = sys.argv[2] if len(sys.argv) > 2 else FN + "/ftml-dump.jsonl"
    rep = sys.argv[3] if len(sys.argv) > 3 else FN + "/compare-report.txt"
    main(ref, ftm, rep)
