#!/usr/bin/env python3
"""Compare reference render vs ftml legacy html for the R2 Form/Raw/Rawold battery."""
import json, re, sys

root = "/home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh/conformance-refphp/formraw/"


def load(p):
    out = {}
    try:
        for line in open(root + p, encoding="utf-8"):
            r = json.loads(line)
            out[r["id"]] = r
    except FileNotFoundError:
        pass
    return out


ref = load(sys.argv[1] if len(sys.argv) > 1 else "ref-render-before.jsonl")
ftml = load(sys.argv[2] if len(sys.argv) > 2 else "ftml-dump.jsonl")


def shape(s):
    if not isinstance(s, str):
        return s
    s = s.replace("\r\n", "\n").replace("<br />", "<br>")
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip("\n")


same = 0
diff = []
for cid in ref:
    r = ref[cid].get("output", "ERR:" + ref[cid].get("error", ""))
    f = ftml.get(cid, {}).get("html", "MISSING")
    if shape(r) == shape(f):
        same += 1
    else:
        diff.append((cid, r, f))
print("total=%d shaped_same=%d diff=%d" % (len(ref), same, len(diff)))
for cid, r, f in diff:
    print("=== %s\n  ref: %r\n  ftm: %r" % (cid, r[:220], f[:220]))
