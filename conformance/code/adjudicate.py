#!/usr/bin/env python3
"""Adjudicate the R2 Code battery against live captures.

Compares only the code-block fragment (`<div class="code">...</div>`), since
surrounding paragraph text differs between the battery cases and the probe
labels. Two normalizations:
  - `wrap`: remove the single newline live puts between `<div class="code">`
    and its child `<pre>`/`<div class="hl-main">` (the FRAME open item).
  - `full`: also strip empty spans from highlighter output (fossil vendor
    artifact) and normalize `&#039;` to `'`.

Prints one row per probe/battery pair: whether ref (before correction), ftml,
and ref (expected after correction) match live's code fragment.
"""
import json, re

root = "/home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh/conformance-refphp/code/"
cap = json.load(open(root + "captures.json"))
ref = {r["id"]: r.get("output", "ERR:" + r.get("error", "")) for r in map(json.loads, open(root + "ref-render.jsonl"))}
ftml = {r["id"]: r.get("html", "") for r in map(json.loads, open(root + "ftml-dump.jsonl"))}

PAIRS = {
    "wrap-basic": "basic-line",
    "empty-body": "empty",
    "blank-body": "empty-two-lines",
    "blankrun-body": "body-blank-run",
    "py-type": "arg-type-python",
    "css-type": "arg-type-css-inline",
    "unknown-type": "arg-type-unknown",
    "name-arg": "arg-name",
    "literal-body": "body-wikitext",
    "entities-body": "body-quotes",
    "midline": "mid-paragraph",
    "stray-close": "stray-closer",
    "unterminated": "unterminated",
    "nested": "nested-openers",
    "spaced-opener": "arg-spaced-name",
}


def fragment(s):
    """Return code-block fragments concatenated, or a marker for literal."""
    if "<div class=\"code\"" not in s:
        return "<LITERAL>"
    # capture each div.code block by balancing is overkill; find to first </div>
    # for the simple shapes here, then also grab trailing </div> for hl blocks
    out = []
    pos = 0
    while True:
        i = s.find('<div class="code"', pos)
        if i < 0:
            break
        # find matching </div>: count opens/closes from i
        depth = 0
        j = i
        while j < len(s):
            if s.startswith("<div", j):
                depth += 1
            elif s.startswith("</div>", j):
                depth -= 1
                if depth == 0:
                    j += len("</div>")
                    break
            j += 1
        out.append(s[i:j])
        pos = j
    return "".join(out)


def normalize(s, wrap=True, extra=False):
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    if wrap:
        s = s.replace('<div class="code">\n', '<div class="code">')
        s = s.replace('<div class="hl-main">\n', '<div class="hl-main">')
    if extra:
        s = re.sub(r'<span class="hl-[a-z]+"></span>', '', s)
        s = s.replace("&#039;", "'")
    return s.strip()


print(f"{'probe':<16} {'battery':<20} {'ref':>5} {'ftml':>5} {'ref*':>5}  note")
print("-" * 90)
for p, b in PAIRS.items():
    live = normalize(fragment(cap[p]["html"]), wrap=True, extra=True)
    r0 = normalize(fragment(ref[b]), wrap=True, extra=False)
    f = normalize(fragment(ftml[b]), wrap=True, extra=True)
    r1 = normalize(fragment(ref[b]), wrap=True, extra=True)
    mark = lambda x: "OK" if x == live else "DIFF"
    note = ""
    if r1 != live:
        note = "LIVE=" + repr(live[:120])
    print(f"{p:<16} {b:<20} {mark(r0):>5} {mark(f):>5} {mark(r1):>5}  {note}")
