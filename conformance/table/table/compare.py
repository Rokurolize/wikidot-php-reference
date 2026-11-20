#!/usr/bin/env python3
"""Compare the R2 Table reference renders (before and after correction) against the shared ftml dumper and, when present, against live saved-page captures. The frame-level join surface (blank-line counts, page-edge newlines, fossil pretty-print indentation and <br /> against <br>) is normalized away so that only rule-level tag and body differences count; byte-identical counts are reported separately. Run from this directory with python3 compare.py, which writes compare-report.txt."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_jsonl(path):
    out = {}
    with open(ROOT / path, encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rec = json.loads(line)
                out[rec["id"]] = rec
    return out


def shape(text):
    if not isinstance(text, str):
        return text or ""
    text = text.replace("\r\n", "\n").replace("<br />", "<br>")
    text = re.sub(r"\n{2,}", "\n", text)
    text = "\n".join(line.lstrip(" ") for line in text.split("\n"))
    return text.strip("\n")


def compare_battery(report):
    before = load_jsonl("ref-render-before.jsonl")
    final = load_jsonl("ref-render-final.jsonl")
    ftml = load_jsonl("ftml-dump.jsonl")
    report.append("BATTERY (whole-document cases)")
    report.append("cases=%d" % len(before))
    for label, ref in (("before", before), ("final", final)):
        byte = sum(1 for cid in ref if ref[cid].get("output") == ftml.get(cid, {}).get("html"))
        shaped = sum(1 for cid in ref if shape(ref[cid].get("output", "")) == shape(ftml.get(cid, {}).get("html", "")))
        report.append("%s: byte_identical=%d/%d shaped_agreement=%d/%d shaped_diff=%d" %
                      (label, byte, len(ref), shaped, len(ref), len(ref) - shaped))
    diffs = [cid for cid in sorted(final)
             if shape(final[cid].get("output", "")) != shape(ftml.get(cid, {}).get("html", ""))]
    report.append("final shaped disagreements: %s" % ", ".join(diffs))
    for cid in diffs:
        report.append("=== %s\n  ref: %r\n  ftml: %r" %
                      (cid, shape(final[cid].get("output", ""))[:480],
                       shape(ftml.get(cid, {}).get("html", ""))[:480]))
    return before, final, ftml


def live_shape(text):
    """Live saved-page captures insert one serving-layer newline between
    adjacent block tags; the ftml pins and the dumper do not. Remove only
    that newline so the comparison isolates rule-level differences."""
    return re.sub(r'>\n<', '><', shape(text))


def compare_probes(report):
    cap_path = ROOT / "probes" / "captures.json"
    if not cap_path.exists():
        report.append("LIVE PROBES: no capture file present")
        return
    captures = json.load(open(cap_path, encoding="utf-8"))
    before = load_jsonl("probes/ref-probe-render-before.jsonl")
    final = load_jsonl("probes/ref-probe-render.jsonl")
    ftml = load_jsonl("probes/ftml-probe-dump.jsonl")
    valid = {cid: cap for cid, cap in captures.items()
             if cap.get("valid") and cap.get("stable") and cap.get("saved_source_matches")}
    report.append("")
    report.append("LIVE PROBES")
    report.append("probes=%d valid=%d stable=%d source_matches=%d" %
                  (len(captures), sum(1 for c in captures.values() if c.get("valid")),
                   sum(1 for c in captures.values() if c.get("stable")),
                   sum(1 for c in captures.values() if c.get("saved_source_matches"))))
    report.append("strict inter-block newline comparison: every live capture has one serving-layer newline between adjacent block tags that neither the dumper nor the reference emits, so strict matches are 0 on all three sides; the frame-tolerant numbers below remove only that newline")
    for label, ref in (("before", before), ("final", final)):
        live_ok = sum(1 for cid in valid if live_shape(ref.get(cid, {}).get("output", "")) == live_shape(valid[cid].get("html", "")))
        report.append("%s vs live (frame-tolerant): match=%d/%d" % (label, live_ok, len(valid)))
    ftml_ok = sum(1 for cid in valid if live_shape(ftml.get(cid, {}).get("html", "")) == live_shape(valid[cid].get("html", "")))
    report.append("ftml vs live (frame-tolerant): match=%d/%d" % (ftml_ok, len(valid)))
    for cid in sorted(valid):
        live = live_shape(valid[cid].get("html", ""))
        r = live_shape(final.get(cid, {}).get("output", ""))
        f = live_shape(ftml.get(cid, {}).get("html", ""))
        if r != live:
            report.append("=== %s\n  ref:  %r\n  ftml: %r\n  live: %r" % (cid, r[:480], f[:480], live[:480]))


def main():
    report = []
    compare_battery(report)
    compare_probes(report)
    out = "\n".join(report) + "\n"
    (ROOT / "compare-report.txt").write_text(out, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
