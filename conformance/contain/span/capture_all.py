#!/usr/bin/env python3
"""Orchestrate whole wikidot-probe capture CLI runs, one page at a time.

The sandbox intermittently answers HTTP 503 and the standard capture CLI
aborts on the first error without writing its output. This script performs no
fetching and no verification itself: for each probe page it writes a
single-entry map, invokes the unmodified wikidot-probe capture CLI, and
retries the whole CLI run until that page's capture JSON lands. It then merges
the per-page captures into captures.json in map order. Every stable,
saved_source_matches and valid flag is computed by the standard CLI.
"""
import json
import os
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
CLI = "/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-python"
PROBE = "/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe"
MAP = os.path.join(BASE, sys.argv[1] if len(sys.argv) > 1 else "probe-map.json")
OUT = os.path.join(BASE, sys.argv[2] if len(sys.argv) > 2 else "captures.json")
LOGNAME = sys.argv[3] if len(sys.argv) > 3 else "capture-one.log"

mapping = json.load(open(MAP, encoding="utf-8"))
captures = {}
for case_id, value in mapping.items():
    one = os.path.join(BASE, ".one-map.json")
    one_out = os.path.join(BASE, ".one-capture.json")
    json.dump({case_id: value}, open(one, "w", encoding="utf-8"))
    for attempt in range(1, 13):
        try:
            if os.path.exists(one_out):
                os.remove(one_out)
            with open(os.path.join(BASE, LOGNAME), "a", encoding="utf-8") as log:
                log.write("=== %s attempt %d ===\n" % (case_id, attempt))
                rc = subprocess.call(
                    [CLI, PROBE, "capture", "--site", "sandbox-for-codex",
                     "--map", one, "--out", one_out],
                    stdout=log, stderr=subprocess.STDOUT, timeout=180)
            if rc == 0 and os.path.exists(one_out):
                rec = json.load(open(one_out, encoding="utf-8"))
                captures.update(rec)
                print("%s captured (attempt %d): valid=%s" % (
                    case_id, attempt, rec[case_id].get("valid")), flush=True)
                break
            print("%s attempt %d rc=%s, retrying" % (case_id, attempt, rc), flush=True)
        except Exception as exc:  # noqa: BLE001 - retry any CLI/transport failure
            print("%s attempt %d error=%r, retrying" % (case_id, attempt, exc), flush=True)
        time.sleep(3)
    else:
        print("%s FAILED after 12 attempts" % case_id, flush=True)
        sys.exit(2)

json.dump(captures, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote %d captures to %s" % (len(captures), OUT))
