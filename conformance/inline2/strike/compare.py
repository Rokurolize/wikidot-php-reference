#!/usr/bin/env python3
"""Three-way comparator for the R2-INLINE2 Strikethrough battery.
Joins battery sources, reference render output, ftml dumper output and the
cached live captures, applies a documented canonicalization of known frame /
serving-layer surfaces, and writes compare.json plus a short summary to stdout.
"""
import json, re, sys, os

D = os.path.dirname(os.path.abspath(__file__))

def load(name, default=None):
    path = os.path.join(D, name)
    if not os.path.exists(path):
        return default
    return {r["id"]: r for r in map(json.loads, open(path, encoding="utf-8"))}

def canon(s):
    if not isinstance(s, str):
        return s
    s = s.replace("&#8212;", "\u2014").replace("&#151;", "\u2014")
    s = s.replace("<br />", "<br>").replace("<hr />", "<hr>").replace("<div >", "<div>")
    s = s.replace("style=\"color: red;\"", "style=\"color: red\"")
    s = s.replace("&#39;", "'").replace("class=\"newpage\" ", "")
    s = re.sub(r"\s*\n+\s*", "\n", s)
    s = re.sub(r">\s*\n+<", "><", s)
    s = re.sub(r"\n+", "", s)
    s = re.sub(r">\s+<", "><", s)
    return s.strip()

def main():
    ref_name = sys.argv[1] if len(sys.argv) > 1 else "ref-before-render.jsonl"
    battery = load("battery.jsonl", {})
    ref = load(ref_name, {})
    ftml = load("ftml-dump.jsonl", {})
    live = None
    if os.path.exists(os.path.join(D, "probe-captures.json")):
        data = json.load(open(os.path.join(D, "probe-captures.json"), encoding="utf-8"))
        live = data
    rows = []
    for cid, rec in battery.items():
        r = canon(ref.get(cid, {}).get("output", ref.get(cid, {}).get("error")))
        f = canon(ftml.get(cid, {}).get("html"))
        row = {"id": cid, "source": rec["source"], "ref": r, "ftml": f,
               "ref_vs_ftml": "same" if r == f else "diff"}
        if live and cid in live:
            cap = live[cid]
            l = canon(cap.get("html"))
            row["live"] = l
            row["live_valid"] = bool(cap.get("valid"))
            row["live_stable"] = bool(cap.get("stable"))
            row["saved_source_matches"] = cap.get("saved_source_matches")
            eq = [r == f, r == l, f == l]
            row["live_vs_ref"] = "same" if eq[1] else "diff"
            row["live_vs_ftml"] = "same" if eq[2] else "diff"
            if all(eq):
                row["triple"] = "all3"
            elif eq[1] and not eq[2]:
                row["triple"] = "ref+live"
            elif eq[2] and not eq[1]:
                row["triple"] = "ftml+live"
            elif eq[0] and not eq[1]:
                row["triple"] = "ref+ftml"
            else:
                row["triple"] = "all-disagree"
        rows.append(row)
    out = os.path.join(D, "compare.json")
    json.dump({"ref_file": ref_name, "rows": rows}, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    rf = sum(1 for x in rows if x["ref_vs_ftml"] == "same")
    print(f"ref={ref_name} cases={len(rows)} ref=ftml(after canon)={rf}")
    if live:
        from collections import Counter
        c = Counter(x.get("triple", "no-live") for x in rows)
        print("triple:", dict(c))

if __name__ == "__main__":
    main()
