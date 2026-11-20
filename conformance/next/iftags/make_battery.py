#!/usr/bin/env python3
"""Generate the R2-next Iftags differential battery.

Each case is {"id", "source"} plus an optional "tags" array. The shared
reference harness (ref-php/harness/batch.php) injects that array as a tagged
RefPage, and the shared ftml dumper feeds the same array into PageInfo.tags,
so both tag polarities are deterministic. `note` is stripped from the emitted
JSONL and exists only to document intent here. Prose is on single lines.
"""
import json
import pathlib

CASES = [
    # --- basic openers, closers, and tag polarities ---
    dict(id="basic-plus-hit", source="[[iftags +alpha]]KEEP[[/iftags]]", tags=["alpha"], note="required tag present"),
    dict(id="basic-plus-miss", source="[[iftags +alpha]]KEEP[[/iftags]]", tags=["beta"], note="required tag absent"),
    dict(id="basic-minus-hit", source="[[iftags -alpha]]KEEP[[/iftags]]", tags=["beta"], note="forbidden tag absent"),
    dict(id="basic-minus-miss", source="[[iftags -alpha]]KEEP[[/iftags]]", tags=["alpha"], note="forbidden tag present"),
    dict(id="bare-hit", source="[[iftags alpha]]KEEP[[/iftags]]", tags=["alpha"], note="any-tag present"),
    dict(id="bare-miss", source="[[iftags alpha]]KEEP[[/iftags]]", tags=["beta"], note="any-tag absent"),
    dict(id="mixed-plus-minus-hit", source="[[iftags +alpha -beta gamma]]KEEP[[/iftags]]", tags=["alpha", "gamma"], note="required and forbidden and any"),
    dict(id="mixed-plus-minus-miss-forbidden", source="[[iftags +alpha -beta gamma]]KEEP[[/iftags]]", tags=["alpha", "beta", "gamma"], note="forbidden present"),
    dict(id="mixed-plus-minus-miss-any", source="[[iftags +alpha -beta gamma]]KEEP[[/iftags]]", tags=["alpha", "delta"], note="any absent"),
    dict(id="opener-upper", source="[[IFTAGS +alpha]]KEEP[[/iftags]]", tags=["alpha"], note="uppercase opener"),
    dict(id="opener-mixed", source="[[Iftags +alpha]]KEEP[[/iftags]]", tags=["alpha"], note="mixed-case opener"),
    dict(id="closer-upper", source="[[iftags +alpha]]KEEP[[/IFTAGS]]", tags=["alpha"], note="uppercase closer"),
    dict(id="opener-and-closer-upper", source="[[IFTAGS +ALPHA]]KEEP[[/IFTAGS]]", tags=["alpha"], note="uppercase head and case-insensitive tag test"),
    dict(id="no-space-after-name", source="[[iftags+alpha]]KEEP[[/iftags]]", tags=["alpha"], note="no separator after name, invalid opener"),
    dict(id="space-before-name", source="[[ iftags +alpha]]KEEP[[/iftags]]", tags=["alpha"], note="leading space inside opener"),
    dict(id="extra-spaces-spec", source="[[iftags   +alpha   -beta  ]]KEEP[[/iftags]]", tags=["alpha"], note="runs of spaces in spec"),
    dict(id="empty-spec-tagged", source="[[iftags]]KEEP[[/iftags]]", tags=["alpha"], note="empty spec on tagged page"),
    dict(id="empty-spec-spaces-tagged", source="[[iftags   ]]KEEP[[/iftags]]", tags=["alpha"], note="whitespace-only spec on tagged page"),
    dict(id="empty-spec-untagged", source="[[iftags]]KEEP[[/iftags]]", note="empty spec on untagged page"),
    dict(id="plus-untagged", source="[[iftags +alpha]]KEEP[[/iftags]]", note="required tag on untagged page"),

    # --- case, separators, empty conditions ---
    dict(id="case-plus-spec-upper", source="[[iftags +ALPHA]]KEEP[[/iftags]]", tags=["alpha"], note="uppercase spec, lowercase tag"),
    dict(id="case-plus-tag-upper", source="[[iftags +alpha]]KEEP[[/iftags]]", tags=["ALPHA"], note="lowercase spec, uppercase tag"),
    dict(id="case-bare", source="[[iftags ALPHA]]KEEP[[/iftags]]", tags=["alpha"], note="uppercase bare condition"),
    dict(id="case-minus-spec", source="[[iftags -BETA]]KEEP[[/iftags]]", tags=["alpha", "beta"], note="uppercase forbidden, lowercase tag"),
    dict(id="case-minus-tag", source="[[iftags -beta]]KEEP[[/iftags]]", tags=["BETA"], note="uppercase tag, lowercase forbidden"),
    dict(id="comma-plus-both", source="[[iftags +alpha,+beta]]KEEP[[/iftags]]", tags=["alpha", "beta"], note="comma-separated required tags, both present"),
    dict(id="comma-plus-one", source="[[iftags +alpha,+beta]]KEEP[[/iftags]]", tags=["alpha"], note="comma-separated required tags, one present"),
    dict(id="comma-minus", source="[[iftags -alpha,-beta]]KEEP[[/iftags]]", tags=["gamma"], note="comma-separated forbidden tags"),
    dict(id="comma-bare", source="[[iftags alpha,beta]]KEEP[[/iftags]]", tags=["beta"], note="comma-separated any tags"),
    dict(id="comma-space-mixed", source="[[iftags +alpha, -beta gamma]]KEEP[[/iftags]]", tags=["alpha", "gamma"], note="comma and space mixed separators"),
    dict(id="bare-minus-only", source="[[iftags -]]KEEP[[/iftags]]", tags=["alpha"], note="dangling minus condition on tagged page"),
    dict(id="bare-minus-only-untagged", source="[[iftags -]]KEEP[[/iftags]]", note="dangling minus condition untagged"),
    dict(id="bare-plus-only", source="[[iftags +]]KEEP[[/iftags]]", tags=["alpha"], note="dangling plus condition"),
    dict(id="bare-double-bare", source="[[iftags alpha beta]]KEEP[[/iftags]]", tags=["beta"], note="two bare conditions, one present"),
    dict(id="bare-double-bare-miss", source="[[iftags alpha beta]]KEEP[[/iftags]]", tags=["gamma"], note="two bare conditions, none present"),
    dict(id="tag-hyphen", source="[[iftags +some-tag]]KEEP[[/iftags]]", tags=["some-tag"], note="hyphenated tag"),
    dict(id="tag-underscore", source="[[iftags +some_tag]]KEEP[[/iftags]]", tags=["some_tag"], note="underscore tag"),
    dict(id="tag-unicode", source="[[iftags +テーマ]]KEEP[[/iftags]]", tags=["テーマ"], note="unicode tag"),

    # --- recursion and nesting ---
    dict(id="nested-both-true", source="[[iftags +alpha]]OUT[[iftags +alpha]]IN[[/iftags]]TAIL[[/iftags]]", tags=["alpha"], note="nested gates both pass"),
    dict(id="nested-inner-false", source="[[iftags +alpha]]OUT[[iftags +beta]]IN[[/iftags]]TAIL[[/iftags]]", tags=["alpha"], note="inner gate false"),
    dict(id="nested-outer-false", source="[[iftags +beta]]OUT[[iftags +alpha]]IN[[/iftags]]TAIL[[/iftags]]", tags=["alpha"], note="outer gate false"),
    dict(id="nested-triple", source="[[iftags +alpha]]A[[iftags +alpha]]B[[iftags +alpha]]C[[/iftags]]D[[/iftags]]E[[/iftags]]", tags=["alpha"], note="three-level nesting"),
    dict(id="nested-unbalanced-inner", source="[[iftags +alpha]]OUT[[iftags +alpha]]IN[[/iftags]]TAIL", tags=["alpha"], note="outer closer missing"),
    dict(id="two-adjacent", source="[[iftags +alpha]]A[[/iftags]][[iftags +alpha]]B[[/iftags]]", tags=["alpha"], note="two adjacent blocks"),
    dict(id="two-adjacent-second-false", source="[[iftags +alpha]]A[[/iftags]][[iftags +beta]]B[[/iftags]]", tags=["alpha"], note="adjacent blocks with different gates"),

    # --- malformed and unterminated ---
    dict(id="unterminated-open", source="[[iftags +alpha]]KEEP-no-closer", tags=["alpha"], note="unterminated block"),
    dict(id="stray-closer", source="before[[/iftags]]after", tags=["alpha"], note="closer without opener"),
    dict(id="missing-one-bracket", source="[[iftags +alpha]KEEP[[/iftags]]", tags=["alpha"], note="single-bracket opener"),
    dict(id="triple-close-head", source="[[iftags +alpha]]]KEEP[[/iftags]]", tags=["alpha"], note="extra bracket after opener"),
    dict(id="closer-first", source="[[/iftags]]KEEP[[iftags +alpha]]TAIL[[/iftags]]", tags=["alpha"], note="closer before opener"),
    dict(id="newline-in-spec", source="[[iftags +alpha\n+beta]]KEEP[[/iftags]]", tags=["alpha", "beta"], note="newline inside spec"),

    # --- inline vs line-start bodies and paragraph seams ---
    dict(id="inline-body", source="prefix [[iftags -beta]]KEEP[[/iftags]] suffix", tags=["alpha"], note="inline gate with inline body"),
    dict(id="line-start-body", source="[[iftags -beta]]KEEP[[/iftags]]\nAFTER", tags=["alpha"], note="line-start gate with following line"),
    dict(id="body-next-line", source="[[iftags -beta]]\nKEEP\n[[/iftags]]\nAFTER", tags=["alpha"], note="block body on next line"),
    dict(id="leading-space-opener", source="  [[iftags -beta]]KEEP[[/iftags]]", tags=["alpha"], note="indented opener"),
    dict(id="blockquote-opener", source="> [[iftags -beta]]KEEP[[/iftags]]", tags=["alpha"], note="quote-prefixed opener"),
    dict(id="body-paragraph-breaks", source="[[iftags -beta]]A\n\nB\n\nC[[/iftags]]", tags=["alpha"], note="body with paragraph breaks"),
    dict(id="whitespace-only-body", source="[[iftags -beta]]   [[/iftags]]", tags=["alpha"], note="whitespace-only body"),
    dict(id="empty-body", source="[[iftags -beta]][[/iftags]]", tags=["alpha"], note="empty body"),
    dict(id="false-gate-newlines", source="A\n[[iftags +beta]]HIDDEN[[/iftags]]\nB", tags=["alpha"], note="false gate between lines"),
    dict(id="true-gate-newlines", source="A\n[[iftags +alpha]]SHOWN[[/iftags]]\nB", tags=["alpha"], note="true gate between lines"),

    # --- comments inside the spec ---
    dict(id="spec-comment-complete", source="[[iftags +alpha [!--x--] -beta]]KEEP[[/iftags]]", tags=["alpha"], note="complete comment in spec, gate should fall to literal"),
    dict(id="spec-comment-straddle", source="[[iftags +alpha [!--x--]]KEEP[[/iftags]]", tags=["alpha"], note="comment straddling head close"),
    dict(id="spec-comment-closer-inside", source="[[iftags +alpha [!-- [[/iftags]] --]]KEEP[[/iftags]]", tags=["alpha"], note="comment containing a closer"),
    dict(id="spec-comment-unterminated", source="[[iftags +alpha [!--x]]KEEP[[/iftags]]", tags=["alpha"], note="unterminated comment in spec"),

    # --- attribute and flag edges ---
    dict(id="star-flag", source="[[iftags* +alpha]]KEEP[[/iftags]]", tags=["alpha"], note="star flag, iftags rejects stars"),
    dict(id="score-flag", source="[[iftags_ +alpha]]KEEP[[/iftags]]", tags=["alpha"], note="score flag, iftags rejects scores"),
    dict(id="name-suffix", source="[[iftagsx +alpha]]KEEP[[/iftags]]", tags=["alpha"], note="longer name, not iftags"),
    dict(id="name-prefix", source="[[xiftags +alpha]]KEEP[[/iftags]]", tags=["alpha"], note="prefixed name, not iftags"),
    dict(id="plain-attrs", source="[[iftags +alpha class=x]]KEEP[[/iftags]]", tags=["alpha"], note="unrecognized attribute-shaped spec token"),

    # --- adjacency with neighboring rules in pipeline order ---
    dict(id="body-comment", source="[[iftags -beta]]A[!-- c --]B[[/iftags]]", tags=["alpha"], note="comment inside kept body"),
    dict(id="body-iframe", source="[[iftags -beta]]\n[[iframe https://example.com/]]\n[[/iftags]]", tags=["alpha"], note="iframe inside kept body"),
    dict(id="body-date", source="[[iftags -beta]]\n[[date 0]]\n[[/iftags]]", tags=["alpha"], note="date inside kept body"),
    dict(id="body-math", source="[[iftags -beta]]\n[[math]]\nx^2\n[[/math]]\n[[/iftags]]", tags=["alpha"], note="math inside kept body"),
    dict(id="false-hides-math", source="[[iftags +beta]]\n[[math]]\nx^2\n[[/math]]\n[[/iftags]]", tags=["alpha"], note="math inside suppressed body"),
    dict(id="false-hides-iframe", source="[[iftags +beta]]\n[[iframe https://example.com/]]\n[[/iftags]]", tags=["alpha"], note="iframe inside suppressed body"),
    dict(id="math-contains-false-iftags", source="[[math]]\nx [[iftags +beta]]HIDDEN[[/iftags]] y\n[[/math]]", tags=["alpha"], note="false gate inside a math body leaves the math opener literal, cross-rule seam"),
    dict(id="body-bold-seam", source="[[iftags -beta]]**BOLD**KEEP[[/iftags]]", tags=["alpha"], note="bold seam at body start"),
    dict(id="body-span-seam", source="[[iftags -beta]][[span class=x]]SPAN[[/span]]KEEP[[/iftags]]", tags=["alpha"], note="span seam at body start"),
    dict(id="after-block-div", source="[[iftags -beta]]KEEP[[/iftags]]\n[[div]]\nD\n[[/div]]", tags=["alpha"], note="kept gate before a div block"),
]


def main():
    out = pathlib.Path(__file__).with_name("battery.jsonl")
    with out.open("w", encoding="utf-8") as fh:
        for case in CASES:
            rec = {"id": case["id"], "source": case["source"]}
            if "tags" in case:
                rec["tags"] = case["tags"]
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"wrote {len(CASES)} cases to {out}")


if __name__ == "__main__":
    main()
