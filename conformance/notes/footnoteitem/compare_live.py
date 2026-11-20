#!/usr/bin/env python3
"""Compare live saved-page, reference and ftml footnote-item footers.

Settles two Footnoteitem-surface questions with live evidence:
  (Q1) the onclick quote spelling (raw ' in the reference vs &#39; in ftml);
  (Q2) the separator after the back-reference on an empty note body
       (". " with a trailing space in the reference vs "." in ftml).
All comparisons are restricted to the <div class="footnote-footer"> segments,
which are the exact surface rendered by Render/Xhtml/Footnoteitem.php.
"""
import json
import re

FOOTER = re.compile(r'<div class="footnote-footer".*?</div>', re.S)


def load(path, key):
    out = {}
    for line in open(path, encoding="utf-8"):
        d = json.loads(line)
        out[d["id"]] = d.get(key) or ""
    return out


def footers(s):
    return FOOTER.findall(s)


def main():
    caps = json.load(open("captures.json", encoding="utf-8"))
    ref = load("ref-probe-render-before.jsonl", "output")
    ft = load("ftml-probe-dump.jsonl", "html")
    valid = [k for k, v in caps.items() if v.get("valid")]
    print(f"captures: {len(caps)}, valid/stable/source-matching: {len(valid)}")
    q1_live_raw = q1_live_ent = 0
    q2_live_space = q2_live_nospace = 0
    footer_rows = 0
    live_ref_same = live_ft_same = 0
    for cid in valid:
        live = caps[cid]["html"]
        lf, rf, ff = footers(live), footers(ref.get(cid, "")), footers(ft.get(cid, ""))
        if not lf:
            continue
        footer_rows += 1
        if lf == rf:
            live_ref_same += 1
        if lf == ff:
            live_ft_same += 1
        for x in lf:
            if "scrollToReference('" in x:
                q1_live_raw += 1
            if "scrollToReference(&#39;" in x:
                q1_live_ent += 1
            m = re.search(r'</a>(\.\s*)</div>', x)
            if m:
                if m.group(1) == ". ":
                    q2_live_space += 1
                elif m.group(1) == ".":
                    q2_live_nospace += 1
        # print detailed per-probe item shapes for the settling cases
        if cid in ("p-one", "p-empty", "p-empty-ws", "p-two", "p-block-first"):
            print("=" * 72)
            print(cid)
            print("  LIVE:", [x for x in lf])
            print("  REF :", [x for x in rf])
            print("  FTL :", [x for x in ff])
    print("=" * 72)
    print(f"probes with >=1 footer: {footer_rows}")
    print(f"footer-list live==ref raw: {live_ref_same}/{footer_rows}")
    print(f"footer-list live==ftml raw: {live_ft_same}/{footer_rows}")
    print(f"Q1 live footers with raw quote: {q1_live_raw}; with &#39; entity: {q1_live_ent}")
    print(f"Q2 empty-body footers with '. ' (space): {q2_live_space}; with '.' (no space): {q2_live_nospace}")


if __name__ == "__main__":
    main()
