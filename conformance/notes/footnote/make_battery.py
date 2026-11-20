#!/usr/bin/env python3
"""Generate battery.jsonl for the R2-notes Footnote rule: WHOLE documents only.
Each record is a full page source exercising footnote matching, numbering into
wiki vars, and the superscript footnoteref anchor, in the context of real
page shapes (block present/absent/options, nested markup, malformed/unterminated
forms, adjacency with the other family rules in pipeline order).
"""
import json

CASES = []


def add(cid, source, tags=None):
    rec = {"id": cid, "source": source}
    if tags is not None:
        rec["tags"] = tags
    CASES.append(rec)


add("fn01-single", "Alpha[[footnote]]note[[/footnote]]")
add("fn02-two", "A[[footnote]]one[[/footnote]] B[[footnote]]two[[/footnote]]")
add("fn03-block-after", "A[[footnote]]one[[/footnote]] B[[footnote]]two[[/footnote]]\n\n[[footnoteblock]]")
add("fn04-block-before", "[[footnoteblock]]\n\nA[[footnote]]one[[/footnote]] B[[footnote]]two[[/footnote]]")
add("fn05-block-between", "A[[footnote]]one[[/footnote]]\n\n[[footnoteblock]]\n\nB[[footnote]]two[[/footnote]]")
add("fn06-two-blocks", "A[[footnote]]one[[/footnote]]\n[[footnoteblock]]\n\nB[[footnote]]two[[/footnote]]\n[[footnoteblock]]")
add("fn07-empty-body", "A[[footnote]][[/footnote]] B[[footnote]] x [[/footnote]]\n\n[[footnoteblock]]")
add("fn08-bold-italic-body", "A[[footnote]]**bold** and //ital// and __under__[[/footnote]]\n\n[[footnoteblock]]")
add("fn09-link-body", "A[[footnote]]see [http://example.com the site] and [[wikipedia:Footnote]]\\[[/footnote]]\n\n[[footnoteblock]]")
add("fn10-code-body", "A[[footnote]]code [[code]]x = 1;[[/code]] here[[/footnote]]\n\n[[footnoteblock]]")
add("fn11-math-body", "A[[footnote]]See [[math]] x^2 [[/math]] here[[/footnote]]\n\n[[footnoteblock]]")
add("fn12-list-body", "A[[footnote]]items\n* one\n* two[[/footnote]]\n\n[[footnoteblock]]")
add("fn13-quote-body", "A[[footnote]]excerpt\n> quoted text[[/footnote]]\n\n[[footnoteblock]]")
add("fn14-multiline-body", "Apple[[footnote]]\nfirst line\n\nsecond paragraph\nlast line\n[[/footnote]]\n\n[[footnoteblock]]")
add("fn15-unicode-body", "A[[footnote]]naïve café 日本語 **gras**[[/footnote]]\n\n[[footnoteblock]]")
add("fn16-uppercase-tag", "A[[FOOTNOTE]]up[[/FOOTNOTE]] B[[footnote]]low[[/footnote]]\n\n[[footnoteblock]]")
add("fn17-mixed-case-tag", "A[[FootNote]]mix[[/footnote]] B[[footnote]]two[[/FootNote]]\n\n[[footnoteblock]]")
add("fn18-space-in-opener", "A[[footnote ]]sp[[/footnote]] B[[footnote]]two[[/footnote]]\n\n[[footnoteblock]]")
add("fn19-unterminated", "A[[footnote]]never closed B[[footnote]]also open\n\n[[footnoteblock]]")
add("fn20-stray-closer", "X[[/footnote]] then B[[footnote]]bee[[/footnote]]\n\n[[footnoteblock]]")
add("fn21-nested-footnote", "before[[footnote]]outer [[footnote]]inner[[/footnote]] after[[/footnote]]\n\n[[footnoteblock]]")
add("fn22-block-in-footnote", "A[[footnote]]body [[footnoteblock]] tail[[/footnote]]\n\n[[footnoteblock]]")
add("fn23-fused-close", "x [[footnote]]note[[/footnote]]] y\n\n[[footnoteblock]]")
add("fn24-block-title", "Apple[[footnote]]Banana[[/footnote]]\n\n[[footnoteblock title=\"The feet-noten\"]]\n\nMore stuff underneath")
add("fn25-block-hide", "Apple[[footnote]]Banana[[/footnote]]\n\n[[footnoteblock hide=\"true\"]]")
add("fn26-block-bogus-arg", "Apple[[footnote]]Banana[[/footnote]]\n\n[[footnoteblock bogus=\"true\"]]")
add("fn27-block-title-empty", "Apple[[footnote]]Banana[[/footnote]]\n\n[[footnoteblock title=\"\"]]")
add("fn28-leading-newline", "Text before.\n\n[[footnote]]on its own line[[/footnote]]\n\nText after.\n\n[[footnoteblock]]")
add("fn29-leading-spaces", "A   [[footnote]]spaced opener[[/footnote]]   B[[footnote]]two[[/footnote]]\n\n[[footnoteblock]]")
add("fn30-many-notes", "".join("N%d[[footnote]]body %d[[/footnote]] " % (i, i) for i in range(1, 11)) + "\n\n[[footnoteblock]]")
add("fn31-block-then-more", "A[[footnote]]alpha[[/footnote]]\n[[footnoteblock]]\nB[[footnote]]beta[[/footnote]]\nC[[footnote]]gamma[[/footnote]]")
add("fn32-adj-bibitem", "A[[footnote]]note[[/footnote]]\n\n[[bibliography]]\n[[bibitem Smith2020]]Smith, A. Title.[[/bibitem]]\n[[/bibliography]]\n\nSee [[bibcite Smith2020]].\n\n[[footnoteblock]]")
add("fn33-adj-bibcite-before", "See [[bibcite Smith2020]] and A[[footnote]]note[[/footnote]].\n\n[[bibliography]]\n[[bibitem Smith2020]]Smith, A. Title.[[/bibitem]]\n[[/bibliography]]\n\n[[footnoteblock]]")
add("fn34-adj-undefined-bibcite", "A[[footnote]]note[[/footnote]] and [[bibcite Missing]]\n\n[[footnoteblock]]")
add("fn35-adj-footnoteitem", "A[[footnote]]note[[/footnote]] B[[footnoteitem]]item[[/footnoteitem]]\n\n[[footnoteblock]]")
add("fn36-div-wrapped", "[[div class=\"x\"]]\nA[[footnote]]inside div[[/footnote]]\n[[/div]]\n\n[[footnoteblock]]")
add("fn37-list-wrapped", "* A[[footnote]]inside list[[/footnote]]\n* B[[footnote]]second[[/footnote]]\n\n[[footnoteblock]]")
add("fn38-quote-wrapped", "> A[[footnote]]inside quote[[/footnote]]\n> tail\n\n[[footnoteblock]]")
add("fn39-collapsible-wrapped", "[[collapsible show=\"open\"]]\nA[[footnote]]inside collapsible[[/footnote]]\n[[/collapsible]]\n\n[[footnoteblock]]")
add("fn40-iftags-kept", "A[[footnote]]before[[/footnote]][[iftags tags=\"fn\"]]TAGGED[[/iftags]]B[[footnote]]after[[/footnote]]\n\n[[footnoteblock]]", tags=["fn"])
add("fn41-iftags-hidden", "A[[footnote]]before[[/footnote]][[iftags tags=\"other\"]]HIDDEN[[/iftags]]B[[footnote]]after[[/footnote]]\n\n[[footnoteblock]]", tags=["fn"])
add("fn42-brackets-in-body", "A[[footnote]]a [[ b ]] and [single] and [[/footnote]] done\n\n[[footnoteblock]]")
add("fn43-double-closer", "A[[footnote]]one[[/footnote]][[/footnote]] B[[footnote]]two[[/footnote]]\n\n[[footnoteblock]]")
add("fn44-across-paragraphs", "A[[footnote]]para one\n\npara two[[/footnote]] B[[footnote]]plain[[/footnote]]\n\n[[footnoteblock]]")
add("fn45-block-after-list", "* item\n* item2\n\nA[[footnote]]note[[/footnote]]\n\n[[footnoteblock]]")
add("fn46-table-cell", "|| head ||\n|| A[[footnote]]in cell[[/footnote]] ||\n\n[[footnoteblock]]")
add("fn47-header-note", "= Header[[footnote]]in header[[/footnote]] =\n\n[[footnoteblock]]")
add("fn48-no-notes", "Just a plain document with no footnotes at all.\n\n[[footnoteblock]]")
add("fn49-comment-around", "a[[foot[!--x--]note]]n[[/footnote]]\n\n[[footnoteblock]]")
add("fn50-bracket-prefix", "[[[[footnote]]n[[/footnote]]")
add("fn51-underscore-closer", "A[[footnote]]x[[/footnote_]] B[[footnote]]plain[[/footnote]]")
add("fn52-sameline-code-close", "A[[footnote]]See [[code]] x [[/code]] here[[/footnote]]\n\n[[footnoteblock]]")
add("fn53-empty-doc", "")

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "battery.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for rec in CASES:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("wrote", len(CASES), "cases to", out)
