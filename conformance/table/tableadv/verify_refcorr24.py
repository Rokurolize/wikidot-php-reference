#!/usr/bin/env python3
"""Verify the REFCORR24 witness-family pins against the current checkout.

Run from the clone root:
    python3 conformance/table/tableadv/verify_refcorr24.py

Checks, for each of the 45 witnesses:
  1. the batch render equals the retained expected render (regression pin), and
  2. the batch render canonically agrees with the cached live page fragment
     (fidelity pin). canonical() is the conformance/table/compare_x.py rule:
     collapse whitespace between tags, then strip outer whitespace.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CASES = HERE / "refcorr24-cases.jsonl"
EXPECTED = HERE / "refcorr24-expected.json"
CAPTURES = HERE / "refcorr24-captures.json"


def load_jsonl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def canon(s):
    return re.sub(r">\s+<", "><", s.strip())


def main():
    cases = load_jsonl(CASES)
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    captures = json.loads(CAPTURES.read_text(encoding="utf-8"))
    stdin = "".join(json.dumps(c, separators=(",", ":")) + "\n" for c in cases)
    proc = subprocess.run(
        ["php", str(ROOT / "harness" / "batch.php"), "render"],
        input=stdin, capture_output=True, text=True, cwd=ROOT)
    if proc.returncode != 0:
        print("batch render failed:", proc.stderr[-2000:])
        return 1
    renders = {}
    for line in proc.stdout.splitlines():
        r = json.loads(line)
        renders[r["id"]] = r

    n = 0
    bad_expected = []
    bad_live = []
    for c in cases:
        wid = c["id"]
        r = renders.get(wid)
        if r is None or "error" in r:
            bad_expected.append((wid, "render error"))
            bad_live.append((wid, "render error"))
            continue
        out = r["output"]
        exp = expected[wid]["html"]
        if out.rstrip("\n") != exp.rstrip("\n"):
            bad_expected.append((wid, "expected byte mismatch"))
        if canon(out) != canon(captures[wid]["html"]):
            bad_live.append((wid, "live canonical mismatch"))
        n += 1

    print(f"REFCORR24 pins: {n} witnesses checked")
    print(f"  expected-render byte pins: {n - len(bad_expected)}/{n}  failures={bad_expected}")
    print(f"  live canonical fidelity:   {n - len(bad_live)}/{n}  failures={bad_live}")
    return 0 if not bad_expected and not bad_live else 1


if __name__ == "__main__":
    sys.exit(main())
