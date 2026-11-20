#!/usr/bin/env python3
"""Generate root's R2-table cross-rule interaction battery (xbattery.jsonl).

Whole-document cases for the interactions no single rule owner can own: tables
inside divs / collapsibles / blockquotes, the simple (||) and advanced
([[table]]) forms adjacent and nested, cell content carrying the span-shaped
inline family, footnotes and pipe-bearing links (the F-R2-44 neighborhood),
tables interrupted by headings and lists, and mixed-form boundaries. Sources
are LF-only with no trailing newline because Wikidot normalizes trailing
whitespace on save.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xbattery.jsonl")

SIMPLE = "|| a || b ||\n|| c || d ||"
ADV = ("[[table]]\n[[row]]\n[[cell]]a[[/cell]]\n[[cell]]b[[/cell]]\n"
       "[[/row]]\n[[row]]\n[[cell]]c[[/cell]]\n[[cell]]d[[/cell]]\n[[/row]]\n[[/table]]")

cases = []


def add(cid, source):
    cases.append({"id": cid, "source": source})


# A. Tables inside containers.
add("x01-table-in-div", '[[div class="box"]]\n' + SIMPLE + '\n[[/div]]')
add("x02-table-in-div-attr", '[[div id="d" style="color:red"]]\n' + SIMPLE + '\n[[/div]]')
add("x03-table-in-collapsible", '[[collapsible]]\n' + SIMPLE + '\n[[/collapsible]]')
add("x04-table-in-collapsible-closed", '[[collapsible show="open" hide="close"]]\n' + SIMPLE + '\n[[/collapsible]]')
add("x05-table-in-quote", '> || a || b ||\n> || c || d ||')
add("x06-table-in-quote-head", '> intro\n> || a || b ||\n> || c || d ||')
add("x07-adv-in-div", '[[div class="box"]]\n' + ADV + '\n[[/div]]')
add("x08-adv-in-collapsible", '[[collapsible]]\n' + ADV + '\n[[/collapsible]]')
add("x09-table-in-quote-in-div", '[[div]]\n> || a || b ||\n> || c || d ||\n[[/div]]')

# B. Simple and advanced forms adjacent and nested.
add("x10-simple-then-adv", SIMPLE + '\n\n' + ADV)
add("x11-adv-then-simple", ADV + '\n\n' + SIMPLE)
add("x12-simple-adv-no-blank", SIMPLE + '\n' + ADV)
add("x13-adv-in-simple-cell", '|| [[table]][[row]][[cell]]in[[/cell]][[/row]][[/table]] || b ||')
add("x14-simple-in-adv-cell", '[[table]][[row]][[cell]]|| x || y ||[[/cell]][[/row]][[/table]]')
add("x15-adv-in-adv-cell", '[[table]][[row]][[cell]]\n[[table]][[row]][[cell]]inner[[/cell]][[/row]][[/table]]\n[[/cell]][[/row]][[/table]]')
add("x16-two-adv-adjacent", ADV + '\n' + ADV)
add("x17-simple-adv-simple", SIMPLE + '\n\n' + ADV + '\n\n' + SIMPLE)

# C. Cell content: span-shaped inline family, footnotes, pipe links (F-R2-44).
add("x18-cell-with-span", '|| [[span class="x"]]spanned[[/span]] || b ||')
add("x19-cell-with-size", '|| [[size 120%]]big[[/size]] || b ||')
add("x20-cell-with-color", '|| [[color red]]red[[/color]] || b ||')
add("x21-cell-with-bold", "|| **strong** || ''em'' ||")
add("x22-cell-with-footnote", '|| a[[footnote]]note[[/footnote]] || b ||\n\n[[footnoteblock]]')
add("x23-cell-with-triple-link", '|| [[[some-page|link]]] || b ||')
add("x24-cell-with-url-pipe", '|| [[https://example.com|Example]] || b ||')
add("x25-cell-with-url-pipe-cell2", '|| a || [[http://example.com|link]] ||')
add("x26-cell-with-raw", '|| @@raw@@ || b ||')
add("x27-adv-cell-with-span", '[[table]][[row]][[cell]][[span class="x"]]s[[/span]][[/cell]][[/row]][[/table]]')
add("x28-adv-cell-with-url-pipe", '[[table]][[row]][[cell]][[https://example.com|E]][[/cell]][[/row]][[/table]]')
add("x29-cell-with-div", '|| [[div]]inside[[/div]] || b ||')
add("x30-cell-with-collapsible", '|| [[collapsible]]hidden[[/collapsible]] || b ||')

# D. Tables interrupted by headings, toc, lists and other blocks.
add("x31-table-heading-table", '|| a || b ||\n= Heading =\n|| c || d ||')
add("x32-table-toc-table", '|| a || b ||\n[[toc]]\n|| c || d ||')
add("x33-table-list-table", '|| a || b ||\n* item\n|| c || d ||')
add("x34-table-deflist-table", '|| a || b ||\n: term : definition\n|| c || d ||')
add("x35-table-hr-table", '|| a || b ||\n----\n|| c || d ||')
add("x36-table-code-table", '|| a || b ||\n[[code]]\nx\n[[/code]]\n|| c || d ||')
add("x37-heading-then-table", '= Heading =\n' + SIMPLE)
add("x38-list-then-table", '* item\n' + SIMPLE)
add("x39-adv-heading-adv", ADV + '\n= Heading =\n' + ADV)

# E. Mixed-form boundaries, spans and malformed shapes.
add("x40-adv-colspan-rowspan", '[[table]]\n[[row]]\n[[cell colspan="2"]]wide[[/cell]]\n[[/row]]\n[[row]]\n[[cell rowspan="2"]]tall[[/cell]]\n[[cell]]b[[/cell]]\n[[/row]]\n[[row]]\n[[cell]]d[[/cell]]\n[[/row]]\n[[/table]]')
add("x41-simple-trailing-empty-span", '|| a || || || b ||\n|| c || d ||')
add("x42-simple-header-mix", '||~ H || = C || > R ||\n|| a || b ||')
add("x43-adv-empty-cells", '[[table]][[row]][[cell]][[/cell]][[cell]]b[[/cell]][[/row]][[/table]]')
add("x44-malformed-adv-opener", '[[table]]\n[[row]]\n[[cell]]unclosed\n' + SIMPLE)
add("x45-table-then-literal-brackets", SIMPLE + '\n[[table]]not closed')
add("x46-div-simple-collapsible-adv", '[[div]]\n' + SIMPLE + '\n[[/div]]\n\n[[collapsible]]\n' + ADV + '\n[[/collapsible]]')

with open(OUT, "w", encoding="utf-8") as f:
    for c in cases:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
print("wrote", OUT, len(cases), "cases")
