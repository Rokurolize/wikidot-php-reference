#!/usr/bin/env python3
"""Generate the R2-next Math differential battery (battery.jsonl).

Each record is {"id": ..., "source": ...} for the shared harness batch.php
(render / tokens) and the shared ftml dumper. Sources are LF-only. The
categories are line-start versus inline openers, label charset/case/empties,
type and other attributes, body newlines and trailing whitespace, nesting and
recursion, malformed and unterminated forms, \\include/\\input bodies, and
adjacency with neighbouring rules in pipeline order.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "battery.jsonl")

# (id, source). Keep each source explicit; no generation tricks that could
# hide a byte-level difference from the reader.
CASES = [
    # --- line-start vs inline openers ------------------------------------
    ("basic", "[[math E]]\nx=1\n[[/math]]"),
    ("opener-no-label", "[[math]]\nx\n[[/math]]"),
    ("opener-after-text", "intro\n[[math]]\nx\n[[/math]]"),
    ("opener-midline", "prefix [[math]]\nx\n[[/math]]"),
    ("opener-leading-space", " [[math]]\nx\n[[/math]]"),
    ("opener-leading-tab", "\t[[math]]\nx\n[[/math]]"),
    ("opener-no-space", "[[mathE]]\nx\n[[/math]]"),
    ("opener-trailing-space", "[[math E ]]\nx\n[[/math]]"),
    ("opener-spaces-before-nl", "[[math E]]   \nx\n[[/math]]"),
    ("opener-tab-before-nl", "[[math E]]\t\nx\n[[/math]]"),
    ("opener-crlf", "[[math E]]\r\nx\r\n[[/math]]\r\n"),
    ("opener-blank-line-before", "\n[[math]]\nx\n[[/math]]"),

    # --- label charset, case, empties -----------------------------------
    ("label-upper", "[[MATH Upper]]\nx\n[[/MATH]]"),
    ("label-title", "[[Math Title]]\nx\n[[/Math]]"),
    ("label-digits", "[[math 123]]\nx\n[[/math]]"),
    ("label-underscore", "[[math a_b]]\nx\n[[/math]]"),
    ("label-mixed-case", "[[math Ab_C9]]\nx\n[[/math]]"),
    ("label-hyphen", "[[math a-b]]\nx\n[[/math]]"),
    ("label-dot", "[[math a.b]]\nx\n[[/math]]"),
    ("label-nonascii", "[[math étude]]\nx\n[[/math]]"),
    ("label-empty-spaces", "[[math   ]]\nx\n[[/math]]"),
    ("label-equals", "[[math a=b]]\nx\n[[/math]]"),
    ("label-two-words", "[[math a b]]\nx\n[[/math]]"),
    ("label-quoted", "[[math \"a\" type=\"align\"]]\nx\n[[/math]]"),

    # --- type and other head attributes ---------------------------------
    ("type-equation", "[[math type=\"equation\"]]\nx\n[[/math]]"),
    ("type-eqnarray", "[[math type=\"eqnarray\"]]\nx\n[[/math]]"),
    ("type-align", "[[math type=\"align\"]]\nx\n[[/math]]"),
    ("type-gather", "[[math a type=\"gather\"]]\nx\n[[/math]]"),
    ("type-not-last", "[[math type=\"align\" foo=\"bar\"]]\nx\n[[/math]]"),
    ("type-uppercase", "[[math type=\"ALIGN\"]]\nx\n[[/math]]"),
    ("type-unquoted", "[[math type=align]]\nx\n[[/math]]"),
    ("type-single-quote", "[[math type='align']]\nx\n[[/math]]"),
    ("type-spaces-eq", "[[math type = \"align\"]]\nx\n[[/math]]"),
    ("type-empty", "[[math type=\"\"]]\nx\n[[/math]]"),
    ("attr-unknown", "[[math foo=\"bar\"]]\nx\n[[/math]]"),
    ("attr-hyphen-key", "[[math foo-bar=\"x\"]]\nx\n[[/math]]"),
    ("attr-underscore-key", "[[math foo_bar=\"x\"]]\nx\n[[/math]]"),
    ("attr-label-and-type", "[[math E type=\"eqnarray\" foo=\"x\"]]\nx\n[[/math]]"),
    ("attr-quoted-close-bracket", "[[math a=\"x]]y\"]\nz\n[[/math]]"),

    # --- body newlines and trailing whitespace --------------------------
    ("body-leading-blank", "[[math]]\n\nx\n[[/math]]"),
    ("body-trailing-blank", "[[math]]\nx\n\n[[/math]]"),
    ("body-spaces", "[[math]]\n  x + y  \n[[/math]]"),
    ("body-multiline", "[[math]]\nx = 1\ny = 2\n[[/math]]"),
    ("body-empty", "[[math]]\n[[/math]]"),
    ("body-whitespace-only", "[[math]]\n   \n[[/math]]"),
    ("closer-trailing-spaces", "[[math]]\nx\n[[/math]]   \n"),
    ("closer-trailing-tab", "[[math]]\nx\n[[/math]]\t\n"),
    ("closer-tail-text", "[[math]]\nx\n[[/math]] tail\n"),
    ("closer-eof-no-nl", "[[math]]\nx\n[[/math]]"),
    ("closer-inline", "[[math]]x[[/math]]"),
    ("closer-case-upper", "[[math]]\nx\n[[/MATH]]"),
    ("closer-blankline-tail", "[[math]]\nx\n[[/math]]\n\ntail\n"),

    # --- nesting / recursion / malformed / unterminated -----------------
    ("nested-two", "[[math]]\n[[math]]\nx\n[[/math]]\n[[/math]]"),
    ("nested-outer-tail", "[[math]]\n[[math]]\nx\n[[/math]] tail\n[[/math]]"),
    ("nested-labels", "[[math A]]\n[[math B]]\nx\n[[/math]]\n[[/math]]"),
    ("adjacent-two-blocks", "[[math]]\nx\n[[/math]]\n[[math]]\ny\n[[/math]]"),
    ("stray-closer", "x\n[[/math]]\n"),
    ("unterminated", "[[math]]\nx\n"),
    ("unterminated-outer", "[[math]]\n[[math]]\nx\n[[/math]]\n"),

    # --- \\include / \\input bodies -------------------------------------
    ("include-brace", "[[math]]\n\\include{foo}\n[[/math]]"),
    ("input-brace", "[[math]]\n\\input{foo}\n[[/math]]"),
    ("include-space", "[[math]]\n\\include foo\n[[/math]]"),
    ("input-space", "[[math]]\n\\input bar\n[[/math]]"),
    ("include-in-word", "[[math]]\nx\\include{y}\n[[/math]]"),
    ("include-uppercase", "[[math]]\n\\Include{foo}\n[[/math]]"),
    ("include-in-label-block", "[[math E]]\n\\include{foo}\n[[/math]]"),

    # --- adjacency with neighbouring rules in pipeline order -----------
    ("after-comment", "[!-- hidden --]\n[[math]]\nx\n[[/math]]"),
    ("comment-in-body", "[[math]]\n[!-- [[/math]] --]\nx\n[[/math]]"),
    ("after-date", "[[date 1216153821]]\n[[math]]\nx\n[[/math]]"),
    ("eref-after", "[[math E]]\nx\n[[/math]]\n[[eref E]]"),
    ("eref-before", "[[eref E]]\n[[math E]]\nx\n[[/math]]"),
    ("mathinline-after", "[[math]]\nx\n[[/math]]\n[[$ y $]]"),
    ("in-div", "[[div class=\"box\"]]\n[[math]]\nx\n[[/math]]\n[[/div]]"),
    ("in-blockquote", "> [[math]]\n> x\n> [[/math]]\n"),
    ("in-collapsible", "[[collapsible]]\n[[math]]\nx\n[[/math]]\n[[/collapsible]]"),
    ("in-iftags", "[[iftags poll]]\n[[math]]\nx\n[[/math]]\n[[/iftags]]"),
]


def main():
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        for name, source in CASES:
            fh.write(json.dumps({"id": name, "source": source},
                                ensure_ascii=False) + "\n")
    print(f"wrote {len(CASES)} cases to {OUT}")


if __name__ == "__main__":
    main()
