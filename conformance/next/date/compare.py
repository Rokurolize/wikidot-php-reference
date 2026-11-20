#!/usr/bin/env python3
"""Side-by-side comparison for the Date rule's three evidence sides.

Loads the battery and the cached saved-page probes, normalizes only
frame-level surface (br spelling, empty paragraph wrappers, a stray space
before a tag close, and trailing newlines), and prints per-case reference,
ftml and live views. Use --summary for counts instead of the case view.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_jsonl(name):
    rows = []
    with open(os.path.join(HERE, name), encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return {row["id"]: row for row in rows}


def load_json(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def frame_norm(text):
    text = (text or "").replace("<br />", "<br>")
    text = re.sub(r"\s+>", ">", text)
    text = re.sub(r"<p>\s*</p>", "", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    return text.strip()


def visible(text):
    return re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", frame_norm(text)))


def main():
    battery = load_jsonl("battery.jsonl")
    ref = load_jsonl("ref-render-after.jsonl")
    ftml = load_jsonl("ftml-dump.jsonl")
    tokens = load_jsonl("ref-tokens-after.jsonl")
    probes = load_jsonl("probe-cases.jsonl")
    probe_ref = load_jsonl("ref-probe-render-after.jsonl")
    probe_ftml = load_jsonl("ftml-probe-dump.jsonl")
    captures = load_json("captures.json")
    summary_only = "--summary" in sys.argv

    counts = {"battery_agree": 0, "battery_surface": 0, "battery_substantive": 0}
    for cid, case in battery.items():
        r = ref.get(cid, {}).get("output", "")
        f = ftml.get(cid, {}).get("html", "")
        if frame_norm(r) == frame_norm(f):
            counts["battery_agree"] += 1
        elif visible(r) == visible(f):
            counts["battery_surface"] += 1
        else:
            counts["battery_substantive"] += 1
        if not summary_only:
            print("## %s source=%s" % (cid, case["source"]))
            print("  ref:  %s" % r)
            print("  ftml: %s" % f)
            print("  tok:  %s" % tokens.get(cid, {}).get("output", ""))

    live_counts = {"valid": 0, "all_three": 0, "ref_live": 0, "ftml_live": 0, "none": 0}
    disagreements = []
    for pid, cap in captures.items():
        if not cap.get("valid"):
            continue
        live_counts["valid"] += 1
        r = probe_ref.get(pid, {}).get("output", "")
        f = probe_ftml.get(pid, {}).get("html", "")
        lv = cap.get("html", "")
        nr, nf, nl = frame_norm(r), frame_norm(f), frame_norm(lv)
        if not summary_only:
            print("## LIVE %s source=%s" % (pid, probes.get(pid, {}).get("source", "")))
            print("  ref:  %s" % r)
            print("  ftml: %s" % f)
            print("  live: %s" % lv)
        if nr == nf == nl:
            live_counts["all_three"] += 1
        elif nr == nl:
            live_counts["ref_live"] += 1
            disagreements.append(pid)
        elif nf == nl:
            live_counts["ftml_live"] += 1
            disagreements.append(pid)
        else:
            live_counts["none"] += 1
            disagreements.append(pid)

    print("BATTERY %s total=%d" % (json.dumps(counts, sort_keys=True), len(battery)))
    print("LIVE %s" % json.dumps(live_counts, sort_keys=True))
    if disagreements:
        print("LIVE_DISAGREEMENTS %s" % ", ".join(disagreements))


if __name__ == "__main__":
    main()
