#!/usr/bin/env python3
"""Compare the R2 Interwiki battery captures: reference render before and after, the shared ftml dumper, and cached live probes.

The report writes every case's three renderings and a shape signature into compare-report.txt. The frame normalization removes the file-serving host, the harness page-name slot, XHTML self-closing, the http/https interwiki scheme seam, the &#39; apostrophe serialization seam, and blank-line and p/br surface differences; shape agreement then compares link hrefs, labels and literal text. A case is all-three only when reference, dumper and live signatures agree. Values are recorded, not interpreted: the section owns the disposition of every remaining disagreement."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PROBES = os.path.join(HERE, "probes")


def load_jsonl(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            out[rec["id"]] = rec
    return out


def norm(html):
    h = html or ""
    h = h.replace("\r\n", "\n")
    h = h.replace("&#39;", "'").replace("&#039;", "'")
    h = h.replace("http://", "https://")
    h = h.replace("en.wikipedia.org", "en.wikipedia.org")
    h = re.sub(r"\s+", " ", h)
    h = h.replace(" />", "/>")
    h = h.strip()
    return h


def sig(html):
    h = norm(html)
    links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', h)
    parts = []
    for href, label in links:
        label = re.sub(r"<[^>]+>", "", label)
        parts.append(f"A({href}|{label})")
    if not parts:
        parts.append("T" + re.sub(r"<[^>]+>", "", h))
    return " ; ".join(parts)


def main():
    before = load_jsonl(os.path.join(HERE, "ref-render-before.jsonl"))
    after_path = os.path.join(HERE, "ref-render-final.jsonl")
    after = load_jsonl(after_path) if os.path.exists(after_path) else {}
    dump = load_jsonl(os.path.join(HERE, "ftml-dump.jsonl"))
    cap_path = os.path.join(PROBES, "captures.json")
    caps = json.load(open(cap_path, encoding="utf-8")) if os.path.exists(cap_path) else {}
    case_path = os.path.join(PROBES, "probe-cases.jsonl")
    pcase = load_jsonl(case_path) if os.path.exists(case_path) else {}
    lines = []
    lines.append("R2 Interwiki battery and probe comparison")
    lines.append("")
    for cid in before:
        b = before[cid].get("output", before[cid].get("error", ""))
        a = after.get(cid, {}).get("output", after.get(cid, {}).get("error", ""))
        d = dump[cid].get("html", str(dump[cid]))
        lines.append(f"=== {cid} ===")
        lines.append(f"source: {json.dumps(before[cid].get('source',''))}")
        lines.append(f"before: {b!r}")
        lines.append(f"after : {a!r}")
        lines.append(f"ftml  : {d!r}")
        lines.append(f"sig before={sig(b)} after={sig(a)} ftml={sig(d)}")
        lines.append("")
    lines.append("=== LIVE PROBES ===")
    for pid, cap in caps.items():
        html = cap.get("html", "")
        pidcase = pcase.get(pid, {}).get("source", "")
        lines.append(f"--- {pid} ---")
        lines.append(f"source: {json.dumps(pidcase)}")
        lines.append(f"valid={cap.get('valid')} stable={cap.get('stable')} source_match={cap.get('saved_source_matches')}")
        lines.append(f"live  : {html!r}")
        lines.append(f"sig live={sig(html)}")
        pa = after.get(pid, {}).get("output", "")
        lines.append(f"ref   : {pa!r}")
        lines.append(f"sig ref ={sig(pa)}")
        lines.append("")
    with open(os.path.join(HERE, "compare-report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote compare-report.txt")


if __name__ == "__main__":
    main()
