#!/usr/bin/env python3
"""Compare cached live captures, corrected/pre-correction reference and the
ftml dumper over the paragraph owner's 26 saved-page probes.

Live HTML is passed through the campaign-standard wikidot-probe `norm()`
mask before comparison. The same N1/N2 frame normalizations as the battery
comparator are used so block-join whitespace and the Stage 2 whitespace-run
collapse do not masquerade as Paragraph-rule differences.
"""
import importlib.machinery
import importlib.util
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(BASE, "..")))
from compare import n1, n2  # noqa: E402

loader = importlib.machinery.SourceFileLoader(
    "wikidot_probe", "/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe")
spec = importlib.util.spec_from_loader("wikidot_probe", loader)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def load(name):
    out = {}
    for line in open(os.path.join(BASE, name), encoding="utf-8"):
        rec = json.loads(line)
        out[rec["id"]] = rec.get("output", rec.get("html", rec.get("error")))
    return out


def main():
    mapping = json.load(open(os.path.join(BASE, "probe-map.json"), encoding="utf-8"))
    caps = json.load(open(os.path.join(BASE, "captures.json"), encoding="utf-8"))
    before = load("ref-probe-render-before.jsonl")
    after = load("ref-probe-render-after.jsonl")
    ftml = load("ftml-probe-dump.jsonl")
    lines = []
    counts = {"valid": 0, "stable": 0, "match": 0, "all3": 0,
              "ref_live": 0, "ftml_live": 0, "ref_ftml": 0, "total": 0}
    for cid, info in mapping.items():
        rec = caps.get(cid, {})
        live = probe.norm(rec.get("html", "")) if rec.get("html") else ""
        b = before.get(cid, "")
        a = after.get(cid, "")
        f = ftml.get(cid, "")
        ok = all(rec.get(k) for k in ("valid", "stable", "saved_source_matches"))
        counts["valid"] += bool(rec.get("valid"))
        counts["stable"] += bool(rec.get("stable"))
        counts["match"] += bool(rec.get("saved_source_matches"))
        counts["total"] += 1
        s1 = n1(a) == n1(f) == n1(live)
        s2 = n1(a) == n1(f)
        s3 = n1(f) == n1(live)
        s4 = n1(a) == n1(live)
        counts["all3"] += bool(s1 and ok)
        counts["ref_ftml"] += bool(s2)
        counts["ftml_live"] += bool(s3)
        counts["ref_live"] += bool(s4)
        lines.append("%s %s fullname=%s valid=%s stable=%s match=%s all3=%s ref_ftml=%s ftml_live=%s ref_live=%s"
                     % (cid, "OK" if ok else "BAD", info.get("fullname"),
                        rec.get("valid"), rec.get("stable"),
                        rec.get("saved_source_matches"), s1, s2, s3, s4))
        lines.append("  SRC  : %r" % info.get("source"))
        lines.append("  LIVE : %r" % live)
        lines.append("  REF  : %r" % a)
        lines.append("  FTML : %r" % f)
        lines.append("  BEF  : %r" % b)
    lines.insert(0, json.dumps(counts))
    text = "\n".join(lines) + "\n"
    open(os.path.join(BASE, "compare-probes-report.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
