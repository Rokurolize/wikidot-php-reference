#!/usr/bin/env python3
"""Three-way compare of eref shapes on the cached live probes."""
import json
from pathlib import Path
from compare import load, canonical, shape, body

cap = json.loads(Path("captures.json").read_text(encoding="utf-8"))
records = cap.values() if isinstance(cap, dict) else cap
ref = load("ref-probe-render-before.jsonl")
ftm = load("ftml-probe-dump.jsonl")

counts = {"all_three": 0, "ref_live": 0, "ftml_live": 0, "all_disagree": 0, "invalid": 0}
lines = []
for rec in records:
    cid = rec.get("id") or str(rec.get("fullname", "")).replace("muse-probe-r2link-eref-", "", 1)
    valid = bool(rec.get("saved_source_matches")) and bool(rec.get("stable"))
    if not valid:
        counts["invalid"] += 1
    live = rec.get("html") or rec.get("page_html") or rec.get("content") or ""
    sr = shape(body(ref.get(cid, {}), "ref"))
    sf = shape(body(ftm.get(cid, {}), "ftml"))
    sl = shape(live)
    if sr == sf == sl:
        tag = "all_three"; counts["all_three"] += 1
    elif sr == sl:
        tag = "ref_live"; counts["ref_live"] += 1
    elif sf == sl:
        tag = "ftml_live"; counts["ftml_live"] += 1
    else:
        tag = "all_disagree"; counts["all_disagree"] += 1
    lines.append(f"{cid:24s} {tag:12s} valid={valid} ref={json.dumps(sr)} ftml={json.dumps(sf)} live={json.dumps(sl)}")
    if tag != "all_three":
        lines.append(f"    LIVE RAW: {canonical(live)!r}")

lines.append(f"TOTAL {json.dumps(counts)}")
Path("compare-live.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
