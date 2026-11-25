#!/usr/bin/env python3
"""Verify the REFCORR23 two-documents-one-process statics pins."""
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
pins = json.loads((ROOT / "conformance/frame/refcorr23-statics-pins.json").read_text())
failures = []
for scenario, expected in sorted(pins["scenarios"].items()):
    got = {}
    for mode in ("solo", "pair"):
        proc = subprocess.run(
            ["php", "harness/statics-probe.php", scenario, mode],
            cwd=ROOT, text=True, capture_output=True,
        )
        if proc.returncode != 0:
            failures.append(f"{scenario}:{mode}: driver rc={proc.returncode}: {proc.stderr}")
            break
        try:
            got[mode] = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            failures.append(f"{scenario}:{mode}: invalid JSON: {exc}")
            break
    if len(got) != 2:
        continue
    solo = got["solo"]["b_output"]
    pair = got["pair"]["b_output"]
    digest = hashlib.sha256(solo.encode("utf-8")).hexdigest()
    if pair != solo:
        failures.append(f"{scenario}: pair output differs from solo output")
    if "tokens_pair_equals_solo" in expected:
        st = got["solo"]["b_facts"].get("tokens_json")
        pt = got["pair"]["b_facts"].get("tokens_json")
        if st is None or pt is None or st != pt:
            failures.append(f"{scenario}: pair token wire differs from solo token wire")
    if digest != expected["solo_sha256"]:
        failures.append(f"{scenario}: solo digest {digest} != pinned {expected['solo_sha256']}")
    if not expected["pair_equals_solo"] or ("tokens_pair_equals_solo" in expected and not expected["tokens_pair_equals_solo"]):
        failures.append(f"{scenario}: pin record itself is not green")
if failures:
    print("REFCORR23 statics pin failures:", file=sys.stderr)
    for failure in failures:
        print("  " + failure, file=sys.stderr)
    sys.exit(1)
print(f"REFCORR23 statics pins green: {len(pins['scenarios'])} scenarios")
