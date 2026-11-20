#!/usr/bin/env python3
"""Three-way report for the R2 Concatlines differential.

Loads battery.jsonl, probe-cases.jsonl, the four reference snapshots, the two
ftml dumper snapshots and captures.json from this directory, then reports
agreement on a continuation-join shape. Raw HTML differs across the three
sides for frame reasons that belong to later rules (paragraph wrappers,
<br /> versus <br>, div/span attribute spelling, the stubbed Math and
Equationreference serving surface), so the primary comparison strips tags,
normalizes breaks and collapses whitespace; exact HTML is still printed for
every probe so that no surface difference is silently hidden. Run with no
arguments after all snapshots exist.
"""
import html as htmlmod
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, required=True):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        if required:
            raise SystemExit("missing " + path)
        return None
    with open(path, encoding="utf-8") as fh:
        text = [json.loads(line) for line in fh if line.strip()]
    if text and isinstance(text[0], dict) and "html" in text[0] and "id" in text[0]:
        return text
    return text


def by_id(records, key):
    return {r["id"]: r.get(key) for r in records}


def canon(value):
    if value is None:
        return "MISSING"
    s = str(value)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</(p|div|blockquote|pre|li|h[1-6])>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = htmlmod.unescape(s)
    s = s.replace("\r", "")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()


def category(ref, ftml, live):
    if live is None:
        return "battery-only"
    a, b, c = canon(ref), canon(ftml), canon(live)
    if a == b == c:
        return "all-three"
    if a == c and b != c:
        return "ref+live-vs-ftml"
    if b == c and a != c:
        return "ftml+live-vs-ref"
    if a == b and c != a:
        return "ref+ftml-vs-live"
    return "all-disagree"


def main():
    cases = load("battery.jsonl")
    probes = load("probe-cases.jsonl")
    rb = by_id(load("ref-render-before.jsonl"), "output")
    ra = by_id(load("ref-render-after.jsonl"), "output")
    tb = by_id(load("ref-tokens-before.jsonl"), "output")
    ta = by_id(load("ref-tokens-after.jsonl"), "output")
    fd = by_id(load("ftml-dump.jsonl"), "html")
    prb = by_id(load("ref-probe-render-before.jsonl"), "output")
    pra = by_id(load("ref-probe-render-after.jsonl"), "output")
    ptb = by_id(load("ref-probe-tokens-before.jsonl"), "output")
    pta = by_id(load("ref-probe-tokens-after.jsonl"), "output")
    pfd = by_id(load("ftml-probe-dump.jsonl"), "html")
    caps_path = os.path.join(HERE, "captures.json")
    caps = json.load(open(caps_path, encoding="utf-8")) if os.path.exists(caps_path) else None

    out = []
    w = out.append
    w("R2 Concatlines three-way compare report")
    w("")

    w("Battery: 59 cases, reference before/after render and tokens against the")
    w("shared ftml dumper at HEAD 97bed049ddeadc54981f6d9577bd78fcb212abd9.")
    before_agree = sum(1 for x in cases if canon(rb[x["id"]]) == canon(fd[x["id"]]))
    after_agree = sum(1 for x in cases if canon(ra[x["id"]]) == canon(fd[x["id"]]))
    exact_before = sum(1 for x in cases if str(rb[x["id"]]).replace("<br />", "<br>").strip() == str(fd[x["id"]]).strip())
    exact_after = sum(1 for x in cases if str(ra[x["id"]]).replace("<br />", "<br>").strip() == str(fd[x["id"]]).strip())
    changed = [x["id"] for x in cases if rb[x["id"]] != ra[x["id"]]]
    w("Normalized agreement before: %d/59; after: %d/59." % (before_agree, after_agree))
    w("Exact-after-<br>-normalization agreement before: %d/59; after: %d/59." % (exact_before, exact_after))
    w("Render records changed by correction: %d (%s)." % (len(changed), ", ".join(changed) if changed else "none"))
    tok_changed = [x["id"] for x in cases if tb[x["id"]] != ta[x["id"]]]
    w("Token records changed by correction: %d (%s)." % (len(tok_changed), ", ".join(tok_changed) if tok_changed else "none"))
    w("")

    w("Battery cases whose normalized reference and ftml shapes differ after correction:")
    n = 0
    for x in cases:
        cid = x["id"]
        if canon(ra[cid]) != canon(fd[cid]):
            n += 1
            w("  %-28s REF %s | FTML %s" % (cid, repr(canon(ra[cid])[:90]), repr(canon(fd[cid])[:90])))
    w("Total: %d" % n)
    w("")

    w("Live probes: %d cases under prefix muse-probe-r2link-concat-." % len(probes))
    if caps is None:
        w("Captures not yet present; probe comparison skipped.")
    else:
        counts = {}
        valid = 0
        stable = 0
        source_ok = 0
        for x in probes:
            cid = x["id"]
            cap = caps.get(cid, {})
            live = cap.get("html") if cap.get("valid") else None
            if cap.get("valid"):
                valid += 1
            if cap.get("stable"):
                stable += 1
            if cap.get("saved_source_matches"):
                source_ok += 1
            cat = category(pra[cid], pfd[cid], live)
            counts[cat] = counts.get(cat, 0) + 1
            w("  %-28s %-22s valid=%s stable=%s source=%s" % (
                cid, cat, cap.get("valid"), cap.get("stable"), cap.get("saved_source_matches")))
            w("      REF  %s" % repr(canon(pra[cid])[:140]))
            w("      FTML %s" % repr(canon(pfd[cid])[:140]))
            w("      LIVE %s" % repr(canon(live)[:140]))
            w("      RAW REF  %s" % repr(str(pra[cid])[:200]))
            w("      RAW FTML %s" % repr(str(pfd[cid])[:200]))
            w("      RAW LIVE %s" % repr(str(live)[:200]))
        w("Counts: valid=%d stable=%d source-matched=%d" % (valid, stable, source_ok))
        for k in sorted(counts):
            w("  %s: %d" % (k, counts[k]))
        w("")
        w("Probe records whose reference shape changed with correction:")
        for x in probes:
            cid = x["id"]
            if prb[cid] != pra[cid]:
                w("  %s: %s -> %s" % (cid, repr(canon(prb[cid])[:100]), repr(canon(pra[cid])[:100])))

    text = "\n".join(out) + "\n"
    with open(os.path.join(HERE, "compare-report.txt"), "w", encoding="utf-8") as fh:
        fh.write(text)
    print(text)


if __name__ == "__main__":
    main()
