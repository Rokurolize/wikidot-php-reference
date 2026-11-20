#!/usr/bin/env python3
"""Side-by-side report for the R2-next Math differential.

Loads battery.jsonl, the four reference snapshots, ftml-dump.jsonl and
(once captured) captures.json from this directory, and reports agreement at
the shape level (block recognized vs literal) plus the token-level Math
options. Frame-level surface (paragraph newlines, <br /> vs <br>, and the
out-of-scope LaTeX image failure path) is normalized away before comparison.
Run with no arguments after the files exist.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def by_id(records, key):
    return {r["id"]: (r.get(key) if key else r) for r in (records or [])}


def shape_ref(out):
    if out is None:
        return "missing"
    if isinstance(out, str) and out.startswith("Error:") or "Call to undefined" in str(out):
        return "harness-error"
    s = str(out)
    if '<div class="error-block">The equation has not' in s:
        return "math-block"
    if "math-equation" in s or "equation-number" in s:
        return "math-block"
    if "[[math" in s:
        return "literal"
    return "other"


def shape_ftml(html):
    if html is None:
        return "missing"
    s = str(html)
    if "math-equation" in s or "equation-number" in s:
        return "math-block"
    if "Unsupported math environment" in s:
        return "math-block"
    if "[[math" in s:
        return "literal"
    return "other"


def shape_live(html):
    if html is None:
        return "missing"
    s = str(html)
    if "math-equation" in s or "local--math/eqs" in s or "equation-number" in s:
        return "math-block"
    if "The equation has not been processed correctly" in s or "error-block" in s and "math" in s.lower():
        return "math-block"
    if "[[math" in s:
        return "literal"
    return "other"


def math_tokens(output):
    if not output:
        return []
    try:
        toks = json.loads(output)
    except (ValueError, TypeError):
        return []
    vals = list(toks.values()) if isinstance(toks, dict) else toks
    return [v[1] for v in vals if isinstance(v, list) and v[0] == "Math"]


def frame_norm(text):
    t = str(text)
    t = t.replace("<br />", "<br>")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def report_battery():
    battery = load("battery.jsonl") or []
    before = by_id(load("ref-render-before.jsonl"), None)
    after = by_id(load("ref-render-after.jsonl"), None)
    tok_before = by_id(load("ref-tokens-before.jsonl"), None)
    tok_after = by_id(load("ref-tokens-after.jsonl"), None)
    dump = by_id(load("ftml-dump.jsonl"), "html")
    if not battery:
        print("no battery.jsonl")
        return
    changed = []
    agree_before = agree_after = surface = disagree = errors = 0
    print("id                            ref-before   ref-after    ftml         tokens  note")
    for case in battery:
        cid = case["id"]
        rb, ra, fh = before.get(cid), after.get(cid), dump.get(cid)
        rb = (rb or {}).get("output", "Error: " + str((rb or {}).get("error", "missing")))
        ra = (ra or {}).get("output", "Error: " + str((ra or {}).get("error", "missing")))
        if (after.get(cid) or {}).get("error"):
            errors += 1
        sb, sa, sf = shape_ref(rb), shape_ref(ra), shape_ftml(fh)
        tb = len(math_tokens((tok_before.get(cid) or {}).get("output")))
        ta = len(math_tokens((tok_after.get(cid) or {}).get("output")))
        note = []
        if frame_norm(rb) != frame_norm(ra):
            changed.append(cid)
            note.append("CHANGED")
        if ra is not None:
            if sa == sf:
                agree_after += 1
                if sf == "math-block":
                    surface += 1
            else:
                disagree += 1
                note.append("DISAGREE")
        if sb == sf:
            agree_before += 1
        print(f"{cid:28s} {sb:11s} {sa:11s} {sf:11s} {tb}->{ta:<6d} {' '.join(note)}")
    print(f"\nbattery size: {len(battery)}")
    print(f"render outputs changed by corrections: {len(changed)} ({', '.join(changed)})")
    print(f"shape agreement before: {agree_before}/{len(battery)}; after: "
          f"{agree_after}/{len(battery) if after else 0}")
    print(f"of the after-agreements, {surface} are math-block surface (rendered shape differs by serving layer)")
    print(f"shape disagreements after: {disagree}/{len(battery) if after else 0}")
    print(f"after render records that are caught reference errors: {errors}")


def report_probes():
    path = os.path.join(HERE, "captures.json")
    if not os.path.exists(path):
        print("\nno captures.json yet; live comparison skipped")
        return
    data = json.load(open(path, encoding="utf-8"))
    records = data.values() if isinstance(data, dict) else data
    ref = by_id(load("ref-probe-render-after.jsonl"), "output")
    ref_before = by_id(load("ref-probe-render-before.jsonl"), "output")
    dump = by_id(load("ftml-probe-dump.jsonl"), "html")
    changed = [cid for cid in ref if frame_norm(ref_before.get(cid)) != frame_norm(ref.get(cid))]
    all_three = ref_live = ftml_live = all_disagree = valid = 0
    print("\nid                            ref          ftml         live         valid  stable")
    for rec in records:
        cid = rec.get("id")
        if cid is None:
            cid = str(rec.get("fullname", "")).replace("muse-probe-r2next-math-", "", 1)
        html = rec.get("html") or rec.get("page_html") or rec.get("content") or ""
        ok = bool(rec.get("saved_source_matches")) and bool(rec.get("stable"))
        if ok:
            valid += 1
        sr, sf, sl = shape_ref(ref.get(cid)), shape_ftml(dump.get(cid)), shape_live(html)
        if sr == sf == sl:
            all_three += 1
        elif sr == sl:
            ref_live += 1
        elif sf == sl:
            ftml_live += 1
        else:
            all_disagree += 1
        print(f"{cid:28s} {sr:11s} {sf:11s} {sl:11s} {str(ok):5s}  {rec.get('stable')}")
    print(f"\nprobe renders changed by corrections: {len(changed)} ({', '.join(changed)})")
    print(f"valid probes: {valid}; all three agree: {all_three}; ref+live: {ref_live}; "
          f"ftml+live: {ftml_live}; all disagree: {all_disagree}")


if __name__ == "__main__":
    report_battery()
    report_probes()
