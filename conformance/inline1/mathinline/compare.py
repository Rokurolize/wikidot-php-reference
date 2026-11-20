#!/usr/bin/env python3
"""Three-side comparison report for the R2-inline1 Mathinline stage.

Loads the battery, the reference before/after render and token captures (plus
the supplementary UTF-8 token recovery where the harness json_encode refuses
placeholder bytes), the shared ftml dumper output and the cached live probes,
then writes compare-report.txt. No side is silently normalized: the serving
surface (LaTeX PNG generation vs the harness no-op stub) and frame-level
whitespace are reported separately from the parse/token shape.
"""
import html as htmlmod
import json
import os
import re

D = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(D, name), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def by_id(records):
    return {r["id"]: r for r in records}


def ref_contents(rec):
    out = rec.get("output")
    if isinstance(out, str):
        try:
            out = json.loads(out)
        except ValueError:
            return []
    if isinstance(out, dict):
        out = list(out.values())
    if not isinstance(out, list):
        return []
    return [tok[1].get("content") for tok in out
            if isinstance(tok, list) and tok and tok[0] == "Mathinline"]


SPAN = re.compile(r'<span class="math-inline">\$(.*?)\$</span>', re.S)
IMG = re.compile(r'<img[^>]*class="math-inline"[^>]*>', re.S)
ERR = re.compile(r'<span class="error-inline">.*?</span>', re.S)


def ftml_contents(h):
    return [htmlmod.unescape(s) for s in SPAN.findall(h or "")]


def live_contents(h):
    out = []
    for tag in IMG.findall(h or ""):
        m = re.search(r'\balt="([^"]*)"', tag)
        out.append(htmlmod.unescape(m.group(1)) if m else "")
    return out


def canon(h):
    """Factor out the serving surface and known frame whitespace."""
    h = h or ""
    h = ERR.sub("{{MATHINLINE}}", h)
    h = SPAN.sub("{{MATHINLINE}}", h)
    h = IMG.sub("{{MATHINLINE}}", h)
    h = h.replace("<br />", "<br>").replace("<hr />", "<hr>")
    h = re.sub(r"[ \t]+", " ", h)
    h = re.sub(r">\s+<", "><", h)
    return h.strip()


def main():
    battery = load("battery.jsonl")
    br = by_id(battery)
    rr = by_id(load("ref-render-before.jsonl"))
    tbu = by_id(load("ref-tokens-before-utf8.jsonl"))
    # Before any correction the "after" captures do not exist yet; in that
    # state the report is explicitly a pre-correction snapshot.
    ra = by_id(load("ref-render-after.jsonl")) if os.path.exists(
        os.path.join(D, "ref-render-after.jsonl")) else rr
    tau = by_id(load("ref-tokens-after-utf8.jsonl")) if os.path.exists(
        os.path.join(D, "ref-tokens-after-utf8.jsonl")) else tbu
    fd = by_id(load("ftml-dump.jsonl"))
    cap_path = os.path.join(D, "probes", "captures.json")
    caps = {}
    if os.path.exists(cap_path):
        with open(cap_path, encoding="utf-8") as fh:
            caps = json.load(fh)

    out = []
    w = out.append
    w("R2-inline1 Mathinline three-side comparison report")
    w("")
    w(f"Battery cases: {len(battery)}. Live captures: {len(caps)}.")
    w("")
    w("The parse-shape columns compare the Mathinline token/element contents "
      "(reference tokens, ftml math-inline spans, live math-inline img alt). "
      "The render column is raw exact bytes; the canonical column factors out "
      "the stubbed LaTeX serving surface and frame whitespace, and is the "
      "only render comparison with cross-side meaning here.")
    w("")

    shape_agree_before = shape_agree_after = 0
    raw_agree = canon_agree = 0
    changed = []
    w("id | ref-content (before -> after) | ftml | live | shape | raw | canon")
    w("--- | --- | --- | --- | --- | --- | ---")
    for case in battery:
        cid = case["id"]
        cb = ref_contents(tbu.get(cid, {}))
        ca = ref_contents(tau.get(cid, {}))
        f = ftml_contents(fd.get(cid, {}).get("html", ""))
        lc = caps.get(cid, {})
        lv = live_contents(lc.get("html", "")) if lc.get("valid") else []
        shape_b = (cb == f)
        shape_a = (ca == f)
        shape_agree_before += shape_b
        shape_agree_after += shape_a
        rb = ra.get(cid, {}).get("output", "")
        fh = fd.get(cid, {}).get("html", "")
        raw_agree += (rb == fh)
        can_ok = canon(rb) == canon(fh)
        if lc.get("valid"):
            can_ok = can_ok and canon(rb) == canon(lc["html"])
        canon_agree += can_ok
        if cb != ca:
            changed.append(cid)
        w(f"{cid} | {cb!s} -> {ca!s} | {f!s} | {lv!s} | "
          f"{'Y' if shape_a else 'N'} | {'Y' if rb == fh else 'N'} | "
          f"{'Y' if can_ok else 'N'}")
    w("")
    w(f"Parse-shape agreement reference-before vs ftml: {shape_agree_before}/{len(battery)}")
    w(f"Parse-shape agreement reference-after vs ftml: {shape_agree_after}/{len(battery)}")
    w(f"Raw render exact-byte agreement reference-after vs ftml: {raw_agree}/{len(battery)}")
    w(f"Canonical render agreement across reference-after, ftml and valid live: {canon_agree}/{len(battery)}")
    w(f"Cases whose reference Mathinline token content changed: {changed!s}")
    w("")
    if caps:
        w("Live capture validity:")
        for cid, c in caps.items():
            w(f"  {cid}: valid={c.get('valid')} stable={c.get('stable')} "
              f"saved_source_matches={c.get('saved_source_matches')} "
              f"fullname={c.get('fullname')}")
    with open(os.path.join(D, "compare-report.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print("\n".join(out[:6]))
    print("wrote compare-report.txt")


if __name__ == "__main__":
    main()
