#!/usr/bin/env python3
"""Tabview differential comparator.

Loads JSONL captures by id, applies the campaign probe.norm masking (random
wiki-tabview-*/wiki-tab-* ids, date attrs, scripts, entity decoding, attribute
order, whitespace) and a stricter structural pass that also removes inter-tag
whitespace and the fossil Div renderer's `<div >` spelling. Reports raw, norm
and structural agreement. Never scores a counter/id shift as a correction."""
import json, re, sys, importlib.machinery, importlib.util

loader = importlib.machinery.SourceFileLoader(
    "wikidot_probe", "/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe")
spec = importlib.util.spec_from_loader("wikidot_probe", loader)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

def norm(s):
    return probe.norm(s)

def struct(s):
    s = norm(s)
    s = s.replace("<br />", "<br>").replace("<div >", "<div>")
    s = re.sub(r">\s+<", "><", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def load(path, key):
    out = {}
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        out[r["id"]] = r.get(key, r.get("error", ""))
    return out

def compare(a_path, a_key, b_path, b_key, label, verbose=True):
    A, B = load(a_path, a_key), load(b_path, b_key)
    ids = sorted(set(A) & set(B))
    raw = [i for i in ids if A[i] == B[i]]
    nm = [i for i in ids if norm(A[i]) == norm(B[i])]
    st = [i for i in ids if struct(A[i]) == struct(B[i])]
    print(f"{label}: ids={len(ids)} raw={len(raw)} norm={len(nm)} struct={len(st)}")
    diff = [i for i in ids if i not in st]
    if verbose:
        for i in diff:
            print(f"  DIFF {i}")
            print("    A:", repr(norm(A[i]))[:300])
            print("    B:", repr(norm(B[i]))[:300])
    return ids, A, B, st

if __name__ == "__main__":
    compare(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5],
            verbose=(len(sys.argv) < 7 or sys.argv[6] != "quiet"))
