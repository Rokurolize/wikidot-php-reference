import json

# R2-contain Collapsible battery. Coverage: G1.2 first-closer discipline,
# same-rule and cross-rule nesting, all option keys and quoting variants,
# empty bodies, unterminated and stray closers, inline content inside block
# containers, block/div/collapsible/tab inside the container, and malformed
# forms. Sources are single JSONL records; no tags are needed for this rule.
cases = []

def add(cid, source):
    cases.append((cid, source))

# --- basic shapes -------------------------------------------------------
add("c01-basic-line", "[[collapsible]]\nApple\n[[/collapsible]]")
add("c02-inline", "[[collapsible]]Banana[[/collapsible]]")
add("c03-empty", "[[collapsible]]\n[[/collapsible]]")
add("c04-empty-inline", "[[collapsible]][[/collapsible]]")
add("c05-leading-text", "Before\n[[collapsible]]\nBody\n[[/collapsible]]\nAfter")
add("c06-trailing-space", "[[collapsible]] \nBody\n[[/collapsible]]  ")
add("c07-uppercase", '[[COLLAPSIBLE id="up" show="UPPER" hide="lower"]]\nBODY\n[[/COLLAPSIBLE]]')
add("c08-internal-space", '[[ collapsible show="+ S" hide="- H" ]]\nBODY\n[[/collapsible]]')
add("c09-two-blocks", "[[collapsible]]A[[/collapsible]]\n[[collapsible]]B[[/collapsible]]")
add("c10-adjacent-inline", "[[collapsible]]A[[/collapsible]][[collapsible]]B[[/collapsible]]")

# --- options: labels ----------------------------------------------------
add("c11-show-only", '[[collapsible show="+ Expand"]]B[[/collapsible]]')
add("c12-hide-only", '[[collapsible hide="- Collapse"]]B[[/collapsible]]')
add("c13-show-hide", '[[collapsible show="+ Open" hide="- Close"]]B[[/collapsible]]')
add("c14-showtext", '[[collapsible showText="OPEN" hideText="CLOSE"]]B[[/collapsible]]')
add("c15-empty-labels", '[[collapsible show="" hide=""]]B[[/collapsible]]')
add("c16-label-nbsp-tab", '[[collapsible show="a\tb" hide="x  y"]]B[[/collapsible]]')
add("c17-label-entities", '[[collapsible show="A &amp; B &lt;x&gt;" hide="C &quot;d&quot;"]]B[[/collapsible]]')
add("c18-label-newline", '[[collapsible show="one\ntwo"]]B[[/collapsible]]')

# --- options: folded / hideLocation -------------------------------------
add("c19-folded-no", '[[collapsible folded="no"]]B[[/collapsible]]')
add("c20-folded-false", '[[collapsible folded="false"]]B[[/collapsible]]')
add("c21-folded-yes", '[[collapsible folded="yes"]]B[[/collapsible]]')
add("c22-hideloc-top", '[[collapsible hideLocation="top"]]B[[/collapsible]]')
add("c23-hideloc-bottom", '[[collapsible hideLocation="bottom"]]B[[/collapsible]]')
add("c24-hideloc-both", '[[collapsible hideLocation="both"]]B[[/collapsible]]')
add("c25-hideloc-neither", '[[collapsible hideLocation="neither"]]B[[/collapsible]]')
add("c26-hideloc-unknown", '[[collapsible hideLocation="sideways"]]B[[/collapsible]]')

# --- options: passthrough / quoting / unknown ---------------------------
add("c27-class", '[[collapsible class="myc"]]B[[/collapsible]]')
add("c28-id", '[[collapsible id="hider"]]B[[/collapsible]]')
add("c29-style", '[[collapsible style="color: teal"]]B[[/collapsible]]')
add("c30-data-unknown", '[[collapsible data-x="ya" bogus="z"]]B[[/collapsible]]')
add("c31-single-quotes", "[[collapsible show='+ SQ' hide='- SQ']]B[[/collapsible]]")
add("c32-unquoted-values", "[[collapsible show=OPEN hide=CLOSE]]B[[/collapsible]]")
add("c33-duplicate-folded", '[[collapsible folded="yes" folded="no"]]B[[/collapsible]]')
add("c34-unknown-key-only", '[[collapsible bananas="yes"]]B[[/collapsible]]')

# --- G1.2 closer discipline / nesting ----------------------------------
add("c35-nested-same", '[[collapsible show="L1"]]\nA\n[[collapsible show="L2"]]\nB\n[[/collapsible]]\nC\n[[/collapsible]]')
add("c36-nested-same-four", '[[collapsible]]\nA\n[[collapsible]]\nB\n[[collapsible]]\nC\n[[/collapsible]]\n[[/collapsible]]\n[[/collapsible]]')
add("c37-first-closer-tail", '[[collapsible]]\nA\n[[/collapsible]]\nTAIL\n[[/collapsible]]')
add("c38-opener-after-closer", '[[collapsible]]A[[/collapsible]]\n[[collapsible]]B[[/collapsible]]\n[[collapsible]]C[[/collapsible]]')
add("c39-cross-div-in", '[[collapsible]]\n[[div class="d"]]\ninside\n[[/div]]\n[[/collapsible]]')
add("c40-div-out", '[[div class="d"]]\n[[collapsible]]\ninside\n[[/collapsible]]\n[[/div]]')
add("c41-cross-tab-in", '[[collapsible]]\n[[tabview]]\n[[tab]]One[[/tab]]\n[[/tabview]]\n[[/collapsible]]')
add("c42-cross-footnote", '[[collapsible]]\nA footnote [[footnote]]note[[/footnote]] here\n[[/collapsible]]')

# --- inline content inside block containers / block inside inline -------
add("c43-bold-inside", '[[collapsible]]\n**bold** and //italic//\n[[/collapsible]]')
add("c44-link-inside", '[[collapsible]]\n[[http://example.com|link]]\n[[/collapsible]]')
add("c45-heading-inside", '[[collapsible]]\n= Heading =\nBody\n[[/collapsible]]')
add("c46-list-inside", '[[collapsible]]\n* one\n* two\n[[/collapsible]]')
add("c47-quote-inside", '[[collapsible]]\n> quoted\n[[/collapsible]]')
add("c48-code-inside", '[[collapsible]]\n[[code]]\ncode body\n[[/code]]\n[[/collapsible]]')

# --- unterminated / stray / malformed ----------------------------------
add("c49-unterminated", '[[collapsible]]\nNever closed\nmore text')
add("c50-stray-closer", 'text [[/collapsible]] more')
add("c51-closer-only-line", '[[/collapsible]]')
add("c52-missing-opener", 'plain\n[[/collapsible]]\nplain')
add("c53-malformed-opener", '[[collapsible show=BROKEN]]B[[/collapsible]]')
add("c54-unclosed-inline", 'before [[collapsible]] body after')
add("c55-wrong-closer", '[[collapsible]]B[[/div]]')
add("c56-empty-attr-braces", '[[collapsible ]]B[[/collapsible]]')
add("c57-newline-in-head", '[[collapsible\n show="+ X"\n]]\nB\n[[/collapsible]]')

with open("battery.jsonl", "w") as f:
    for cid, src in cases:
        f.write(json.dumps({"id": cid, "source": src}) + "\n")
print("wrote", len(cases), "battery cases")
