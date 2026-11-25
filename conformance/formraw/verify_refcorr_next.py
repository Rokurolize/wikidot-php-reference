#!/usr/bin/env python3
"""REFCORR-NEXT executable pins for the two m2 reference-side findings.

Run from anywhere:  python3 conformance/formraw/verify_refcorr_next.py
Checks that the corrected reference reproduces the retained live/ftml-shaped
outputs for all 19 angle-raw instances and all 8 freelink apostrophe witnesses.
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys

REF = pathlib.Path(__file__).resolve().parents[2]
PAGES = pathlib.Path("/home/roku/src/Rokurolize/scp-wiki-translation/corpus/en/pages")

SETS = [
    ("angle-raw entities",
     REF / "conformance/formraw/refcorr-next-angle-entity-cases.jsonl",
     REF / "conformance/formraw/refcorr-next-angle-entity-expected.json"),
    ("freelink apostrophe slug",
     REF / "conformance/link/freelink/refcorr-next-o5-slug-cases.jsonl",
     REF / "conformance/link/freelink/refcorr-next-o5-slug-expected.json"),
]


def render(cases):
    inp = "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases)
    p = subprocess.run(["php", "harness/batch.php", "render"], cwd=REF, input=inp,
                       text=True, capture_output=True, encoding="utf-8")
    if p.returncode or p.stderr:
        raise RuntimeError(f"harness failed: {p.returncode} {p.stderr[:500]}")
    return {r["id"]: r["output"].rstrip("\n") for r in map(json.loads, p.stdout.splitlines())}


def raw_spans(html):
    return re.findall(r'<span style="white-space: pre-wrap;">(.*?)</span>', html, re.S)


def check(name, cases_path, expected_path):
    cases = [json.loads(l) for l in cases_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    got = render(cases)
    bad = []
    for c in cases:
        cid = c["id"]
        exp = expected[cid]
        out = got.get(cid)
        if out != exp["expected_html"]:
            bad.append((cid, "output mismatch"))
            continue
        if hashlib.sha256(out.encode("utf-8")).hexdigest() != exp["expected_html_sha256"]:
            bad.append((cid, "sha mismatch"))
            continue
        if c["source"] != exp["source"]:
            bad.append((cid, "source mismatch"))
            continue
        if exp["evidence_kind"] == "cached-live-anchor" and ('href="' + exp["live_href"] + '"') not in out:
            bad.append((cid, "live href absent"))
        if exp["evidence_kind"] == "cached-live-raw-span":
            # The evidence string carries the cached live page's raw spans.
            live = json.loads(exp["evidence"].split("raw spans ", 1)[1])
            mine = raw_spans(out)
            if mine and not all(s in live for s in mine):
                bad.append((cid, "raw span not in cached live"))
    print(f"{name}: {len(cases) - len(bad)}/{len(cases)} pins OK")
    for cid, why in bad:
        print(f"  BAD {cid}: {why}")
    return bad


def main():
    bad = []
    for args in SETS:
        bad.extend(check(*args))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
