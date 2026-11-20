#!/usr/bin/env python3
"""Three-way comparison for the R2 Deflist battery and live probes.

Writes compare-report.txt for the battery (raw and canonical reference-versus-ftml
before and after correction, plus the changed-case list) and probe-compare.txt
for the three-way live/reference/ftml comparison on the double-fetched saved
pages. Canonicalization only removes known frame-level surfaces owned by other
rules: <br /> spelling, entity quoting, per-render bibcite id suffixes, and
inter-element whitespace that libtidy and the ftml serializer insert
differently. No deflist tag or text is removed by it.
"""
import json
import re
import os

BASE = os.path.dirname(os.path.abspath(__file__))


def load(path, key):
    out = {}
    with open(os.path.join(BASE, path), encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            out[row["id"]] = row[key]
    return out


def canon(s):
    s = s or ""
    s = s.replace("<br />", "<br>")
    s = s.replace("&#39;", "'").replace("&#039;", "'")
    s = re.sub(r'id="bibcite-(\d+)-[0-9a-f]+"', r'id="bibcite-\1"', s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def tagshape(s):
    tags = re.findall(r"</?(?:dl|dt|dd)\b[^>]*>", s or "")
    return " ".join(tags)


def battery_report():
    before = load("ref-render-before.jsonl", "output")
    after = load("ref-render-final.jsonl", "output")
    ftml = load("ftml-dump.jsonl", "html")
    order = [json.loads(l)["id"] for l in open(os.path.join(BASE, "battery.jsonl"), encoding="utf-8") if l.strip()]
    lines = []
    raw_b = sum(before.get(c) == ftml.get(c) for c in order)
    raw_a = sum(after.get(c) == ftml.get(c) for c in order)
    can_b = sum(canon(before.get(c)) == canon(ftml.get(c)) for c in order)
    can_a = sum(canon(after.get(c)) == canon(ftml.get(c)) for c in order)
    lines.append(f"battery cases: {len(order)}")
    lines.append(f"raw exact reference/ftml: before {raw_b}/{len(order)}, after {raw_a}/{len(order)}")
    lines.append(f"canonical reference/ftml: before {can_b}/{len(order)}, after {can_a}/{len(order)}")
    changed = [c for c in order if before.get(c) != after.get(c)]
    lines.append(f"render cases changed by the correction: {len(changed)}/{len(order)}")
    lines.append("changed ids: " + ", ".join(changed))
    lines.append("")
    lines.append("per-case after-correction comparison (raw equality):")
    for cid in order:
        eq = after.get(cid) == ftml.get(cid)
        ceq = canon(after.get(cid)) == canon(ftml.get(cid))
        lines.append(f"{'OK  ' if eq else 'DIFF'} {cid:36s} canon={'OK' if ceq else 'DIFF'} "
                     f"shape_ref={tagshape(after.get(cid))} shape_ftml={tagshape(ftml.get(cid))}")
        if not eq and not ceq:
            lines.append("   REF: " + repr(after.get(cid))[:400])
            lines.append("   FTL: " + repr(ftml.get(cid))[:400])
    with open(os.path.join(BASE, "compare-report.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return len(order), raw_b, raw_a, can_b, can_a, len(changed)


def probe_report():
    caps = json.load(open(os.path.join(BASE, "probe-captures.json"), encoding="utf-8"))
    ref = load("probe-ref-final.jsonl", "output")
    ftml = load("probe-ftml-dump.jsonl", "html")
    lines = []
    counts = {"all3": 0, "live_ref": 0, "live_ftml": 0, "ref_ftml": 0, "all_diff": 0}
    for cid, cap in caps.items():
        live = cap.get("html") or ""
        rf = ref.get(cid) or ""
        ff = ftml.get(cid) or ""
        valid = cap.get("valid") and cap.get("stable") and cap.get("saved_source_matches")
        lc, rc, fc = canon(live), canon(rf), canon(ff)
        if lc == rc == fc:
            key = "all3"
        elif lc == rc:
            key = "live_ref"
        elif lc == fc:
            key = "live_ftml"
        elif rc == fc:
            key = "ref_ftml"
        else:
            key = "all_diff"
        counts[key] += 1
        lines.append(f"{cid:26s} valid={valid} {key}")
        lines.append("   LIVE: " + repr(live)[:340])
        lines.append("   REF : " + repr(rf)[:340])
        lines.append("   FTL : " + repr(ff)[:340])
    lines.append("")
    lines.append("canonical three-way counts: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    lines.append(f"stable, source-matching, valid captures: {sum(1 for c in caps.values() if c.get('valid') and c.get('stable') and c.get('saved_source_matches'))}/{len(caps)}")
    with open(os.path.join(BASE, "probe-compare.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return counts


if __name__ == "__main__":
    stats = battery_report()
    pstats = probe_report()
    print("battery:", stats)
    print("probes:", pstats)
