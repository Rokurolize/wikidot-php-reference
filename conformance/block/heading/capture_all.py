#!/usr/bin/env python3
# Orchestrate the standard wikidot-probe capture CLI one page at a time so a
# transient 503 cannot discard an already-completed batch. All fetching,
# double-fetch stability checking and saved-source verification is done by the
# CLI itself; this script only retries whole CLI invocations and merges their
# per-page output files. No probe logic is reimplemented here.
import json
import os
import subprocess
import time

BASE = "/home/roku/.agents/skills/wikidot-py-operations/scripts"
PY = f"{BASE}/wikidot-python"
PROBE = f"{BASE}/wikidot-probe"
HERE = os.path.dirname(os.path.abspath(__file__))

mapping = json.load(open(os.path.join(HERE, "probe-map.json"), encoding="utf-8"))
out_path = os.path.join(HERE, "captures.json")
merged = json.load(open(out_path, encoding="utf-8")) if os.path.exists(out_path) else {}
log = open(os.path.join(HERE, "capture-retry.log"), "a", encoding="utf-8")

for cid, entry in mapping.items():
    if cid in merged and merged[cid].get("valid"):
        log.write(f"{cid}: already captured, skipping\n")
        continue
    one_map = os.path.join(HERE, ".one-map.json")
    one_out = os.path.join(HERE, ".one-capture.json")
    with open(one_map, "w", encoding="utf-8") as fh:
        json.dump({cid: entry}, fh, ensure_ascii=False)
    if os.path.exists(one_out):
        os.remove(one_out)
    for attempt in range(1, 9):
        try:
            res = subprocess.run(
                [PY, PROBE, "capture", "--site", "sandbox-for-codex",
                 "--map", one_map, "--out", one_out, "--pace", "1.0"],
                cwd=HERE, capture_output=True, text=True, timeout=120,
            )
        except subprocess.TimeoutExpired:
            log.write(f"{cid} attempt {attempt}: timeout\n")
            log.flush()
            time.sleep(8)
            continue
        if os.path.exists(one_out):
            rec = json.load(open(one_out, encoding="utf-8"))
            got = rec.get(cid, {})
            if got.get("valid"):
                merged[cid] = got
                log.write(f"{cid}: captured on attempt {attempt}\n")
                log.flush()
                break
            log.write(f"{cid} attempt {attempt}: invalid record {got}\n")
        else:
            err = res.stderr.strip().splitlines()
            last = err[-1] if err else "(no stderr)"
            log.write(f"{cid} attempt {attempt}: rc={res.returncode} {last}\n")
        log.flush()
        time.sleep(8)
    else:
        log.write(f"{cid}: GAVE UP after 8 attempts\n")
        log.flush()
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(merged, fh, indent=1, ensure_ascii=False)

log.write(f"DONE: {len(merged)}/{len(mapping)} valid captures\n")
log.close()
print(f"captured {len(merged)}/{len(mapping)}")
