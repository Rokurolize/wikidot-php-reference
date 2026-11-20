#!/usr/bin/env python3
# Three-way comparison of the reference (before and after correction), the
# shared ftml dumper, and cached live probes at the heading surface. The
# signature keeps the heading tag, its id attribute and its inner markup;
# frame-level newline padding is stripped because Newline/Paragraph rules own
# it. A separate whole-string view is reported without that forgiveness.
import json
import re
import sys

HEAD = re.compile(r"<h([1-6])((?:\s+[^>]*)?)>(.*?)</h\1>", re.S)

def signature(html):
    sig = []
    for m in HEAD.finditer(html or ""):
        level = int(m.group(1))
        attrs = m.group(2).strip()
        idm = re.search(r'\bid="([^"]*)"', attrs)
        ident = idm.group(1) if idm else None
        inner = re.sub(r"\s+", " ", m.group(3)).strip()
        sig.append((level, ident, inner))
    return sig

def load(path, field):
    out = {}
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        out[r["id"]] = r.get(field) or ""
    return out

def canon(html):
    if html is None:
        return ""
    html = html.replace("&#39;", "'").replace("&#039;", "'")
    html = re.sub(r"\s+", " ", html).strip()
    return html

def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "."
    mode = sys.argv[2] if len(sys.argv) > 2 else "battery"
    if mode == "battery":
        before = load(f"{base}/ref-render-before.jsonl", "output")
        after = load(f"{base}/ref-render-after.jsonl", "output")
        ftml = load(f"{base}/ftml-dump.jsonl", "html")
        live = {}
    else:
        before = load(f"{base}/ref-probe-render-before.jsonl", "output")
        after = load(f"{base}/ref-probe-render-after.jsonl", "output")
        ftml = load(f"{base}/ftml-probe-dump.jsonl", "html")
        live = {k: v["html"] for k, v in json.load(open(f"{base}/captures.json", encoding="utf-8")).items()}

    ids = sorted(after)
    stats = {"n": len(ids), "sig_before_ftml": 0, "sig_after_ftml": 0,
             "sig_after_live": 0, "sig_ftml_live": 0, "all3": 0,
             "whole_after_ftml": 0, "whole_after_live": 0}
    rows = []
    for cid in ids:
        sb, sa, sf = signature(before.get(cid)), signature(after.get(cid)), signature(ftml.get(cid))
        sl = signature(live.get(cid, "")) if live else None
        stats["sig_before_ftml"] += sb == sf
        stats["sig_after_ftml"] += sa == sf
        if sl is not None:
            stats["sig_after_live"] += sa == sl
            stats["sig_ftml_live"] += sf == sl
            stats["all3"] += sa == sf == sl
        stats["whole_after_ftml"] += canon(after.get(cid)) == canon(ftml.get(cid))
        if live:
            stats["whole_after_live"] += canon(after.get(cid)) == canon(live.get(cid, ""))
        if (sl is not None and not (sa == sf == sl)) or (sl is None and sa != sf):
            rows.append((cid, sb, sa, sf, sl))
    print(f"MODE {mode}: {json.dumps(stats, sort_keys=True)}")
    print(f"mismatching cases after correction: {len(rows)}")
    for cid, sb, sa, sf, sl in rows:
        print(f"--- {cid}")
        print(f"    before: {sb}")
        print(f"    after : {sa}")
        print(f"    ftml  : {sf}")
        if sl is not None:
            print(f"    live  : {sl}")

if __name__ == "__main__":
    main()
