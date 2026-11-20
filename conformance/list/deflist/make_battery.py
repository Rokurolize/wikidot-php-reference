#!/usr/bin/env python3
"""Generate the R2 Deflist whole-document battery as JSONL.

Each source is LF-only and has trailing newlines stripped, because Wikidot
normalizes line endings and strips a final newline on save. The cases cover
the colon-led term and definition form, the definition-only continuation and
residue forms, empty and malformed terms and definitions, colons inside
content, blank-line and block interruption, unterminated lists at document
end, inline markup spanning definition lines, and deflist shapes inside
bibliography bodies, which the NOTES stage routed to this family.
"""
import json

CASES = [
    ("def01-basic-single", ": term : definition"),
    ("def02-basic-multi", ": Alpha : One\n: Beta : Two"),
    ("def03-inline-bold", ": **Key** : //value//"),
    ("def04-leading-prose", "Intro line\n: k : v"),
    ("def05-blank-before", "Intro\n\n: k : v"),
    ("def06-trailing-prose", ": k : v\nTrailing prose"),
    ("def07-blank-separated-two", ": a : 1\n\n: b : 2"),
    ("def08-empty-term", ":  : Value"),
    ("def09-empty-term-many-spaces", ":     : Value"),
    ("def10-empty-def-no-trailing", ": Term :"),
    ("def11-empty-def-trailing-space", ": Term : "),
    ("def12-empty-def-blank-then", ": Term :\n\n: B : 2"),
    ("def13-empty-def-glued", ": A : 1\n: Term :\n: B : 2"),
    ("def14-multiple-defs", ": A : 1\n: A : 2\n: A : 3"),
    ("def15-colon-in-def", ": key : a: b: c"),
    ("def16-colon-in-term", ": a:b : value"),
    ("def17-sep-no-space-after", ": A :1\n: B : 2"),
    ("def18-sep-tab-after", ": A :\tTabbed"),
    ("def19-semicolon-form", "; term : definition"),
    ("def20-semicolon-mixed", "; term : definition\n: real : def"),
    ("def21-no-space-leading", ":Key:Value"),
    ("def22-no-space-leading2", ":term : def"),
    ("def23-missing-separator", ": term"),
    ("def24-residue-vanish", "text before\n: key value\ntext after"),
    ("def25-just-colon-space", ": "),
    ("def26-colon-only", ":"),
    ("def27-tab-prefix", ":\t: value"),
    ("def28-leading-space", " : A : 1\n: B : 2"),
    ("def29-two-leading-spaces", "  : A : 1"),
    ("def30-definition-only-continuation", ": term : def\n: more text"),
    ("def31-heading-interrupt", ": a : A\n== Heading ==\n: b : B"),
    ("def32-code-interrupt", ": a : A\n[[code]]x[[/code]]\n: b : B"),
    ("def33-div-interrupt", ": a : A\n[[div class=x]]d[[/div]]\n: b : B"),
    ("def34-list-interrupt", ": a : A\n* one\n* two"),
    ("def35-list-then-deflist", "* one\n* two\n: a : A"),
    ("def36-quote-interrupt", ": a : A\n> quoted\n: b : B"),
    ("def37-deflist-in-div", "[[div class=x]]\n: a : A\n[[/div]]"),
    ("def38-deflist-in-collapsible", "[[collapsible]]\n: a : A\n[[/collapsible]]"),
    ("def39-deflist-in-quote", "> : a : A\n> : b : B"),
    ("def40-bold-cross-lines", ": a : **x\n: b : y**"),
    ("def41-iftags-in-value", ": term : [[iftags -zzz]]A\n\nB[[/iftags]]"),
    ("def42-multiline-value", ": Pineapple : Very very long\nwith a newline break"),
    ("def43-comment-term", ": [!-- c --] : e"),
    ("def44-item-inside-list", "[[ul]]\n[[li]]\n: a : A\n[[/li]]\n[[/ul]]"),
    ("def45-bib-closed", "((bibcite a))\n\n[[bibliography]]\n: a : Alpha\n[[/bibliography]]"),
    ("def46-bib-multi", "((bibcite a)) ((bibcite b))\n\n[[bibliography]]\n: a : Alpha\n: b : Bravo\n[[/bibliography]]"),
    ("def47-bib-direct-colon", "((bibcite a))\n\n[[bibliography]]\n: a: Alpha\n[[/bibliography]]"),
    ("def48-bib-malformed", "((bibcite a))\n\n[[bibliography]]\n: b :Bravo\n: a : Alpha\n[[/bibliography]]"),
    ("def49-bib-empty-value", "((bibcite a))\n\n[[bibliography]]\n: a :\n[[/bibliography]]"),
    ("def50-bib-unclosed", "[[bibliography]]\n: a : A"),
    ("def51-bib-residual", "[[bibliography]]\n: a : A\nprose line\n[[/bibliography]]"),
    ("def52-bib-next-line", "((bibcite a))\n\n[[bibliography]]\n: a:\nValue next line\n[[/bibliography]]"),
    ("def53-bib-duplicate", "((bibcite a))\n\n[[bibliography]]\n: a : First\n: a : Second\n[[/bibliography]]"),
    ("def54-bib-colon-content", "((bibcite a))\n\n[[bibliography]]\n: a : A: with colon\n[[/bibliography]]"),
    ("def55-unicode-empty", ": 用語 : 定義\n: 空 :"),
    ("def56-unicode-combined", ":  : Value\n: key : "),
    ("def57-double-colon-start", ":: term : definition"),
    ("def58-many-colons", ": a : b : c : d"),
    ("def59-bib-label-charset", "((bibcite smith2020)) ((bibcite 2b))\n\n[[bibliography]]\n: smith2020 : Smith 2020.\n: smith-2020 : Never.\n: 2b : Or not.\n[[/bibliography]]"),
    ("def60-trailing-blank-lines", ": a : A\n\n\n"),
]

with open("battery.jsonl", "w", encoding="utf-8") as fh:
    for cid, source in CASES:
        source = source.replace("\r\n", "\n").rstrip("\n")
        fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
print("wrote", len(CASES), "cases")
