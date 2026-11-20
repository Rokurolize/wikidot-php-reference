#!/usr/bin/env python3
"""Reproducible battery + live-probe case generator for the R2 Module rule.

Run from anywhere:  python3 make_battery.py
Writes battery.jsonl (>=40 {"id","source"} cases) and probe-cases.jsonl (the
focused subset whose rendered shape is settled by live saved-page probes) next
to this script. All sources are literal; the CRLF / lone-CR cases deliberately
embed control characters so line-ending normalization by the harness and by
ftml can be compared.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

CASES = [
    # --- basic names, known/unknown, case ------------------------------------
    ("mod-basic", "[[module backlinks]]\n"),
    ("mod-known-uppercase", "[[module BACKLINKS]]\n"),
    ("mod-known-mixed", "[[module BackLinks]]\n"),
    ("mod-unknown", "[[module UnknownOracleModule]]\n"),
    ("mod-unknown-mixed", "[[module Unknown_Oracle-2]]\n"),
    # --- name charset edges --------------------------------------------------
    ("mod-name-leading-digit", "[[module 123abc]]\n"),
    ("mod-name-leading-underscore", "[[module _foo]]\n"),
    ("mod-name-leading-hyphen", "[[module -foo]]\n"),
    ("mod-name-slash", "[[module foo/bar]]\n"),
    ("mod-name-inner-slash", "[[module foo/bar-baz_qux]]\n"),
    ("mod-name-hyphen", "[[module foo-bar]]\n"),
    ("mod-name-underscore", "[[module foo_bar]]\n"),
    ("mod-name-uppercase-unknown", "[[module FOO_BAR]]\n"),
    ("mod-name-empty-space", "[[module ]]\n"),
    ("mod-name-empty-nospace", "[[module]]\n"),
    # --- attribute forms -----------------------------------------------------
    ("mod-attr-quoted", '[[module rate show="foo"]]\n'),
    ("mod-attr-unquoted", "[[module rate show=foo]]\n"),
    ("mod-attr-empty", '[[module rate show=""]]\n'),
    ("mod-attr-multiple", '[[module pagetree root="scp-001" depth="2"]]\n'),
    ("mod-attr-on-unknown", '[[module UnknownOracleModule foo="bar"]]\n'),
    ("mod-attr-extra-spaces", '[[module rate   show="foo"  ]]\n'),
    # --- body present / absent / empty / malformed ---------------------------
    ("mod-body-present", "[[module css]]\n.blue { color: blue; }\n[[/module]]\n"),
    ("mod-body-empty", "[[module css]]\n[[/module]]\n"),
    ("mod-body-inline-unknown", "[[module UnknownOracleModule]]preserved body[[/module]]\n"),
    ("mod-body-unknown-newline", "[[module UnknownOracleModule]]\nbody\n[[/module]]\n"),
    ("mod-unterminated", "[[module css]]\n.blue{color:blue}\n"),
    ("mod-stray-closer", "[[/module]]\n"),
    ("mod-body-same-line", "[[module css]] body [[/module]]\n"),
    # --- opener newline variations ------------------------------------------
    ("mod-no-newline", "[[module backlinks]]"),
    ("mod-spaces-then-newline", "[[module backlinks]]   \n"),
    ("mod-crlf", "[[module backlinks]]\r\n"),
    ("mod-lone-cr", "[[module backlinks]]\r"),
    ("mod-tab-after-opener", "[[module backlinks]]\t\n"),
    # --- case variations -----------------------------------------------------
    ("mod-opener-MODULE", "[[MODULE backlinks]]\n"),
    ("mod-opener-mixed", "[[Module backlinks]]\n"),
    ("mod-closer-case", "[[module css]]\nbody\n[[/MODULE]]\n"),
    # --- mid-line and leading-space openers ---------------------------------
    ("mod-midline", "prefix [[module backlinks]]\n"),
    ("mod-leading-space", "[[ module backlinks ]]\n"),
    ("mod-closer-leading-space", "[[module css]]\nbody\n [[/module]]\n"),
    # --- self-nesting defense ------------------------------------------------
    ("mod-nested-two-openers", "[[module css]]\n[[module rate]]\n[[/module]]\n"),
    ("mod-nested-unknown-in-body", "[[module UnknownOracleModule]]\n[[module css]]\n[[/module]]\n"),
    # --- module654 adjacency and distinction --------------------------------
    ("mod-adjacent-module654", "[[module backlinks]]\n[[module654 rate]]\n"),
    ("mod-module654-basic", "[[module654 rate]]\n"),
    ("mod-module654-unknown", "[[module654 UnknownOracleModule]]\n"),
    ("mod-module654-module-closer", "[[module654 css]]\nbody\n[[/module]]\n"),
    ("mod-module-opener-module654-closer", "[[module css]]\nbody\n[[/module654]]\n"),
    # --- adjacency / composition / invalid heads ----------------------------
    ("mod-two-adjacent", "[[module backlinks]]\n[[module rate]]\n"),
    ("mod-unknown-tail", "[[module UnknownOracleModule]]TAIL"),
    ("mod-unknown-stray-close", "[[module UnknownOracleModule]][[/module]]"),
    ("mod-invalid-head-quoted", '[[module foo="bar"]]\n'),
    ("mod-two-adjacent-body", "[[module css]]\n[[/module]]\n[[module rate]]\n[[/module]]\n"),
    ("mod-blank-lines", "\n[[module backlinks]]\n\n"),
]

# Focused subset for live saved-page probes: the shapes the battery cannot
# settle from ftml pins alone (error text, malformed boundaries, name edges,
# module654 forms, nesting, invalid heads, known-module display shape).
PROBE_IDS = [
    "mod-unknown",
    "mod-unknown-mixed",
    "mod-name-leading-digit",
    "mod-name-leading-underscore",
    "mod-name-slash",
    "mod-name-empty-space",
    "mod-attr-on-unknown",
    "mod-invalid-head-quoted",
    "mod-no-newline",
    # mod-spaces-then-newline is intentionally battery-only: Wikidot strips
    # the trailing spaces on save, so it cannot pass read-back verification.
    "mod-stray-closer",
    "mod-midline",
    "mod-leading-space",
    "mod-body-inline-unknown",
    "mod-body-unknown-newline",
    "mod-basic",
    "mod-body-present",
    ("mod-probe-module654-basic", "[[module654 UnknownOracleModule]]\n"),
    ("mod-probe-nested", "[[module css]]\n[[module rate]]\n[[/module]]\n"),
    ("mod-probe-unknown-empty-body", "[[module UnknownOracleModule]]\n[[/module]]\n"),
    ("mod-probe-known-empty-body", "[[module rate]]\n[[/module]]\n"),
]


def main():
    with open(os.path.join(HERE, "battery.jsonl"), "w", encoding="utf-8") as fh:
        for cid, source in CASES:
            fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
    with open(os.path.join(HERE, "probe-cases.jsonl"), "w", encoding="utf-8") as fh:
        for entry in PROBE_IDS:
            if isinstance(entry, tuple):
                cid, source = entry
            else:
                cid, source = next(c for c in CASES if c[0] == entry)
            # Wikidot's save normalizes a trailing newline away; probe sources
            # must be byte-identical to the stored source, so drop it here.
            source = source[:-1] if source.endswith("\n") else source
            fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
    print(f"wrote battery.jsonl ({len(CASES)} cases) and "
          f"probe-cases.jsonl ({len(PROBE_IDS)} cases)")


if __name__ == "__main__":
    main()
