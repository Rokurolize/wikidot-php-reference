#!/usr/bin/env python3
# Root-owned cross-rule interaction battery for the R2 inline1 stage.
# The seams the four per-rule batteries cannot own: bare URLs inside link
# labels and vice versa, email forms inside URLs, inline math inside spans,
# headings and table cells, interwiki forms colliding with include's site-pair
# grammar and with freelinks, and autolinks inside code and raw spans.
import json

cases = [
    # A. URLs inside labels and link forms (F-R2-44 neighborhood).
    ("x01", "[https://example.com/target https://example.com/label]"),
    ("x02", "[https://example.com/target [[$x$]]]"),
    ("x03", "[https://example.com/target mailto:a@b.com]"),
    ("x04", "[[http://example.com|link]]"),
    ("x05", "[[http://example.com|https://example.com/other]]"),
    ("x06", "[[http://example.com/a?b=1&c=2|label]]"),
    # B. Email forms inside URLs and described mailto forms.
    ("x07", "https://example.com/mailto:a@b.com"),
    ("x08", "[mailto:a@b.com mail]"),
    ("x09", "[[mailto:a@b.com|mail]]"),
    ("x10", "https://user:pass@example.com/path"),
    # C. Inline math inside spans, headings, cells and protected spans.
    ("x11", "[[span]]before [[$x$]] after[[/span]]"),
    ("x12", "+ heading [[$x$]] tail"),
    ("x13", "|| [[$x$]] || y ||"),
    ("x14", "||a||[[$x$]]||"),
    ("x15", "@@[[$x$]]@@"),
    ("x16", "[[code]]\n[[$x$]]\n[[/code]]"),
    ("x17", "--[[$x$]]--"),
    ("x18", "**[[$x$]]**"),
    ("x19", "{{[[$x$]]}}"),
    ("x20", "[[[$x$]]]"),
    # D. Interwiki collisions, case, site table and include/freelink seams.
    ("x21", "[wikipedia:Albert_Einstein]"),
    ("x22", "[wikipedia:Albert_Einstein Einstein]"),
    ("x23", "[WIKIPEDIA:Albert_Einstein Einstein]"),
    ("x24", "[pl.wikipedia:Kot kot]"),
    ("x25", "[google:free+wiki G]"),
    ("x26", "[banana:fruit-salad B]"),
    ("x27", "[[wikipedia:Albert_Einstein]]"),
    ("x28", "[[[wikipedia:Albert_Einstein]]]"),
    ("x29", "[wikipedia:Albert_Einstein|label]"),
    ("x30", "[[include wikipedia:Albert_Einstein]]"),
    ("x31", "[[include :sandbox:other-page]]"),
    # E. Autolinks inside code and raw spans (shielded by earlier rules).
    ("x32", "[[code]]\nhttp://example.com/a\n[[/code]]"),
    ("x33", "@@http://example.com/a@@"),
    ("x34", "[[code]]\n[wikipedia:X]\n[[/code]]"),
    ("x35", "@@[wikipedia:X]@@"),
    ("x36", "[[code]]\na@b.com\n[[/code]]"),
    ("x37", "@@a@b.com@@"),
    ("x38", "[[code]]\n[[http://x|y]]\n[[/code]]"),
    # F. Adjacency and nesting of the four inline families.
    ("x39", "http://example.com/a@b.com"),
    ("x40", "a@b.com/path"),
    ("x41", "[http://example.com/a https://x] more http://y.com"),
    ("x42", "[[$http://example.com/a$]]"),
    ("x43", "[[$[wikipedia:X]$]]"),
    ("x44", "[wikipedia:X http://example.com/a]"),
    ("x45", "[[http://x|[[$y$]]]]"),
    ("x46", "[[span]][http://example.com/a L][[/span]]"),
]

with open("xbattery.jsonl", "w", encoding="utf-8") as f:
    for cid, source in cases:
        f.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
print(f"wrote xbattery.jsonl with {len(cases)} cases")
