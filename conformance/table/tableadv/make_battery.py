#!/usr/bin/env python3
"""Generate the R2 Tableadv whole-document battery.

Every case is one self-contained Wikidot document whose advanced table form is [[table]] containing [[row]] blocks containing [[cell]] or [[hcell]] blocks. Sources are stored as JSON strings so embedded newlines are escaped \\n in battery.jsonl, and each case carries tags for protocol compatibility with the shared harness and dumper. The battery mixes structural shapes, header cells, empty cells, span attributes, the attribute grammar, inline and block cell content, nested tables, and interruptions or malformed forms that must stay literal.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CASES = []


def add(cid, source, tags=None):
    CASES.append({"id": cid, "source": source, "tags": tags or []})


def table(rows, head=""):
    return "[[table%s]]\n%s\n[[/table]]" % (head, "\n".join(rows))


def row(cells, head=""):
    return "[[row%s]]\n%s\n[[/row]]" % (head, "\n".join(cells))


def cell(content="", head="", name="cell"):
    return "[[%s%s]]%s[[/%s]]" % (name, head, content, name)


# Structural basics: row counts, cell counts, placement in a document.
add("adv01-single-cell", table([row([cell("X")])]))
add("adv02-two-rows", table([row([cell("A"), cell("B")]), row([cell("C")])]))
add("adv03-three-cells", table([row([cell("A"), cell("B"), cell("C")])]))
add("adv04-two-tables", table([row([cell("A")])]) + "\n\n" + table([row([cell("B")])]))
add("adv05-inline-form", "[[table]] [[row]] [[cell]] Apple [[/cell]] [[/row]] [[/table]]")
add("adv06-midline-table", "intro " + table([row([cell("X")])]) + " tail")
add("adv07-after-heading", "= Heading =\n\n" + table([row([cell("X")])]))
add("adv08-table-then-paragraph", table([row([cell("X")])]) + "\n\nafter")

# Empty table, empty row, empty cell: only a row with a cell makes a table.
add("adv09-empty-table-literal", "[[table]]\n[[/table]]")
add("adv10-empty-row-literal", "[[table]]\n[[row]]\n[[/row]]\n[[/table]]")
add("adv11-empty-cell", table([row([cell()])]))
add("adv12-empty-plus-content", table([row([cell(), cell("B")])]))
add("adv13-empty-row-then-full-row", "[[table]]\n[[row]]\n[[/row]]\n[[row]]\n[[cell]]X[[/cell]]\n[[/row]]\n[[/table]]")

# Header rows and the hcell/cell closer distinction.
add("adv14-header-row", table([row([cell("A", name="hcell"), cell("B", name="hcell")]), row([cell("1"), cell("2")])]))
add("adv15-hcell-cell-closer", table([row(["[[hcell]]Heading[[/cell]]"])]))
add("adv16-cell-hcell-closer", table([row(["[[cell]]Heading[[/hcell]]"])]))
add("adv17-header-attrs", table([row([cell("Group", ' colspan="2" class="heading"', "hcell")])]))
add("adv18-mixed-header-body", table([row([cell("H", name="hcell")]), row([cell("D")])]))

# Span forms, including the fallback that drops a zero span.
add("adv19-colspan", table([row([cell("Three", ' colspan="3"'), cell("Two", ' rowspan="2"')])]))
add("adv20-rowspan", table([row([cell("Two", ' rowspan="2"')]), row([cell("A"), cell("B")])]))
add("adv21-colspan-zero", table([row([cell("Zero", ' colspan="0" data-name="zero"')])]))
add("adv22-rowspan-zero", table([row([cell("Zero", ' rowspan="0"')])]))
add("adv23-colspan-bad", table([row([cell("Bad", ' colspan="abc" data-name="bad"'), cell("Good", ' colspan="2"', "hcell")])]))
add("adv24-colspan-big", table([row([cell("Wide", ' colspan="10" rowspan="2"')])]))
add("adv25-header-colspan", table([row([cell("Group", ' colspan="2"', "hcell")]), row([cell("A"), cell("B")])]))

# Attribute grammar on table, row and cell: quoting, unknown keys, case, id.
add("adv26-table-attrs", table([row([cell("X")])], ' class="grid" style="color: red"'))
add("adv27-table-id", table([row([cell("X")])], ' id="fruit"'))
add("adv28-row-attrs", table([row([cell("X")], ' data-id="r1" class="top"')]))
add("adv29-cell-attrs", table([row([cell("X", ' data-sort="number" class="c"')])]))
add("adv30-unknown-attrs", table([row([cell("X", ' foo="1" aria-label="l"')])], ' foo="2"'))
add("adv31-uppercase-attrs", table([row([cell("X", ' CLASS="c" DATA-X="1"')])], ' CLASS="g"'))
add("adv32-quoted-close-bracket", '[[table class="a]]b"]]\n[[row]][[cell]]x[[/cell]][[/row]]\n[[/table]]')
add("adv33-empty-attr-values", table([row([cell("X", ' class="" data-x=""')])], ' class=""'))
add("adv34-title-attr", table([row([cell("X", ' title="tip"')])], ' title="tip"'))
add("adv35-many-attrs", table([row([cell("X", ' z="1" a="2" m="3" class="c"')])], ' class="a" id="x" style="color:red"'))
add("adv36-dup-attr", table([row([cell("X", ' class="a" class="b"')])]))
add("adv37-id-prefixed", table([row([cell("X", ' id="u-bar"')])], ' id="u-foo"'))
add("adv38-unquoted-attrs", table([row([cell("X", ' class=foo data-x=1')])]))

# Alignment and style attributes pass through on cells.
add("adv39-align-center", table([row([cell("C", ' align="center"'), cell("R", ' style="text-align: right;"')])]))
add("adv40-valign-dropped", table([row([cell("X", ' valign="top"')])]))

# Inline markup and block content inside cells.
add("adv41-inline-markup", table([row([cell("**bold** and //italic//")])]))
add("adv42-paragraph-cell", table([row([cell("\n\nApple\n\n")])]))
add("adv43-two-paragraph-cell", table([row([cell("\n\nApple\n\nPear\n\n")])]))
add("adv44-list-in-cell", table([row([cell("\n* one\n* two\n")])]))
add("adv45-heading-in-cell", table([row([cell("\n= Inner =\n")])]))
add("adv46-quote-in-cell", table([row([cell("\n> quoted\n")])]))
add("adv47-space-junk", "[[table]]   \n [[row]]  [[cell]]A[[/cell]]  [[/row]] \n[[/table]]")

# Nested tables, inline and with paragraph bodies.
add("adv48-nested-inline", "[[table]][[row]][[cell]][[table]][[row]][[cell]].[[/cell]][[/row]][[/table]][[/cell]][[/row]][[/table]]")
add("adv49-nested-paragraph", table([row([cell("\n\n1\n\n" + table([row([cell("\n\n2\n\n")])]) + "\n\n")])]))
add("adv50-nested-deep", table([row([cell(table([row([cell(table([row([cell("deep")])]))])]))])]))

# Interruptions and malformed or unterminated forms that must stay literal.
add("adv51-junk-in-table", "[[table]]\n[[row]]\n[[cell]]X[[/cell]]\n[[/row]]\njunk\n[[/table]]")
add("adv52-junk-in-row", "[[table]]\n[[row]]\n[[cell]]X[[/cell]]\njunk\n[[/row]]\n[[/table]]")
add("adv53-unterminated-table", "[[table]]\n[[row]]\n[[cell]]X[[/cell]]\n[[/row]]")
add("adv54-unterminated-cell", "[[table]]\n[[row]]\n[[cell]]X\n[[/row]]\n[[/table]]")
add("adv55-naked-row-cell", "[[row]] naked [[/row]]\n\n[[cell]] naked [[/cell]]\n\n[[hcell]] naked [[/hcell]]")
add("adv56-col-alias", "[[table]]\n[[row]]\n[[col]]X[[/col]]\n[[/row]]\n[[/table]]")
add("adv57-fused-close", "[[table]]\n[[row]]\n[[cell]]x[[/cell]]\n[[/row]]\n[[/table]]]\nafter")
add("adv58-table-in-div", "[[div]]\n" + table([row([cell("X")])]) + "\n[[/div]]")
add("adv59-malformed-args", "[[table bad=1]]\n[[/table]]\n\n" + table([row([cell("x", " bad=1")])]))
add("adv60-cell-quoted-bracket", "[[table]]\n[[row]]\n[[cell class=\"a]b\"]]x[[/cell]]\n[[/row]]\n[[/table]]")


def main():
    with open(ROOT / "battery.jsonl", "w", encoding="utf-8", newline="\n") as handle:
        for case in CASES:
            handle.write(json.dumps(case, ensure_ascii=False) + "\n")
    print("wrote %d cases" % len(CASES))


if __name__ == "__main__":
    main()
