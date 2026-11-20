#!/usr/bin/env python3
"""Produce the consolidated Bibitem compare report with controlled A/B isolation."""
import json
import re


def load(p):
    return {r["id"]: r for r in (json.loads(l) for l in open(p, encoding="utf-8"))}


def shape(html):
    h = html.replace("\n", " ")
    return (
        re.findall(r'<div class="bibitem"[^>]*>.*?</div>', h)
        + re.findall(r'<a href="javascript:;"[^>]*class="bibcite"[^>]*>.*?</a>', h)
        + re.findall(r'<span class="error-inline">.*?</span>', h)
    )


def bits(html):
    return re.findall(r'<div class="bibitem"[^>]*>.*?</div>', html.replace("\n", " "))


def nbits(s):
    return re.findall(r'<div class="bibitem"[^>]*>.*?</div>', re.sub(r"\s+", " ", s))


def ncites(s):
    return re.findall(r'<a[^>]*class="bibcite"[^>]*>(\d+)</a>', s)


def nerr(s):
    return re.findall(r'<span class="error-inline">.*?</span>', s)


ft = load("ftml-dump.jsonl")
ftprobe = load("ftml-probe-dump.jsonl")
caps = json.load(open("captures.json", encoding="utf-8"))
lines = []
A = lines.append

A("Bibitem R2-notes consolidated compare report (2026-11-20).")
A("Three reference snapshots are compared: 'before' is the original tree at the start of")
A("this rule (original Bibitem and original Bibliography), 'controlled-before' is every")
A("teammate's CURRENT file with only my two Bibitem files restored to their pre-correction")
A("bytes, and 'after' is the current tree with my correction in place. The controlled pair")
A("isolates my correction from the Bibliography owner's concurrent edit at 13:25-13:26,")
A("which removed inter-div whitespace and moved raw whole-string agreement from 0/52 to")
A("29/52 all by itself. I do not claim that jump for Bibitem.")
A("")

A("=== Battery (52 whole-document cases) ===")
for tag, p in [
    ("before", "ref-render-before.jsonl"),
    ("controlled-before", "ref-render-controlled-before.jsonl"),
    ("after", "ref-render-after.jsonl"),
]:
    r = load(p)
    raw = sum(r[c].get("output") == ft[c].get("html") for c in r)
    sh = sum(shape(r[c].get("output", "")) == shape(ft[c].get("html", "")) for c in r)
    bd = sum(bits(r[c].get("output", "")) == bits(ft[c].get("html", "")) for c in r)
    A(f"{tag}: raw whole-string ref==ftml {raw}/52; bibitem-family shape {sh}/52; bibitem div {bd}/52")

A("")
A("=== Live probes (22 pages, all valid / stable / source-matching) ===")
for tag, p in [
    ("before", "ref-probe-render-before.jsonl"),
    ("controlled-before", "ref-probe-render-controlled-before.jsonl"),
    ("after", "ref-probe-render-after.jsonl"),
]:
    r = load(p)

    def ok(cid, side):
        return (nbits(side), ncites(side), nerr(side)) == (
            nbits(caps[cid]["html"]),
            ncites(caps[cid]["html"]),
            nerr(caps[cid]["html"]),
        )

    lr = sum(ok(c, r[c].get("output", "")) for c in r)
    lf = sum(ok(c, ftprobe[c].get("html", "")) for c in r)
    a3 = sum(
        ok(c, r[c].get("output", "")) and ok(c, ftprobe[c].get("html", "")) for c in r
    )
    A(f"{tag}: live==reference {lr}/22; live==ftml {lf}/22; all-three {a3}/22")

A("")
A("=== Isolated effect of the Bibitem correction (controlled-before -> after) ===")
for name in ["render", "tokens", "probe-render", "probe-tokens"]:
    b = load(f"ref-{name}-controlled-before.jsonl")
    a = load(f"ref-{name}-after.jsonl")
    ch = [c for c in b if b[c].get("output") != a[c].get("output")]
    A(f"ref-{name}: {len(ch)}/{len(b)} cases changed: {', '.join(ch) if ch else 'none'}")
A("The four probe render changes are exactly p-empty-body, p-empty-blank-entry,")
A("p-space-only-body and p-tab-only-body, each only 'N. ' -> 'N.'. The one battery")
A("render change is b07-empty-body, also 'N. ' -> 'N.'. Token-mode changes are only")
A("the added boolean 'empty' option on Bibitem start tokens; no rule, label, id or")
A("content changed. The corrected tree has empty PHP stderr on every run.")

A("")
A("=== Remaining disagreements after correction ===")
A("Live==reference disagrees on 2/22 probes: p-self-cite (Bibcite's id suffix and")
A("Bibcite's quote spelling, Bibcite owner's surface) and p-span-inline (reference")
A("<span style=\"\"> versus live and ftml <span>, Span rule frame surface). Both are")
A("outside Bibitem's two files. Live==ftml disagrees on 3/22 probes: p-self-cite,")
A("p-nested-footnote and p-special-chars, all solely the ftml &#39; quote-entity")
A("spelling against live's raw apostrophe in onclick attributes and in text.")
A("The battery's 4 remaining bibitem-div shape disagreements are the same four")
A("surfaces (b13 Bibcite, b14 Footnote quote, b42 text quote, b49 Span).")
A("All other battery differences are frame-level whitespace and wrapper padding.")
A("")
A("Coverage: no candidate ftml divergence in Bibitem's own div wrapper, numbering,")
A("emptiness or label handling was found; the ftml quote-entity cases are routed as")
A("candidate findings F1/F2 for the coordinator because they surface inside a")
A("bibliography entry but belong to ftml's HtmlContext escaping, not to Bibitem.")

open("compare-report.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
