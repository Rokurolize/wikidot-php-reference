#!/usr/bin/env python3
"""Generate the Freelink R2 battery: 60 cases spanning opener/closer variants,
malformed and unterminated forms, target and label edges (empty, whitespace,
duplicate pipes, anchors, cross-site :: and : prefixes, URLs), case variation,
mid-line and line-start positions, and both existence polarities. Run from any
cwd; writes battery.jsonl next to this script."""
import json
import os

CASES = [
    # A. existence polarities and case variation against the root stub map
    ("exist-target-labeled", "[[[muse-probe-r2link-free-exists|shown]]]"),
    ("exist2-target-labeled", "[[[muse-probe-r2link-free-exists2|Second]]]"),
    ("exist-target-bare", "[[[muse-probe-r2link-free-exists]]]"),
    ("exist2-empty-label", "[[[muse-probe-r2link-free-exists2|]]]"),
    ("new-target-labeled", "[[[missing-page|Wanted]]]"),
    ("new-target-bare", "[[[missing-page]]]"),
    ("new-target-empty-label", "[[[missing-page|]]]"),
    ("case-upper-exists", "[[[MUSE-PROBE-R2LINK-FREE-EXISTS|shown]]]"),
    ("case-mixed-exists", "[[[MuSe-PrObE-r2LiNk-free-ExIsTs|shown]]]"),
    ("exist-target-anchor", "[[[muse-probe-r2link-free-exists#sec|shown]]]"),
    # B. opener/closer variations
    ("double-bracket", "[[some-page]]"),
    ("triple-quad", "[[[[SCP-001-EX]]]]"),
    ("triple-quint", "[[[[[SCP-001-EX]]]]]"),
    ("triple-short-closer", "[[[some-page]]"),
    ("triple-no-closer", "[[[some-page"),
    ("triple-closer-junk", "[[[some-page]]]junk"),
    ("triple-extra-close", "[[[some-page]]]]"),
    ("triple-space-opener", "[[[ some-page | Label ]]]"),
    ("double-open-triple-close", "[[some-page|Label]]]"),
    ("triple-open-double-close", "[[[some-page|Label]]"),
    # C. malformed and unterminated
    ("empty-target", "[[[|Label]]]"),
    ("whitespace-target", "[[[   |Label]]]"),
    ("empty-label", "[[[some-page|]]]"),
    ("dup-pipes", "[[[page-slug|A|B|C]]]"),
    ("dup-pipes-spaced", "[[[ page-slug | A | B | C ]]]"),
    ("triple-hash", "[[[home###|Home]]]"),
    ("double-hash", "[[[a##b]]]"),
    ("hash-route", "[[[MAIN/##/page#toc1|Hash routing]]]"),
    # D. anchors
    ("anchor-digit", "[[[scp-series#001|SCP-001 to SCP-099]]]"),
    ("anchor-alpha", "[[[scp-series#section|Label]]]"),
    ("anchor-label-only", "[[[#my-anchor|Label]]]"),
    ("anchor-label-only-space", "[[[ #my-anchor | Label ]]]"),
    ("anchor-empty-first", "[[[#my-anchor]]]"),
    ("anchor-dash", "[[[scp-series#sec-1|Label]]]"),
    ("anchor-underscore", "[[[scp-series#sec_1|Label]]]"),
    ("anchor-colon", "[[[scp-series#sec:1|Label]]]"),
    # E. cross-site, category, colon shapes
    ("cross-site-colon", "[[[:scp-wiki:component:theme|Sigma-9 Theme]]]"),
    ("cross-site-colon-spaced", "[[[:scp-wiki : system : Recent Changes]]]"),
    ("fossil-cross-site", "[[[site::page|Label]]]"),
    ("fossil-cross-site-no-page", "[[[site::|Label]]]"),
    ("category", "[[[system:Recent Changes]]]"),
    ("category-spaced", "[[[system: Recent Changes]]]"),
    ("multi-colon-empty", "[[[a:b:c|]]]"),
    ("default-category", "[[[_default:a|Label]]]"),
    # F. URL targets and leading/trailing space
    ("url-plain", "[[[https://example.com/|Example]]]"),
    ("url-leading-space", "[[[ https://example.com/ | Example ]]]"),
    ("url-trailing-space", "[[[https://example.com | Trailing]]]"),
    ("url-no-scheme", "[[[example.com|Example]]]"),
    ("url-subpath", "[[[example/edit|Edit page]]]"),
    ("url-hash-route", "[[[MAIN/#/page|Hash routing]]]"),
    # G. positions, star/underscore, unicode
    ("line-start", "[[[some-page|Line start]]]"),
    ("mid-line", "text before [[[some-page|Mid line]]] text after"),
    ("second-line", "first line\n[[[some-page|Second line]]]"),
    ("inline-two", "[[[a|A]]] and [[[b|B]]]"),
    ("adjacent-freelinks", "[[[a|A]]][[[b|B]]]"),
    ("star-target", "[[[*SCP-001]]]"),
    ("star-labeled", "[[[*some-page|Label]]]"),
    ("underscore-target", "[[[_some-page|Label]]]"),
    ("unicode-cyrillic", "[[[документ]]]"),
    ("unicode-cjk", "[[[日本語|Label]]]"),
]

def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "battery.jsonl")
    with open(out, "w", encoding="utf-8") as fh:
        for cid, source in CASES:
            fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
    print(f"wrote {len(CASES)} cases to {out}")

if __name__ == "__main__":
    main()
