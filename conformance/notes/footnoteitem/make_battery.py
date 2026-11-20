#!/usr/bin/env python3
"""Generate the Footnoteitem R2 battery of WHOLE DOCUMENTS.

Footnoteitem has regex=null: its tokens are emitted only by Footnoteblock,
which wraps each collected note in a start/end Footnoteitem token pair that
renders the <div class="footnote-footer"> wrapper and back-reference. So every
case here is a whole document that gathers at least one note and renders a
block (or deliberately does not, to observe the no-block seam). Sources are
LF-only with trailing newlines stripped, as Wikidot normalizes on save.
"""
import json

# (id, source). Trailing newlines are stripped when emitted.
C = [
    # --- core: one note, one block -------------------------------------
    ("fni-01-one", "Apple[[footnote]]Alpha[[/footnote]] banana.\n\n[[footnoteblock]]"),
    ("fni-02-two", "A[[footnote]]one[[/footnote]] B[[footnote]]two[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-03-three", "a[[footnote]]first[[/footnote]] b[[footnote]]second[[/footnote]] c[[footnote]]third[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-04-four", "w[[footnote]]W[[/footnote]] x[[footnote]]X[[/footnote]] y[[footnote]]Y[[/footnote]] z[[footnote]]Z[[/footnote]]\n\n[[footnoteblock]]"),
    # --- empty bodies --------------------------------------------------
    ("fni-05-empty-one", "A[[footnote]][[/footnote]] B\n\n[[footnoteblock]]"),
    ("fni-06-empty-mixed", "A[[footnote]][[/footnote]] B[[footnote]]plain[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-07-empty-ws", "A[[footnote]]   [[/footnote]] B[[footnote]]\n\t\n[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-08-all-empty", "A[[footnote]][[/footnote]] B[[footnote]][[/footnote]] C[[footnote]][[/footnote]]\n\n[[footnoteblock]]"),
    # --- nested markup inside note bodies ------------------------------
    ("fni-09-bold-italic", "X[[footnote]]This has **bold** and //italics// and ##mono##.[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-10-link", "X[[footnote]]See [http://example.com the example] and [[wiki page]].[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-11-multiline", "X[[footnote]]\nThis note spans two lines.\nAnd a third.\n[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-12-paragraphs", "X[[footnote]]First paragraph.\n\nSecond paragraph after a blank line.\n[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-13-list-body", "X[[footnote]]\n* one\n* two\n* three\n[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-14-blockquote-body", "X[[footnote]]\n> quoted note body\n> second line\n[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-15-div-body", "X[[footnote]]\n[[div class=\"note-body\"]]\nInside a div.\n[[/div]]\n[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-16-code-body", "X[[footnote]]A code span ``some <code> & raw`` inside.[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-17-html-special", "X[[footnote]]Quotes \" and ' and amp & and < > tags.[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-18-nested-footnote", "X[[footnote]]outer note[[footnote]]inner note[[/footnote]] tail[[/footnote]]\n\n[[footnoteblock]]"),
    # --- block position ------------------------------------------------
    ("fni-19-block-first", "[[footnoteblock]]\n\nAlpha[[footnote]]note A[[/footnote]]\n\nBeta[[footnote]]note B[[/footnote]]"),
    ("fni-20-block-middle", "Alpha[[footnote]]note A[[/footnote]]\n\n[[footnoteblock]]\n\nBeta[[footnote]]note B[[/footnote]]"),
    ("fni-21-block-last", "Alpha[[footnote]]note A[[/footnote]]\n\nBeta[[footnote]]note B[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-22-two-blocks", "Alpha[[footnote]]A[[/footnote]]\n[[footnoteblock]]\n\nBeta[[footnote]]B[[/footnote]]\n[[footnoteblock]]"),
    ("fni-23-block-with-tail", "Alpha[[footnote]]A[[/footnote]]\n\n[[footnoteblock]]\n\nTrailing paragraph after the block."),
    # --- no block / empty block ---------------------------------------
    ("fni-24-no-block", "Alpha[[footnote]]note A[[/footnote]] and Beta[[footnote]]note B[[/footnote]] but no block."),
    ("fni-25-empty-block", "No notes at all here.\n\n[[footnoteblock]]"),
    ("fni-26-empty-block-bare", "[[footnoteblock]]"),
    ("fni-27-two-empty-blocks", "No notes.\n\n[[footnoteblock]]\n\n[[footnoteblock]]"),
    # --- options on the block -----------------------------------------
    ("fni-28-title", "X[[footnote]]note[[/footnote]]\n\n[[footnoteblock title=\"My Notes\"]]"),
    ("fni-29-title-empty", "X[[footnote]]note[[/footnote]]\n\n[[footnoteblock title=\"\"]]"),
    ("fni-30-title-special", "X[[footnote]]note[[/footnote]]\n\n[[footnoteblock title=\"A & B's <notes>\"]]"),
    ("fni-31-hide", "X[[footnote]]note[[/footnote]]\n\n[[footnoteblock hide=\"true\"]]"),
    ("fni-32-title-unquoted", "X[[footnote]]note[[/footnote]]\n\n[[footnoteblock title=Custom]]"),
    # --- malformed / unterminated -------------------------------------
    ("fni-33-unterminated-note", "X[[footnote]]note with no close\n\n[[footnoteblock]]"),
    ("fni-34-stray-close", "X note with only a close[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-35-unterminated-then-good", "X[[footnote]]bad no close\nY[[footnote]]good[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-36-fused-close", "X[[footnote]]note A[[/footnote]][[footnote]]note B[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-37-malformed-block", "X[[footnote]]note[[/footnote]]\n\n[[footnoteblock"),
    ("fni-38-malformed-opener", "X[[footnote ]]note[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-39-uppercase", "X[[FOOTNOTE]]note[[/FOOTNOTE]]\n\n[[footnoteblock]]"),
    # --- adjacency with other family rules ----------------------------
    ("fni-40-with-bib", "A[[footnote]]note[[/footnote]] [[bibitem alpha]]Entry A[[/bibitem]]\n\n[[bibliography]]\n[[bibcite alpha]]\n[[/bibliography]]\n\n[[footnoteblock]]"),
    ("fni-41-bibcite-before", "A[[footnote]]note[[/footnote]] see [[bibcite alpha]].\n\n[[bibliography]]\n[[bibitem alpha]]Entry A[[/bibitem]]\n[[/bibliography]]\n\n[[footnoteblock]]"),
    ("fni-42-undefined-bibcite", "A[[footnote]]note[[/footnote]] see [[bibcite missing]].\n\n[[footnoteblock]]"),
    ("fni-43-dup-biblabel", "A[[footnote]]note[[/footnote]]\n\n[[bibliography]]\n[[bibitem alpha]]One[[/bibitem]]\n[[bibitem alpha]]Two[[/bibitem]]\n[[bibcite alpha]]\n[[/bibliography]]\n\n[[footnoteblock]]"),
    # --- notes inside other constructs (numbering seams, for context) --
    ("fni-44-note-in-div", "[[div]]\nInside[[footnote]]note in div[[/footnote]]\n[[/div]]\n\n[[footnoteblock]]"),
    ("fni-45-note-in-quote", "> Quoted[[footnote]]note in quote[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-46-note-in-list", "* item[[footnote]]note in list[[/footnote]]\n* second\n\n[[footnoteblock]]"),
    ("fni-47-note-in-collapsible", "[[collapsible show=\"open\"]]\nInside[[footnote]]note in collapsible[[/footnote]]\n[[/collapsible]]\n\n[[footnoteblock]]"),
    # --- unicode and edge shapes --------------------------------------
    ("fni-48-unicode", "Café[[footnote]] naïve résumé — 日本語 漢字 🎯[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-49-repeated-marker", "Same[[footnote]]shared note[[/footnote]] and again[[footnote]]shared note[[/footnote]]\n\n[[footnoteblock]]"),
    ("fni-50-block-in-div", "[[div]]\nA[[footnote]]note[[/footnote]]\n[[footnoteblock]]\n[[/div]]"),
]

with open("battery.jsonl", "w", encoding="utf-8") as fh:
    for cid, source in C:
        source = source.rstrip("\n")
        fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
print("wrote", len(C), "cases")
