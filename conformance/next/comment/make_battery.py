#!/usr/bin/env python3
"""Build the R2-next Comment battery and the live probe case list.

Outputs battery.jsonl (full local differential battery) and probe-cases.jsonl
(the subset taken to a saved Wikidot page). All sources are LF-only with
trailing newlines stripped except the cases that deliberately carry CR/CRLF
or a trailing newline: those are local-only, because Wikidot normalizes line
endings and trailing newlines on save.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# (id, source) pairs. The id prefix encodes the coverage group.
CASES = [
    # op / close / body shapes
    ("op-basic-inline", "a[!-- hidden --]b"),
    ("op-basic-line-start", "[!-- hidden --]\nvisible"),
    ("op-basic-line-end", "visible\n[!-- hidden --]"),
    ("op-empty", "a[!-- --]b"),
    ("op-no-space", "a[!--x--]b"),
    ("op-whitespace-body", "a[!--   \n  --]b"),
    ("op-close-three-hyphens", "a[!-- hidden ---]b"),
    ("op-close-four-hyphens", "a[!-- hidden ----]b"),
    ("op-close-five-hyphens", "a[!-- hidden -----]b"),
    ("op-hyphen-run-open-close", "a[!----\nhidden\n---]\nb"),
    ("op-unmatched-closer", "a--]b"),
    ("op-unterminated", "a[!-- hidden b"),
    ("op-unterminated-line", "a\n[!-- hidden\nb"),
    ("op-two-openers-one-closer", "a[!-- one [!-- two --]b"),
    # optional leading newline and line position
    ("nl-leading-one", "a\n[!-- c --]b"),
    ("nl-leading-two", "a\n\n[!-- c --]b"),
    ("nl-comment-only-line", "a\n[!-- c --]\nb"),
    ("nl-comment-only-blank-around", "a\n\n[!-- c --]\n\nb"),
    ("nl-comment-at-eof", "a\n[!-- c --]"),
    ("nl-comment-at-start-tail", "[!-- c --] z"),
    ("nl-comment-at-start-only", "[!-- c --]"),
    ("nl-indented-spaces", "a\n  [!-- c --]\nb"),
    ("nl-indented-tab", "a\n\t[!-- c --]\nb"),
    ("nl-trailing-newline-local", "a[!-- c --]b\n"),
    # multiline, nesting, adjacency
    ("ml-body", "a[!-- line1\nline2 --]b"),
    ("ml-line-start", "a\n[!-- line1\nline2 --]\nb"),
    ("ml-nested", "a[!-- outer [!-- inner --] tail --]b"),
    ("ml-adjacent", "a[!-- one --][!-- two --]b"),
    ("ml-chained-lines", "[!-- one --]\n[!-- two --]\nb"),
    ("ml-span-with-block-syntax", "a[!-- [[div]]x[[/div]] --]b"),
    ("ml-span-with-module-opener", "a[!-- [[module X]] --]b"),
    ("ml-span-with-math-opener", "a[!-- [[math]] --]\nx"),
    # case variations
    ("case-upper-body", "a[!-- HIDDEN --]b"),
    ("case-mixed-body", "a[!-- HiDdEn --]b"),
    ("case-opener-word", "a[!COMMENT hidden --]b"),
    ("case-close-word", "a[!-- hidden --COMMENT]b"),
    # CRLF and lone CR (local only)
    ("crlf-inline", "a[!-- c --]\r\nb"),
    ("crlf-line-start", "a\r\n[!-- c --]\r\nb"),
    ("crlf-multiline-body", "a[!-- x\r\ny --]b"),
    ("cr-only-inline", "a[!-- c --]\rb"),
    ("cr-only-line", "a\r[!-- c --]\rb"),
    # adjacency with neighbours in pipeline order
    ("adj-before-iframe", "[!-- hide --]\n[[iframe https://example.com]]"),
    ("adj-hide-iframe", "a[!-- [[iframe https://example.com]] --]b"),
    ("adj-before-date", "[!-- hide --]\n[[date 0]]"),
    ("adj-before-heading", "[!-- c --]\n= Heading ="),
    ("adj-before-list", "[!-- c --]\n* item"),
    ("adj-before-div", "[!-- c --]\n[[div class=\"x\"]]\nT\n[[/div]]"),
    ("adj-inside-code", "[[code]]\nA[!-- c --]B\n[[/code]]"),
    ("adj-inside-raw", "@@A[!-- c --]B@@"),
    ("adj-inside-span-head", "[[span [!--x--] class=\"c\"]]T[[/span]]"),
    ("adj-span-with-iftags-head", "[!-- [[iftags +x]] --]\nbody"),
    # ftml corpus pin shapes (test/comment and test/paragraph pins)
    ("pin-double-bracket-head", "[[!-- Theme Lab candidate port header. --]]\nBody paragraph."),
    ("pin-double-bracket-inline", "Before [[!-- note --]] after."),
    ("pin-double-bracket-only-line", "Line one\n[[!-- note --]]\nLine two"),
    ("pin-paragraph-single-break", "A\n[!-- x --]\nB"),
    ("pin-paragraph-line-final", "A\n[!-- x --]"),
    ("pin-comment-line-break-demotion", "x\n\n[!-- c --] \nz"),
    ("pin-comment-line-splice", "x\n[!-- c --] z"),
    ("pin-list-comment-line-start", "[!--x--]* item\n[!--a--][!--b--]# item"),
    ("pin-code-closer-comment-suffix", "[[code]]\nbody\n[[/code]][!-- c --]"),
    ("pin-double-bracket-in-block-head", "a[[span [!-- x --]]] b[[/span]]c"),
    ("pin-double-bracket-before-name", "[[[!--x--]span class=\"c\"]]x[[/span]]"),
]

# Live probe subset. Every source here is LF-only with trailing newlines
# stripped, because Wikidot normalizes line endings and trailing newlines
# on save; the CR/CRLF and trailing-newline battery cases stay local.
PROBE_IDS = [
    "op-basic-inline",
    "op-basic-line-start",
    "op-basic-line-end",
    "op-empty",
    "op-no-space",
    "op-close-three-hyphens",
    "op-close-five-hyphens",
    "op-unmatched-closer",
    "op-unterminated",
    "nl-leading-one",
    "nl-comment-only-line",
    "nl-comment-only-blank-around",
    "nl-comment-at-start-tail",
    "nl-indented-spaces",
    "ml-body",
    "ml-nested",
    "ml-adjacent",
    "case-upper-body",
    "adj-before-iframe",
    "adj-hide-iframe",
    "adj-before-heading",
    "adj-before-list",
    "adj-inside-code",
    "adj-inside-raw",
    "pin-double-bracket-head",
    "pin-double-bracket-inline",
    "pin-double-bracket-only-line",
    "pin-paragraph-single-break",
]


def main():
    by_id = dict(CASES)
    assert len(by_id) == len(CASES), "duplicate battery id"
    with open(os.path.join(HERE, "battery.jsonl"), "w", encoding="utf-8") as fh:
        for cid, source in CASES:
            fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
    with open(os.path.join(HERE, "probe-cases.jsonl"), "w", encoding="utf-8") as fh:
        for cid in PROBE_IDS:
            source = by_id[cid]
            assert "\r" not in source and not source.endswith("\n"), cid
            fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
    print("battery", len(CASES), "probes", len(PROBE_IDS))


if __name__ == "__main__":
    main()
