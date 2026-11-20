#!/usr/bin/env python3
"""Generate battery.jsonl for the R2-block Toc rule (whole documents only).

Covers [[toc]] matcher variants and attributes, placement relative to headings
(before / after / multiple), heading level skips and repeats, headings and TOC
blocks nested in divs / collapsibles / iftags / quotes / footnotes, float
layout and range-adjacent forms, and malformed / near-miss spellings.
"""
import json

CASES = []


def add(cid, source, tags=None):
    rec = {"id": cid, "source": source}
    if tags is not None:
        rec["tags"] = tags
    CASES.append(rec)


# --- core matching and placement -------------------------------------------
add("toc01-before", "[[toc]]\n\n+ Alpha\n\n+ Beta")
add("toc02-after", "+ Alpha\n\n+ Beta\n\n[[toc]]")
add("toc03-empty", "[[toc]]")
add("toc04-no-headings-body", "Opening text.\n\n[[toc]]\n\nClosing text.")
add("toc05-multiple", "+ Lead\n\nintro\n\n[[toc]]\n\n+ Middle\n\n[[toc]]\n\n++ Nested\n\n[[toc]]\n\n+ Final")
add("toc06-multiple-adjacent", "[[toc]]\n[[toc]]\n\n+ One")
add("toc07-levels", "+ L1\n\n++ L2\n\n+++ L3\n\n++++ L4\n\n+++++ L5\n\n++++++ L6\n\n[[toc]]")
add("toc08-skip", "+ One\n\n++++ Four\n\n[[toc]]")
add("toc09-repeat", "+ A\n\n++ B\n\n+ C\n\n++ D\n\n[[toc]]")
add("toc10-skipped-heading", "[[toc]]\n\n+ Alpha\n\n+* Skipped\n\n++ Beta")
add("toc11-inline-markup", "+ **Bold** and //italic// text\n\n[[toc]]")
add("toc12-link-in-heading", "+ See [http://example.com the site]\n\n[[toc]]")
add("toc13-footnote-in-heading", "+ Head[[footnote]]note text[[/footnote]] tail\n\n+ Plain\n\n[[toc]]")
add("toc14-repeated-text", "+ Same\n\n+ Same\n\n+ Same\n\n[[toc]]")
add("toc15-dash-runs", "+ aa -- bb\n\n+ cc --- dd\n\n+ ee -- [[span]]ff[[/span]] -- gg\n\n[[toc]]")
add("toc16-unicode", "+ 日本語 🌊 café\n\n[[toc]]")

# --- layout: float alignment and attributes --------------------------------
add("toc20-float-left", "[[f<toc]]\n\n+ A")
add("toc21-float-right", "[[f>toc]]\n\n+ A")
add("toc22-title", "+ A\n\n[[toc title=\"Contents\"]]")
add("toc23-title-empty", "[[toc title=\"\"]]\n\n+ A")
add("toc24-title-entities", "[[toc title=\"目次 & <notes>\"]]\n\n+ A")
add("toc25-class", "[[toc class=\"third-toc\"]]\n\n+ A")
add("toc26-style", "[[toc style=\"color: blue\"]]\n\n+ A")
add("toc27-id", "[[toc id=\"my-toc\"]]\n\n+ A")
add("toc28-multi-attrs", "[[toc title=\"T\" class=\"c\" style=\"color:red\" id=\"i\"]]\n\n+ A")
add("toc29-quoted-close-bracket", "[[toc title=\"a]]b\"]]\n\n+ A")
add("toc30-float-title", "[[f<toc title=\"Left TOC\"]]\n\n+ A")
add("toc31-float-class", "[[f>toc class=\"righty\"]]\n\n+ A")
add("toc32-float-id", "[[f>toc id=\"toc-right\"]]\n\n+ A")

# --- nesting with other block constructs -----------------------------------
add("toc40-div-wrapped-heading", "[[div class=\"x\"]]\n+ Inside div\n[[/div]]\n\n[[toc]]")
add("toc41-collapsible-wrapped-heading", "[[collapsible show=\"open\"]]\n+ Inside collapsible\n[[/collapsible]]\n\n[[toc]]")
add("toc42-iftags-kept-heading", "[[iftags tags=\"fn\"]]+ Kept heading[[/iftags]]\n\n[[toc]]", tags=["fn"])
add("toc43-iftags-hidden-heading", "[[iftags tags=\"other\"]]+ Hidden heading[[/iftags]]\n\n[[toc]]", tags=["fn"])
add("toc44-toc-in-div", "[[div]]\n[[toc]]\n[[/div]]\n\n+ A")
add("toc45-toc-in-collapsible", "[[collapsible]]\n[[toc]]\n[[/collapsible]]\n\n+ A")
add("toc46-toc-in-quote", "> [[toc]]\n\n+ A")
add("toc47-toc-in-list", "* [[toc]]\n\n+ A")
add("toc48-toc-in-footnote", "[[footnote]]\n[[toc]]\n[[/footnote]]\n\n+ A\n\n[[footnoteblock]]")
add("toc49-iftags-mid-name", "[[t[[iftags -zzz]][[/iftags]]oc]]\n\n+ A")
add("toc50-author-anchor-collision", "[[# toc1]]\n\n+ One\n\n+ Two\n\n[[# toc0]]\n\n[[toc]]")

# --- malformed / near-miss forms -------------------------------------------
add("toc60-uppercase", "[[TOC]]\n\n+ A")
add("toc61-mixedcase", "[[Toc]]\n\n+ A")
add("toc62-gt-align", "[[>toc]]\n\n+ A")
add("toc63-star", "[[*toc]]\n\n+ A")
add("toc64-score", "[[_toc]]\n\n+ A")
add("toc65-prefix-suffix", "x[[toc]]y\n\n+ A")
add("toc66-indented", "  [[toc]]\n\n+ A")
add("toc67-tabbed", "\t[[toc]]\n\n+ A")
add("toc68-trailing-space", "[[toc ]]\n\n+ A")
add("toc69-two-spaces", "[[toc  title=\"X\"]]\n\n+ A")
add("toc70-tab-sep", "[[toc\ttitle=\"X\"]]\n\n+ A")
add("toc71-unterminated", "[[toc\n\n+ A")
add("toc72-stray-closer", "[[/toc]]\n\n+ A")
add("toc73-same-line-text", "[[toc]] trailing\n\n+ A")
add("toc74-clear-float", "[[toc]]~~~~\n\n+ A")
add("toc75-tocx", "[[toctest]]\n\n+ A")

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "battery.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for rec in CASES:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("wrote", len(CASES), "cases to", out)
