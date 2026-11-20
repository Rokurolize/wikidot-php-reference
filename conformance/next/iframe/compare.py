#!/usr/bin/env python3
"""Side-by-side reference / ftml / live view for the R2-next Iframe battery and probes.
Usage: compare.py battery [before|after]   or   compare.py probe [before|after].
Raw equality and Class-S-normalized equality are both reported; normalization only
removes frame-level surface (paragraph blank lines, <br /> vs <br>, <div > vs <div>,
code-block padding) and never touches iframe src, attributes, or token content.
"""
import json
import os
import sys
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def load_jsonl(name):
    path = os.path.join(HERE, name)
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        if line.strip():
            rec = json.loads(line)
            out[rec["id"]] = rec
    return out


def norm_surface(html):
    if html is None:
        return None
    html = html.replace("<br />", "<br>")
    html = html.replace("<div >", "<div>")
    html = re.sub(r"</p>\s*<p>", "</p><p>", html)
    html = re.sub(r"\A\n+|\n+\Z", "", html)
    html = re.sub(r"\n(<div class=\"code\">)", r"\1", html)
    html = re.sub(r"(</div>)\n+", r"\1", html)
    return html.strip()


def classify(raw, normalized, label):
    return f"{label}: raw={raw} norm={normalized}"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "battery"
    suffix = sys.argv[2] if len(sys.argv) > 2 else "after"
    if mode == "battery":
        cases = load_jsonl("battery.jsonl")
        ref = load_jsonl(f"ref-render-{suffix}.jsonl")
        ftml = load_jsonl("ftml-dump.jsonl")
        live = {}
    elif mode == "probe":
        cases = load_jsonl("probe-cases.jsonl")
        ref = load_jsonl(f"ref-probe-render-{suffix}.jsonl")
        ftml = load_jsonl("ftml-probe-dump.jsonl")
        path = os.path.join(HERE, "captures.json")
        live = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    else:
        raise SystemExit("mode must be battery or probe")
    raw_rf = norm_rf = total = 0
    raw_rl = norm_rl = valid = 0
    for cid, rec in cases.items():
        source = rec["source"]
        r = (ref.get(cid, {}).get("output") or ref.get(cid, {}).get("error"))
        f = ftml.get(cid, {}).get("html")
        c = live.get(cid, {})
        l = c.get("html")
        total += 1
        raw_rf += (r == f)
        norm_rf += (norm_surface(r) == norm_surface(f))
        print("=" * 78)
        print(f"CASE {cid} source={source!r}")
        print(f"  REF : {r!r}")
        print(f"  FTML: {f!r} errors={len(ftml.get(cid, {}).get('errors', []))}")
        print(classify(r == f, norm_surface(r) == norm_surface(f), "REF/FTML"))
        if live:
            isvalid = bool(c.get("valid") and c.get("stable") and c.get("saved_source_matches"))
            valid += isvalid
            print(f"  LIVE: valid={isvalid} stable={c.get('stable')} src_match={c.get('saved_source_matches')}")
            print(f"        {l!r}")
            if isvalid:
                raw_rl += (r == l)
                norm_rl += (norm_surface(r) == norm_surface(l))
                print(classify(r == l, norm_surface(r) == norm_surface(l), "REF/LIVE"))
    print("=" * 78)
    print(f"TOTAL {total}  REF/FTML {classify(raw_rf, norm_rf, 'counts')}")
    if live:
        print(f"VALID {valid}  REF/LIVE {classify(raw_rl, norm_rl, 'counts')}")


if __name__ == "__main__":
    main()
