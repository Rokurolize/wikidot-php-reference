#!/usr/bin/env python3
"""Generate the R2 Table (pipeline rule 35, the || cell-separator form) battery of whole-document Wikidot-source cases. The battery covers row and cell counts, header ~ cells, empty cells and both span forms (leading and trailing empties), the > = < alignment markers and their near misses, inline and block cell content, interruptions by other block constructs, unterminated and malformed rows, multiple adjacent tables and nested tables where the grammar admits them. Sources are LF-only with trailing newlines stripped, matching Wikidot's save normalization; JSON stores their newlines as escaped \\n. The optional tags field is accepted by both the shared reference harness and the shared ftml dumper but no case here turns on page tags. Every case id is prefixed t35- to keep this owner's cases disjoint from the Tableadv owner and the root's cross-rule cases."""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "battery.jsonl")

CASES = [
    ("t35-01-single-cell", "|| Cell ||"),
    ("t35-02-no-space", "||no spaces||"),
    ("t35-03-two-rows-two-cells", "|| A || B ||\n|| C || D ||"),
    ("t35-04-ragged-rows", "|| A ||\n|| B || C ||\n|| D || E || F ||"),
    ("t35-05-one-row-three-cells", "|| Alpha || Beta || Gamma ||"),
    ("t35-06-leading-space-content", "||  Left  ||= Center ||\n|| Normal ||> Right  ||"),
    ("t35-07-trailing-space", "|| Para space ||   \n\nAfter\n\n|| EOF space ||   "),

    ("t35-08-header-one", "||~ Head ||\n|| body ||"),
    ("t35-09-header-spaced-literal", "|| ~ Head ||\n|| cell ||"),
    ("t35-10-header-glued-literal", "||~Head ||\n||~||\n||~a||"),
    ("t35-11-header-repeated-literal", "||~~ A ||\n||=== B ||\n||>>> C ||"),
    ("t35-12-header-inline", "||~ **Bold** and //italic// ||\n|| plain ||"),
    ("t35-13-header-many", "||~ A ||~ B ||~ C ||\n|| x || y || z ||"),

    ("t35-14-align-right", "||> Right ||\n|| normal ||"),
    ("t35-15-align-center", "||= Center ||\n|| normal ||"),
    ("t35-16-align-left", "||< Left ||\n|| normal ||"),
    ("t35-17-align-no-space-literal", "||>a||\n||=a||\n||<a||"),
    ("t35-18-align-and-header", "||~= Center head ||\n||~> Right head ||\n||~< Left head ||"),

    ("t35-19-empty-middle-cell", "|| A |||| C ||"),
    ("t35-20-empty-leading-cell", "|||| B || C ||"),
    ("t35-21-trailing-empties", "|| A ||||\n|| B ||||||"),
    ("t35-22-span-two", "|||| Durian ||"),
    ("t35-23-span-three-with-header", "||||||~ Very Berry ||"),
    ("t35-24-span-plus-align", "||||= Center span ||\n||||> Right span ||"),
    ("t35-25-all-empty-row", "||||\n||||||"),
    ("t35-26-empty-between-rows", "|| A ||\n\n|| B ||"),

    ("t35-27-bold-italic-color", "|| **bold** || //italic// || ##red|color## ||"),
    ("t35-28-link-and-mailto", "|| [http://example.com site] || [[span]]inline[[/span]] ||"),
    ("t35-29-footnote-in-cell", "|| see[1] || normal ||\n\n[1] footnote text"),
    ("t35-30-line-continuation", "|| Apple _\nBanana || Cherry_ || _Pineapple _\n _\n _\nMelon ||"),
    ("t35-31-comment-cell", "|| A [!--x--] || B ||\n|| A[!--x--] || B ||"),
    ("t35-32-french-quotes-and-literal-angle", "||<<french quotes>>||<div>||"),

    ("t35-33-cell-with-span-block", "||[[span]]inline block[[/span]] ||\n|| tail ||"),
    ("t35-34-cell-with-div", "||[[div class=\"x\"]]\ninside\n[[/div]] ||\n|| after ||"),
    ("t35-35-cell-with-list", "||[[ul]]\n* one\n* two\n[[/ul]] ||\n|| after ||"),
    ("t35-36-cell-with-quote", "|| > quoted line ||\n|| after ||"),

    ("t35-37-then-paragraph", "|| Alpha ||\nPlain paragraph after table without a blank line."),
    ("t35-38-paragraph-then-table", "Plain paragraph before.\n\n|| Alpha ||"),
    ("t35-39-interrupted-by-heading", "|| A || B ||\n+ Heading\n|| C || D ||"),
    ("t35-40-interrupted-by-hr", "|| A ||\n\n----\n\n|| B ||"),
    ("t35-41-interrupted-by-code", "|| A ||\n{{ some code }}\n|| B ||"),
    ("t35-42-two-tables-blank-line", "|| one ||\n\n|| two ||"),
    ("t35-43-table-then-list", "|| a ||\n* one\n* two"),
    ("t35-44-quoted-table", "> || quoted ||\n> || row ||"),

    ("t35-45-unterminated-last-row", "|| A || B ||\n|| C || D"),
    ("t35-46-unterminated-junk", "|| A || B ||\n|| C || D || junk"),
    ("t35-47-single-pipe-lines", "|| A ||\n| single ||\n|| B ||"),
    ("t35-48-marker-only-line", "||~||\n||=||\n||>||\n||<||"),
    ("t35-49-row-without-closing-pipes", "|| A || B\n|| C"),
    ("t35-50-opener-only", "||"),
    ("t35-51-eof-no-newline", "|| A || B ||"),

    ("t35-52-nested-table-opener", "|| outer A1 ||\n|| [[table]]\n|| inner B2 ||\n[[/table]] ||\n|| outer C3 ||"),
    ("t35-53-advanced-inside-simple", "|| outer ||\n[[table]]\n[[row]]\n[[cell]]inner[[/cell]]\n[[/row]]\n[[/table]]\n|| tail ||"),
    ("t35-54-simple-inside-advanced-cell", "[[table]]\n[[row]]\n[[cell]]\n|| inner A || B ||\n[[/cell]]\n[[/row]]\n[[/table]]"),

    ("t35-55-leading-blank-line", "\n|| A ||\n|| B ||"),
    ("t35-56-table-only-with-trailing-blank", "|| A ||\n\n"),
    ("t35-57-mixed-markers-and-spans", "||||> Right span ||= Center ||~ Head ||\n|| A |||| D ||"),
    ("t35-58-wide-grid", "|| 1 || 2 || 3 || 4 ||\n|| a || b || c || d ||\n|| 5 || 6 ||"),
    ("t35-59-inline-bold-crosses-cell", "|| **A1 || B2** || C3 ||"),
    ("t35-60-unicode-content", "|| café || 日本語 || <b>x</b> ||"),
]


def main():
    with open(OUT, "w", encoding="utf-8", newline="\n") as handle:
        for cid, source in CASES:
            rec = {"id": cid, "source": source.rstrip("\n")}
            handle.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("wrote", len(CASES), "cases to", OUT)


if __name__ == "__main__":
    main()
