#!/usr/bin/env python3
"""Reproducible battery generator for the R2 Module654 rule differential.

Writes battery.jsonl (JSONL {"id","source"}) next to this script. Each case
probes one shape in the [[module654 Name attr]] / [[/module]] matching space,
including the module654-vs-module distinction and the Wikidot closer policy
(Wikidot closes a module654 opener with [[/module]], never [[/module654]]).
Newlines, CRLF and lone CR are written as real control characters.
"""
import json
import os

CASES = [
    # --- name charset edges ---
    ("m654-name-basic", "[[module654 Rate]]\nbody\n[[/module]]"),
    ("m654-name-uppercase", "[[module654 RATE]]\nbody\n[[/module]]"),
    ("m654-name-mixed", "[[module654 rate]]\nbody\n[[/module]]"),
    ("m654-name-leading-digit", "[[module654 123abc]]\nbody\n[[/module]]"),
    ("m654-name-digits-only", "[[module654 654]]\nbody\n[[/module]]"),
    ("m654-name-slash", "[[module654 foo/bar]]\nbody\n[[/module]]"),
    ("m654-name-hyphen", "[[module654 foo-bar]]\nbody\n[[/module]]"),
    ("m654-name-leading-hyphen", "[[module654 -foo]]\nbody\n[[/module]]"),
    ("m654-name-underscore", "[[module654 foo_bar]]\nbody\n[[/module]]"),
    ("m654-name-leading-underscore", "[[module654 _foo]]\nbody\n[[/module]]"),
    ("m654-name-empty", "[[module654 ]]\nbody\n[[/module]]"),
    ("m654-name-no-space", "[[module654Rate]]\nbody\n[[/module]]"),
    ("m654-name-dot", "[[module654 foo.bar]]\nbody\n[[/module]]"),
    ("m654-name-unicode", "[[module654 \u00e9]]\nbody\n[[/module]]"),
    # --- attribute forms ---
    ("m654-attr-one", "[[module654 Rate show=\"x\"]]\nbody\n[[/module]]"),
    ("m654-attr-bare", "[[module654 Rate foo]]\nbody\n[[/module]]"),
    ("m654-attr-two", "[[module654 Rate a=\"1\" b=\"2\"]]\nbody\n[[/module]]"),
    ("m654-attr-quoted-space", "[[module654 Rate title=\"a b\"]]\nbody\n[[/module]]"),
    ("m654-attr-empty", "[[module654 Rate \"\"]]\nbody\n[[/module]]"),
    ("m654-attr-tab", "[[module654 Rate\tfoo=\"x\"]]\nbody\n[[/module]]"),
    ("m654-attr-multi-space", "[[module654 Rate   foo=\"x\"]]\nbody\n[[/module]]"),
    # --- body present / absent / empty ---
    ("m654-body-present", "[[module654 CSS]]\n.red { color: red; }\n[[/module]]"),
    ("m654-body-empty", "[[module654 CSS]]\n\n[[/module]]"),
    ("m654-body-absent", "[[module654 CSS]]"),
    ("m654-body-absent-newline", "[[module654 CSS]]\n"),
    ("m654-body-inline", "[[module654 Rate]]body[[/module]]"),
    ("m654-body-inline-empty", "[[module654 Rate]][[/module]]"),
    # --- unterminated / stray closer ---
    ("m654-unterminated", "[[module654 CSS]]\nbody"),
    ("m654-stray-closer", "before\n[[/module]]\nafter"),
    ("m654-stray-closer654", "before\n[[/module654]]\nafter"),
    ("m654-double-closer", "[[module654 CSS]]\nbody\n[[/module]]\n[[/module]]"),
    # --- opener newline variations ---
    ("m654-newline-none", "[[module654 CSS]]body\n[[/module]]"),
    ("m654-newline-spaces", "[[module654 CSS]]   \nbody\n[[/module]]"),
    ("m654-newline-crlf", "[[module654 CSS]]\r\nbody\r\n[[/module]]"),
    ("m654-newline-lone-cr", "[[module654 CSS]]\rbody\r[[/module]]"),
    ("m654-newline-two", "[[module654 CSS]]\n\nbody\n[[/module]]"),
    ("m654-newline-tab-space", "[[module654 CSS]]\t \nbody\n[[/module]]"),
    # --- case variations ---
    ("m654-case-opener-upper", "[[MODULE654 CSS]]\nbody\n[[/module]]"),
    ("m654-case-opener-mixed", "[[Module654 CSS]]\nbody\n[[/module]]"),
    ("m654-case-closer-upper", "[[module654 CSS]]\nbody\n[[/MODULE]]"),
    ("m654-case-closer-mixed", "[[module654 CSS]]\nbody\n[[/Module]]"),
    # --- mid-line / leading-space openers ---
    ("m654-midline", "text [[module654 CSS]]\nbody\n[[/module]]"),
    ("m654-leading-space", " [[module654 CSS]]\nbody\n[[/module]]"),
    ("m654-after-blank", "before\n\n[[module654 CSS]]\nbody\n[[/module]]"),
    # --- closer policy ---
    ("m654-closer-654", "[[module654 CSS]]\nbody\n[[/module654]]"),
    ("m654-closer-module", "[[module654 CSS]]\nbody\n[[/module]]"),
    ("m654-module-closer-654", "[[module CSS]]\nbody\n[[/module654]]"),
    # --- nesting / adjacency with Modulepre and Module ---
    ("m654-adjacent-module", "[[module654 CSS]]\n.a{}\n[[/module]]\n[[module Rate]]\n[[/module]]"),
    ("m654-nested-module", "[[module654 CSS]]\n[[module Rate]]\n[[/module]]\n[[/module]]"),
    ("m654-nested-654", "[[module654 CSS]]\n[[module654 Rate]]\n[[/module]]\n[[/module]]"),
    ("m654-module-then-654", "[[module Rate]]\n[[module654 CSS]]\n[[/module]]\n[[/module]]"),
    # --- module654-vs-module distinction (ftml pin shapes) ---
    ("m654-vs-module-unknown", "[[module654 UnknownOracleModule]]"),
    ("m654-vs-module-invalid-head", "[[module654 class=\"\"]]\nv7 body\n[[/module654]]"),
    ("m654-vs-module-tail", "[[module654 UnknownOracleModule]]TAIL"),
    ("m654-vs-module-sameclose", "[[module654 UnknownOracleModule]][[/module]]"),
    ("m654-vs-module-attr-unknown", "[[module654 UnknownOracleModule foo=\"bar\"]]"),
    ("m654-vs-module-newline-unknown", "[[module654 UnknownOracleModule]]\nbody\n[[/module]]"),
    # --- controls ---
    ("control-module-basic", "[[module Rate]]\n[[/module]]"),
    ("control-plain", "just plain text"),
]


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "battery.jsonl")
    with open(out, "w", encoding="utf-8") as fh:
        for cid, source in CASES:
            fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
    print(f"wrote {len(CASES)} cases to {out}")


if __name__ == "__main__":
    main()
