#!/usr/bin/env python3
"""Generate the R2 List rule battery: whole-document Wikidot-source cases.

Sources are LF-only with trailing newlines stripped, matching what Wikidot
normalizes on save. The optional tags field is accepted by both the shared
reference harness and the shared ftml dumper.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "battery.jsonl")

CASES = [
    # --- basic runs -------------------------------------------------------
    ("l01-bullet-single", "* one", []),
    ("l02-number-single", "# one", []),
    ("l03-bullet-three", "* one\n* two\n* three", []),
    ("l04-number-three", "# one\n# two\n# three", []),
    ("l05-no-final-newline", "* alpha\n* beta", []),
    ("l06-inline-markup", "* **bold** and //italic// and [[b]]tag[[/b]]", []),
    ("l07-long-item", "* a fairly long item with several words and punctuation, including a comma", []),

    # --- depth changes ----------------------------------------------------
    ("d01-child-step", "* one\n * two\n* three", []),
    ("d02-two-levels", "* one\n * two\n  * three\n* four", []),
    ("d03-three-levels", "* one\n * two\n  * three\n   * four", []),
    ("d04-skip-one-level", "* root\n  * skipped\n* after", []),
    ("d05-skip-three-levels", "* root\n    # skipped three\n* after", []),
    ("d06-return-to-root", "* one\n * two\n  * three\n* four", []),
    ("d07-partial-return", "* one\n * two\n  * three\n * four\n* five", []),
    ("d08-sibling-sublists", "* first\n # a\n* second\n # b", []),
    ("d09-descending", "   * four\n  * three\n * two\n* one", []),
    ("d10-tab-indent", "* root\n\t* tab child\n* after", []),
    ("d11-indented-first", "  * indented first\n* second", []),
    ("d12-too-deep-first", "                     * too deep", []),
    ("d13-deep-then-root", "* a\n  # b\n    * c\n  # d\n* e", []),

    # --- marker type changes and mixed nesting ----------------------------
    ("m01-root-switch", "* apple\n* banana\n# celery\n# kale\n* cherry", []),
    ("m02-root-switch-number-first", "# apple\n# banana\n* celery\n* kale\n# cherry", []),
    ("m03-child-switch", "* apple\n * banana\n * cherry\n* mango\n # lettuce\n # spinach\n* pineapple", []),
    ("m04-child-switch-deeper", "* A\n * B\n  # 1\n  # 2\n * C\n* D", []),
    ("m05-switch-and-return", "* a\n # b\n  * c\n # d\n* e", []),
    ("m06-same-depth-child-markers", "* a\n * b\n # c\n * d", []),
    ("m07-blank-between-runs", "* apple\n\n* banana\n\n\n* cherry\n* mango", []),
    ("m08-adjacent-runs", "* a\n# b\n* c", []),

    # --- empty items and the empty-container family -----------------------
    ("z01-empty-bullet", "* ", []),
    ("z02-empty-number", "# ", []),
    ("z03-empty-between", "* a\n* \n* b", []),
    ("z04-all-empty", "* \n* \n* ", []),
    ("z05-whitespace-only", "* a\n*  \t \n* b", []),
    ("z06-empty-parent", "* \n * child\n* after", []),
    ("z07-empty-nested-parent", "* root\n * \n  * grandchild\n* after", []),
    ("z08-empty-at-end", "* a\n* b\n* ", []),
    ("z09-empty-at-start", "* \n* b", []),

    # --- content, continuation and interruption ---------------------------
    ("b01-list-then-paragraph", "* a\n* b\n\ntext after", []),
    ("b02-paragraph-then-list", "text before\n* a\n* b", []),
    ("b03-continuation-lines", "* mango _\nmelon _\npineapple\n* pear", []),
    ("b04-interrupted-by-heading", "* a\n* b\n+ Heading\ntext", []),
    ("b05-interrupted-by-quote", "* a\n> quote\n* b", []),
    ("b06-interrupted-by-code", "* a\n{{ code }}\n* b", []),
    ("b07-item-with-link", "* see [http://example.com the site]\n* next", []),
    ("b08-list-hr-list", "* a\n\n----\n\n* b", []),
    ("b09-interrupted-by-div", "* a\n[[div class=\"x\"]]\ninner\n[[/div]]\n* b", []),
    ("b10-continuation-blank", "* a\n\nsecond paragraph inside item\n* b", []),

    # --- malformed and literal forms --------------------------------------
    ("x01-no-space-star", "*No space", []),
    ("x02-no-space-hash", "#No space", []),
    ("x03-two-spaces-after-marker", "*  two spaces", []),
    ("x04-midline-marker", "text * not a marker", []),
    ("x05-quoted-marker", "> * quoted marker", []),
    ("x06-double-star", "**bold**", []),
    ("x07-hash-alone", "#", []),
    ("x08-space-then-blank", "* a\n \n* b", []),

    # --- unterminated runs ------------------------------------------------
    ("u01-unterminated-bullet", "* a\n* b", []),
    ("u02-unterminated-nested", "* a\n * b\n  * c", []),
    ("u03-unterminated-then-blank", "* a\n* b\n", []),
    ("u04-unterminated-number", "# one\n # two", []),
]


def main():
    with open(OUT, "w", encoding="utf-8", newline="\n") as handle:
        for cid, source, tags in CASES:
            rec = {"id": cid, "source": source.rstrip("\n")}
            if tags:
                rec["tags"] = tags
            handle.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("wrote", len(CASES), "cases to", OUT)


if __name__ == "__main__":
    main()
