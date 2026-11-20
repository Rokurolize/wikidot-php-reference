#!/usr/bin/env python3
"""Generate the Freelink live probe set and the two existence target pages.
probe-cases.jsonl: {id, source} records whose rendered saved page is evidence.
target-cases.jsonl: the two run-owned pages named exactly
muse-probe-r2link-free-exists and muse-probe-r2link-free-exists2, whose content
mirrors the root harness page map in ref-php/harness/pages.php."""
import json
import os

PROBES = [
    # existence polarity and case-variation (the battery cannot settle these
    # because the ftml dumper has no page-existence notion)
    ("p-exist-labeled", "[[[muse-probe-r2link-free-exists|shown]]]"),
    ("p-exist-bare", "[[[muse-probe-r2link-free-exists]]]"),
    ("p-exist2-empty-label", "[[[muse-probe-r2link-free-exists2|]]]"),
    ("p-new-labeled", "[[[muse-probe-r2link-free-new-page|Wanted]]]"),
    ("p-case-upper-exist", "[[[MUSE-PROBE-R2LINK-FREE-EXISTS|shown]]]"),
    # anchors (fossil regex vs ftml corpus pins)
    ("p-anchor-digit", "[[[scp-series#001|SCP-001 to SCP-099]]]"),
    ("p-anchor-alpha", "[[[scp-series#section|Label]]]"),
    ("p-anchor-dash", "[[[scp-series#sec-1|Label]]]"),
    ("p-anchor-underscore", "[[[scp-series#sec_1|Label]]]"),
    ("p-anchor-colon", "[[[scp-series#sec:1|Label]]]"),
    ("p-anchor-label-only-space", "[[[ #my-anchor | Label ]]]"),
    ("p-anchor-plain", "[[[scp-series#001]]]"),
    ("p-triple-hash", "[[[home###|Home]]]"),
    # label/target edges
    ("p-dup-pipes", "[[[page-slug|A|B|C]]]"),
    ("p-dup-pipes-spaced", "[[[ page-slug | A | B | C ]]]"),
    ("p-empty-target", "[[[|Label]]]"),
    ("p-whitespace-target", "[[[   |Label]]]"),
    ("p-empty-label", "[[[some-page|]]]"),
    ("p-quad", "[[[[SCP-001-EX]]]]"),
    ("p-quint", "[[[[[SCP-001-EX]]]]]"),
    # cross-site and category
    ("p-cross-colon", "[[[:scp-wiki:component:theme|Sigma-9 Theme]]]"),
    ("p-fossil-cross", "[[[site::page|Label]]]"),
    ("p-category", "[[[system:Recent Changes]]]"),
    ("p-default-category", "[[[_default:a|Label]]]"),
    ("p-multi-colon-empty", "[[[a:b:c|]]]"),
    # URL and leading space
    ("p-url-plain", "[[[https://example.com/|Example]]]"),
    ("p-url-leading-space", "[[[ https://example.com/ | Example ]]]"),
    ("p-url-trailing-space", "[[[https://example.com | Trailing]]]"),
    ("p-url-hash-route", "[[[MAIN/#/page|Hash routing]]]"),
    # star/underscore/unicode and positions
    ("p-star", "[[[*SCP-001]]]"),
    ("p-underscore", "[[[_some-page|Label]]]"),
    ("p-cyrillic", "[[[документ]]]"),
    ("p-midline", "text before [[[some-page|Mid line]]] text after"),
    ("p-noline-start", "first line\n[[[some-page|Second line]]]"),
]

TARGETS = [
    ("exists", "FREELINK TARGET ONE"),
    ("exists2", "FREELINK TARGET TWO"),
]

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "probe-cases.jsonl"), "w", encoding="utf-8") as fh:
        for cid, source in PROBES:
            fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
    with open(os.path.join(here, "target-cases.jsonl"), "w", encoding="utf-8") as fh:
        for cid, source in TARGETS:
            fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
    print(f"wrote {len(PROBES)} probe cases and {len(TARGETS)} target cases")

if __name__ == "__main__":
    main()
