#!/usr/bin/env python3
"""Verify the REFCORR-next adjacent-paragraph framing pins.

Run from the clone root:
    python3 conformance/table/tableadv/verify_refcorr_next_framing.py

Checks, for each of the 8 witnesses:
  1. the batch render equals the retained expected render (byte regression);
  2. every pinned table-adjacent framing substring appears in the render
     after the repository canon (collapse >\\s+<, strip outer whitespace);
  3. for the five corpus witnesses, every pinned framing substring also
     appears in the cached live #page-content fragment under the same canon.

The three synthetic witnesses sit at Tableadv-stage sizes 73-78 bytes, i.e.
below the old 8192 split: they pin that the framing behavior is not a
large-page-only effect. The five corpus witnesses span stage sizes 3,714 to
73,534 bytes, including the three pages the coordinator's verifier sampled.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CASES = HERE / "refcorr-next-framing-cases.jsonl"
EXPECTED = HERE / "refcorr-next-framing-expected.json"
CAPTURES = HERE / "refcorr-next-framing-captures.json"
FRAMING = HERE / "refcorr-next-framing.json"


def canon(s):
    return re.sub(r">\s+<", "><", s.strip())


def main():
    cases = [json.loads(l) for l in CASES.read_text(encoding="utf-8").splitlines() if l.strip()]
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    captures = json.loads(CAPTURES.read_text(encoding="utf-8"))
    framing = json.loads(FRAMING.read_text(encoding="utf-8"))
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

    bad_expected, bad_render, bad_live = [], [], []
    for c in cases:
        cid = c["id"]
        r = renders.get(cid)
        if r is None or "error" in r:
            bad_expected.append((cid, "render error"))
            continue
        out = r["output"]
        if out.rstrip("\n") != expected[cid]["html"].rstrip("\n"):
            bad_expected.append((cid, "expected byte mismatch"))
        cr = canon(out)
        for a in framing[cid]["assert"]:
            if a not in cr:
                bad_render.append((cid, a))
        if c["kind"] == "corpus":
            cl = canon(captures[cid]["html"])
            for a in framing[cid]["assert"]:
                if a not in cl:
                    bad_live.append((cid, a))

    n = len(cases)
    print(f"REFCORR-next framing pins: {n} witnesses checked")
    print(f"  expected-render byte pins: {n - len(bad_expected)}/{n}  failures={bad_expected}")
    print(f"  render framing assertions: {n - len(bad_render)}/{n}  failures={bad_render}")
    print(f"  live framing assertions:   {len(captures) - len(bad_live)}/{len(captures)}  failures={bad_live}")
    return 0 if not (bad_expected or bad_render or bad_live) else 1


if __name__ == "__main__":
    sys.exit(main())
