#!/usr/bin/env python3
"""Compare two JSONL captures (ref {id,output} vs ftml {id,html}) with raw and
canonical agreement. Canonicalization only: normalize <br /> to <br>, &#39; to
apostrophe, collapse whitespace runs to one space, and strip ends. It keeps
whitespace BETWEEN tags (so the fossil's 4-space-per-level indentation stays a
visible difference)."""
import json, re, sys

def canon(s):
    s = s.replace("<br />", "<br>")
    s = s.replace("&#39;", "'")
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def load(path, key):
    out = {}
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        out[r["id"]] = r.get(key, r.get("error", ""))
    return out

def main(a, ak, b, bk):
    A, B = load(a, ak), load(b, bk)
    ids = sorted(set(A) & set(B))
    raw = [i for i in ids if A[i] == B[i]]
    can = [i for i in ids if canon(A[i]) == canon(B[i])]
    print(f"ids={len(ids)} raw={len(raw)} canonical={len(can)}")
    print("--- canonical mismatches ---")
    for i in ids:
        if canon(A[i]) != canon(B[i]):
            print(i)
            print("  REF :", repr(A[i])[:200])
            print("  FTL :", repr(B[i])[:200])

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
