#!/usr/bin/env python3
"""Three-way structural report for the R2-contain Div differential.

Loads the battery, the four reference snapshots (render/tokens before and
after), the ftml dumper snapshot and the live probe captures from this
directory. Raw HTML differs across the three sides for frame reasons owned
by later rules (<div > wrapper, <br /> versus <br>, paragraph wrappers,
pretty-print newlines, collapsible/tabview chrome), so the primary comparison
normalizes those surfaces and the tabview/collapsible counter ids (root's
harness audit: Collapsible::$count and Tabview $_counter leak across batch
cases). Exact HTML is printed per probe so no surface difference is hidden.
"""
import html as htmlmod
import importlib.machinery
import importlib.util
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# The campaign-standard live masker (per-render random element ids and date
# data-delta / data-timestamp), imported as directed by the skill's
# measuring-live-behavior.md rather than re-derived here.
_loader = importlib.machinery.SourceFileLoader(
    "wikidot_probe",
    "/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe",
)
_spec = importlib.util.spec_from_loader("wikidot_probe", _loader)
probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probe)


def live_canon(value):
    return canon(probe.norm(value)) if value is not None else "MISSING"


def load(name, required=True):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        if required:
            raise SystemExit("missing " + path)
        return None
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def by_id(records, key):
    return {r["id"]: r.get(key) for r in records}


def norm_ids(s):
    s = re.sub(r'collapsible-block-\d+', 'collapsible-block-N', s)
    s = re.sub(r'wiki-tabview-[0-9a-f]{8,}', 'wiki-tabview-N', s)
    s = re.sub(r'wiki-tabview-\d+', 'wiki-tabview-N', s)
    s = re.sub(r'wiki-tab-\d+-\d+', 'wiki-tab-N-N', s)
    s = re.sub(r'tabview\d+', 'tabviewN', s)
    s = re.sub(r'YAHOO\.widget\.TabView\(\'[^\']+\'\)', "YAHOO.widget.TabView('N')", s)
    return s


def canon(value):
    if value is None:
        return "MISSING"
    s = str(value)
    s = norm_ids(s)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</(p|div|blockquote|pre|li|h[1-6]|ul|ol)>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = htmlmod.unescape(s)
    s = s.replace("\r", "")
    s = re.sub(r"[ \t\xa0]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()


def category(ref, ftml, live):
    if live is None:
        return "battery-only"
    a, b, c = canon(ref), canon(ftml), live_canon(live)
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
    prb = by_id(load("ref-probe-render-before.jsonl", False) or [], "output")
    pra = by_id(load("ref-probe-render-after.jsonl", False) or [], "output")
    ptb = by_id(load("ref-probe-tokens-before.jsonl", False) or [], "output")
    pta = by_id(load("ref-probe-tokens-after.jsonl", False) or [], "output")
    pfd = by_id(load("ftml-probe-dump.jsonl", False) or [], "html")
    caps_path = os.path.join(HERE, "captures.json")
    caps = json.load(open(caps_path, encoding="utf-8")) if os.path.exists(caps_path) else None

    out = []
    w = out.append
    w("R2-contain Div three-way compare report")

    before_agree = sum(1 for x in cases if canon(rb[x["id"]]) == canon(fd[x["id"]]))
    after_agree = sum(1 for x in cases if canon(ra[x["id"]]) == canon(fd[x["id"]]))
    changed = [x["id"] for x in cases if rb[x["id"]] != ra[x["id"]]]
    tok_changed = [x["id"] for x in cases if tb[x["id"]] != ta[x["id"]]]
    w(f"Battery: {len(cases)} cases; normalized reference/ftml agreement before {before_agree}/{len(cases)}, after {after_agree}/{len(cases)}.")
    w(f"Render records changed by correction: {len(changed)}; token records changed: {len(tok_changed)}.")
    w("Changed render ids: " + ", ".join(changed))
    w("")

    w("Battery cases whose normalized reference and ftml shapes still differ after correction:")
    for x in cases:
        cid = x["id"]
        if canon(ra[cid]) != canon(fd[cid]):
            w(f"  {cid:26} REF {canon(ra[cid])[:100]!r} | FTML {canon(fd[cid])[:100]!r}")
    w("")

    if caps is None:
        w("Live captures not present; probe comparison skipped.")
    else:
        counts = {}
        valid = 0
        for x in probes:
            cid = x["id"]
            cap = caps.get(cid)
            if not cap or not cap.get("valid") or not cap.get("stable") or not cap.get("saved_source_matches"):
                continue
            valid += 1
            cat = category(pra.get(cid), pfd.get(cid), cap.get("html"))
            counts[cat] = counts.get(cat, 0) + 1
            w(f"  PROBE {cid:26} {cat:20} REF {canon(pra.get(cid))[:70]!r} FTML {canon(pfd.get(cid))[:70]!r} LIVE {live_canon(cap.get('html'))[:70]!r}")
        w(f"Valid/stable/source-matching probes: {valid}/{len(probes)}")
        w("Probe categories: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))

    text = "\n".join(out) + "\n"
    with open(os.path.join(HERE, "compare-report.txt"), "w") as fh:
        fh.write(text)
    print(text)


if __name__ == "__main__":
    main()
