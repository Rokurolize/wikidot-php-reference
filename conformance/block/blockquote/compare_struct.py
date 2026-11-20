#!/usr/bin/env python3
"""Rule-level comparator: raw, whitespace-canonical, and structural agreement
between pairs of {id,output} / {id,html} / {id,source_html} captures.

Structural canonicalization removes inter-tag whitespace (the live page
serializer's pretty-print newlines, the fossil's padding), normalizes <br />
to <br> and &#39; to an apostrophe, and collapses whitespace inside text
runs. It leaves element nesting, attributes, entities and text intact."""
import json, re, sys

def struct(s):
    s = s.replace("<br />", "<br>").replace("&#39;", "'")
    s = re.sub(r">\s+<", "><", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def canon(s):
    s = s.replace("<br />", "<br>").replace("&#39;", "'")
    return re.sub(r"\s+", " ", s).strip()

def load(path, key):
    out = {}
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        out[r["id"]] = r.get(key, r.get("error", ""))
    return out

def main():
    a, ak, b, bk, label = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    A, B = load(a, ak), load(b, bk)
    ids = sorted(set(A) & set(B))
    raw = [i for i in ids if A[i] == B[i]]
    can = [i for i in ids if canon(A[i]) == canon(B[i])]
    st = [i for i in ids if struct(A[i]) == struct(B[i])]
    print(f"{label}: ids={len(ids)} raw={len(raw)} canonical={len(can)} structural={len(st)}")
    return ids, A, B, st

if __name__ == "__main__":
    main()
