#!/usr/bin/env python3
"""Adjudicate reference and ftml against valid saved-page live captures."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_jsonl(name):
    out = {}
    with open(ROOT / name, encoding="utf-8") as handle:
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
    return text.strip("\n")


captures = json.load(open(ROOT / "captures.json", encoding="utf-8"))
ref = load_jsonl("ref-probe-render.jsonl")
ftml = load_jsonl("ftml-probe-dump.jsonl")
valid = {k: v for k, v in captures.items() if v.get("valid") and v.get("stable")
         and v.get("saved_source_matches")}
ok_ref = ok_ftml = 0
diffs = []
for cid, cap in sorted(valid.items()):
    live = cap.get("html", "")
    r = ref.get(cid, {}).get("output", "ERR:" + ref.get(cid, {}).get("error", ""))
    f = ftml.get(cid, {}).get("html", "MISSING")
    if shape(r) == shape(live):
        ok_ref += 1
    if shape(f) == shape(live):
        ok_ftml += 1
    if shape(r) != shape(live):
        diffs.append((cid, r, f, live))
print("probes=%d valid=%d ref_live_match=%d ftml_live_match=%d ref_disagreements=%d"
      % (len(captures), len(valid), ok_ref, ok_ftml, len(diffs)))
for cid, r, f, live in diffs:
    print("=== %s\n  ref: %r\n  ftm: %r\n  live:%r" % (cid, r[:300], f[:300], live[:300]))
