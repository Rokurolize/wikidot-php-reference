#!/usr/bin/env python3
"""Regenerate conformance-refphp/module/modulepre/battery.jsonl.

One case per JSON line: {"id": <str>, "source": <str>}. Cases exercise the
Modulepre prefilter's matching space: it is the pre-module rule whose regex
/^\\[\\[module654\\s([a-z0-9_\\-\\/]+)(\\s+.*?)?\\]\\](?:(.*?)\\[\\[\\/module\\]\\])?/ims
rewrites a leading `[[module654` to `[[module` so the downstream Module rule
can claim it. Every shape that turns on the name charset, attribute tail,
opener newline, body/closer presence, case, line position, and the
module654-vs-module distinction is represented. Deterministic: same ids and
sources on every run.
"""
import json
from pathlib import Path

CASES = []


def add(cid, source):
    CASES.append((cid, source))


CSS_BODY = ".mp-box { color: red; }"

# --- name charset edges -------------------------------------------------
add("mp-name-lower", "[[module654 backlinks]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-name-upper", "[[module654 CSS]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-name-mixed", "[[module654 RaTe]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-name-leading-digit", "[[module654 9lives]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-name-slash", "[[module654 foo/bar]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-name-hyphen", "[[module654 my-module]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-name-underscore", "[[module654 my_module]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-name-empty", "[[module654 ]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-name-dot", "[[module654 foo.bar]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-name-colon", "[[module654 foo:bar]]\n" + CSS_BODY + "\n[[/module]]")

# --- attribute forms ----------------------------------------------------
add("mp-attr-simple", '[[module654 rate show="mp-x"]]')
add("mp-attr-multiple", '[[module654 listpages category="cats" limit="5"]]\nbody\n[[/module]]')
add("mp-attr-unquoted", "[[module654 rate show=mp-x]]")
add("mp-attr-empty", '[[module654 rate ""]]')
add("mp-attr-newline", '[[module654 rate\nshow="mp-x"]]')
add("mp-attr-brackets", '[[module654 rate a="x]]y"]]')
add("mp-attr-spaces", '[[module654 rate   show="mp-x"   ]]\nbody\n[[/module]]')

# --- body present / absent / empty --------------------------------------
add("mp-body-basic", "[[module654 css]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-body-empty", "[[module654 css]]\n[[/module]]")
add("mp-body-absent", "[[module654 css]]")
add("mp-body-inline", "[[module654 css]]inline-body[[/module]]")
add("mp-body-blank-lines", "[[module654 css]]\n\n\n" + CSS_BODY + "\n\n[[/module]]")
add("mp-body-punctuation", "[[module654 css]]\n***bold*** and [[div]]\n[[/module]]")

# --- unterminated and stray closers -------------------------------------
add("mp-unterm", "[[module654 css]]\n" + CSS_BODY)
add("mp-stray-closer", "[[/module]]")
add("mp-closer-654", "[[/module654]]")
add("mp-unterm-then-text", "[[module654 css]]\n" + CSS_BODY + "\nTRAILING")
add("mp-close-then-open", "[[/module]]\n[[module654 css]]\n" + CSS_BODY + "\n[[/module]]")

# --- opener newline variations ------------------------------------------
add("mp-nl-none", "[[module654 css]]text")
add("mp-nl-spaces", "[[module654 css]]   \n" + CSS_BODY + "\n[[/module]]")
add("mp-nl-tabs", "[[module654 css]]\t\n" + CSS_BODY + "\n[[/module]]")
add("mp-nl-crlf", "[[module654 css]]\r\n" + CSS_BODY + "\r\n[[/module]]")
add("mp-nl-cr", "[[module654 css]]\r" + CSS_BODY + "\r[[/module]]")
add("mp-nl-two", "[[module654 css]]\n\n" + CSS_BODY + "\n[[/module]]")
add("mp-nl-eof", "[[module654 css]]\n")

# --- case variations ----------------------------------------------------
add("mp-case-ALL", "[[MODULE654 CSS]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-case-mixed", "[[Module654 CSS]]\n" + CSS_BODY + "\n[[/MODULE]]")
add("mp-case-closer", "[[module654 CSS]]\n" + CSS_BODY + "\n[[/MODULE654]]")

# --- opener position ----------------------------------------------------
add("mp-midline", "prefix [[module654 css]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-leading-space", " [[module654 css]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-leading-space2", "  [[module654 css]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-quoted", "> [[module654 CSS]]\n> " + CSS_BODY + "\n> [[/module]]")

# --- nesting / adjacency ------------------------------------------------
add("mp-adjacent-module", "[[module654 css]]\n" + CSS_BODY + "\n[[/module]]\n[[module rate]]")
add("mp-nested-module-in-654", "[[module654 css]]\n[[module rate]]\n[[/module]]")
add("mp-nested-654-in-module", "[[module css]]\n[[module654 rate]]\n[[/module]]")
add("mp-654-body-has-module-closer", "[[module654 css]]\n[[module rate]]\n[[/module]]\n[[/module]]")
add("mp-two-654", "[[module654 css]]\nA\n[[/module]]\n[[module654 rate]]\nB\n[[/module]]")

# --- module654-vs-module distinction ------------------------------------
add("mp-vs-module-baseline", "[[module CSS]]\n" + CSS_BODY + "\n[[/module]]")
add("mp-vs-module-nonewline", "[[module CSS]]text")
add("mp-vs-654-nonewline", "[[module654 CSS]]text")
add("mp-vs-654-closer-654", "[[module654 CSS]]\n" + CSS_BODY + "\n[[/module654]]")

# --- unknown module names -----------------------------------------------
add("mp-unknown-name", "[[module654 UnknownOracleModule]]")
add("mp-unknown-with-body", "[[module654 UnknownOracleModule]]\nbody\n[[/module]]")
add("mp-unknown-no-newline", "[[module654 UnknownOracleModule]]TAIL")
add("mp-unknown-attrs", '[[module654 UnknownOracleModule foo="bar"]]')


def main():
    out = Path(__file__).with_name("battery.jsonl")
    with out.open("w", encoding="utf-8") as fh:
        for cid, source in CASES:
            fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
    ids = [cid for cid, _ in CASES]
    assert len(ids) == len(set(ids)), "duplicate ids"
    print(f"wrote {len(CASES)} cases to {out}")


if __name__ == "__main__":
    main()
