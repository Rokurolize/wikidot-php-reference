#!/usr/bin/env python3
"""Side-by-side comparison of reference, ftml, and live for the probe cases.

Reads probe-cases.jsonl, ref-probe-render-before.jsonl (or -after), ftml-probe-dump.jsonl
and captures.json, prints one block per case with the three rendered shapes and
validity flags. Run after the probe capture completes.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_jsonl(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return {}
    out = {}
    for line in open(path, encoding="utf-8"):
        if line.strip():
            rec = json.loads(line)
            out[rec["id"]] = rec
    return out


def main():
    suffix = sys.argv[1] if len(sys.argv) > 1 else "before"
    cases = {r["id"]: r["source"] for r in
             (json.loads(l) for l in open(os.path.join(HERE, "probe-cases.jsonl"), encoding="utf-8"))}
    ref = load_jsonl(f"ref-probe-render-{suffix}.jsonl")
    ftml = load_jsonl("ftml-probe-dump.jsonl")
    captures_path = os.path.join(HERE, "captures.json")
    live = json.load(open(captures_path, encoding="utf-8")) if os.path.exists(captures_path) else {}
    for cid, source in cases.items():
        r = ref.get(cid, {})
        f = ftml.get(cid, {})
        c = live.get(cid, {})
        print("=" * 78)
        print(f"CASE {cid}  source={source!r}")
        print(f"  REF : {r.get('output', r.get('error'))!r}")
        print(f"  FTML: {f.get('html')!r} errors={len(f.get('errors', []))}")
        print(f"  LIVE: valid={c.get('valid')} stable={c.get('stable')} "
              f"src_match={c.get('saved_source_matches')}")
        print(f"        {c.get('html')!r}")


if __name__ == "__main__":
    main()
