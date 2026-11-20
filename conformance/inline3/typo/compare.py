#!/usr/bin/env python3
"""Compare reference render captures with the shared ftml dumper.

Usage: python3 compare.py ref-render-before.jsonl ftml-dump.jsonl

The harness appends two trailing newlines to every render record, and the two
renderers serialize line breaks, horizontal rules, link classes, colour styles,
apostrophes and typographic characters differently.  `frame` strips only
serialization surface (including the two trailing newlines); `canon`
additionally maps every Typography entity to the raw character ftml emits, so a
residual under `canon` is a substantive Stage-1 disagreement rather than a
spelling difference.  Both raw and normalized counts are reported, as required.
Non-breaking space is mapped before whitespace collapse so it stays visible.
"""
import json
import os
import re
import sys

DIR = os.path.dirname(os.path.abspath(__file__))

ENTITIES = {
    "&#8220;": "\u201c", "&#8221;": "\u201d", "&#8222;": "\u201e",
    "&#8216;": "\u2018", "&#8217;": "\u2019", "&#171;": "\u00ab",
    "&#187;": "\u00bb", "&#160;": "\u00a0", "&#8230;": "\u2026",
    "&#8212;": "\u2014", "&#39;": "'", "&#039;": "'", "&quot;": '"',
}


def canon(html):
    if html is None:
        return ""
    h = html.rstrip("\n")
    for entity, char in ENTITIES.items():
        h = h.replace(entity, char)
    h = h.replace("<br />", "<br>").replace("<hr />", "<hr>")
    h = h.replace(' class="newpage"', "")
    h = re.sub(r'(style="color: #[0-9a-fA-F]{3,6});"', r'\1"', h)
    return re.sub(r"[ \t\r\n]+", "", h)


def frame(html):
    if html is None:
        return ""
    h = html.rstrip("\n")
    h = h.replace("<br />", "<br>").replace("<hr />", "<hr>")
    h = h.replace(' class="newpage"', "")
    h = re.sub(r'(style="color: #[0-9a-fA-F]{3,6});"', r'\1"', h)
    return re.sub(r"[ \t\r\n]+", "", h)


def load(name):
    with open(os.path.join(DIR, name), encoding="utf-8") as fh:
        return {r["id"]: r.get("output", r.get("html", r.get("error", "")))
                for r in (json.loads(line) for line in fh if line.strip())}


def main():
    ref, ftml = load(sys.argv[1]), load(sys.argv[2])
    ids = sorted(ref)
    raw = [i for i in ids if str(ref[i]).strip() == str(ftml.get(i, "")).strip()]
    fr = [i for i in ids if frame(ref[i]) == frame(ftml.get(i, ""))]
    can = [i for i in ids if canon(ref[i]) == canon(ftml.get(i, ""))]
    print(f"total {len(ids)}  raw {len(raw)}  frame {len(fr)}  canonical {len(can)}")
    print("raw matches:", ",".join(raw))
    print("frame residual:", ",".join(i for i in ids if i not in fr))
    print("canonical residual:", ",".join(i for i in ids if i not in can))
    for i in ids:
        if i not in can:
            print(f"--- {i}\n REF : {ref[i]!r}\n FTML: {ftml.get(i)!r}")


if __name__ == "__main__":
    main()
