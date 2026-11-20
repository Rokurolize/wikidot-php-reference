#!/usr/bin/env python3
"""Build the Size R2 differential battery (JSONL {"id","source"[,"tags"]})."""
import json

C = []
def add(cid, src, tags=None):
    row = {"id": cid, "source": src}
    if tags is not None:
        row["tags"] = tags
    C.append(row)

# --- value forms: accepted by live (ftml corpus pins) --------------------
add("sz01-pct", "[[size 90%]]Banana[[/size]]")
add("sz02-px", "[[size 4px]]Cherry[[/size]]")
add("sz03-em-leading-dot", "[[size .5em]]X[[/size]]")
add("sz04-em-decimal", "[[size 1.5em]]X[[/size]]")
add("sz05-pct-integer", "[[size 100%]]X[[/size]]")
add("sz06-named-small", "[[size small]]X[[/size]]")
add("sz07-named-xxsmall", "[[size xx-small]]X[[/size]]")
add("sz08-named-medium", "[[size medium]]X[[/size]]")
add("sz09-named-larger", "[[size larger]]X[[/size]]")
add("sz10-named-xxlarge", "[[size xx-large]]X[[/size]]")
add("sz11-long-digits-px", "[[size 123456px]]X[[/size]]")
add("sz12-long-digits-pct", "[[size 1000000%]]X[[/size]]")
add("sz13-multi-dot-px", "[[size 1.2.3px]]X[[/size]]")
add("sz14-trailing-dot-px", "[[size 1.px]]X[[/size]]")
add("sz15-dot-only-px", "[[size .px]]X[[/size]]")

# --- value forms: rejected by live (ftml parity-gap pins) ---------------
add("sz16-pt-unit", "[[size 12pt]]X[[/size]]")
add("sz17-rem-unit", "[[size 1rem]]X[[/size]]")
add("sz18-vh-unit", "[[size 2vh]]X[[/size]]")
add("sz19-negative-px", "[[size -1px]]X[[/size]]")
add("sz20-plus-px", "[[size +1px]]X[[/size]]")
add("sz21-exponent-pct", "[[size 1e2%]]X[[/size]]")
add("sz22-inf-pct", "[[size inf%]]X[[/size]]")
add("sz23-nan-pct", "[[size NaN%]]X[[/size]]")
add("sz24-upper-larger", "[[size LARGER]]X[[/size]]")
add("sz25-title-larger", "[[size Larger]]X[[/size]]")
add("sz26-upper-px", "[[size 80PX]]X[[/size]]")
add("sz27-upper-em", "[[size 1EM]]X[[/size]]")
add("sz28-upper-small", "[[size SMALL]]X[[/size]]")
add("sz29-upper-xlarge", "[[size X-LARGE]]X[[/size]]")
add("sz30-nbsp-arg", "[[size \u00a0100%\u00a0]]X[[/size]]")
add("sz31-no-arg", "[[size]]X[[/size]]")
add("sz32-junk", "[[size banana]]X[[/size]]")

# --- opener/name case, quoting and attribute variants -------------------
add("sz33-opener-upper", "[[SIZE 100%]]X[[/SIZE]]")
add("sz34-opener-title", "[[Size 100%]]X[[/Size]]")
add("sz35-opener-mixed-closer", "[[SiZe larger]]X[[/sIzE]]")
add("sz36-leading-space-name", "[[ size 100%]]X[[/size]]")
add("sz37-double-space", "[[size  100%]]X[[/size]]")
add("sz38-tab-separator", "[[size\t100%]]X[[/size]]")
add("sz39-newline-in-head", "[[size\n100%]]X[[/size]]")
add("sz40-equals-form", "[[size=100%]]X[[/size=]]")
add("sz41-quoted-value", '[[size "100%"]]X[[/size]]')
add("sz42-trailing-head-space", "[[size 100% ]]X[[/size]]")
add("sz43-entity-head", "[[size 100&#37;]]X[[/size]]")
add("sz44-escaped-head", "[[size 100\\%]]X[[/size]]")
add("sz45-extra-close-in-head", "[[size 100%]]]X[[/size]]")
add("sz46-attr-like", '[[size 100% class="x"]]X[[/size]]')

# --- empty bodies, unterminated and stray closers -----------------------
add("sz47-empty-body", "[[size 100%]][[/size]]")
add("sz48-whitespace-body", "[[size 100%]]   [[/size]]")
add("sz49-unterminated", "[[size 100%]]text")
add("sz50-stray-closer", "text[[/size]]")
add("sz51-space-before-close", "[[size 120%]]x [[/size]]")
add("sz52-double-close", "[[size 80%]]x[[/size]]y[[/size]]")
add("sz53-space-in-closer", "[[size 80%]]x[[/size ]]")
add("sz54-unpaired-close-preserved", "[[SIZE]]outer [[size 80%]]valid[[/size]] tail[[/SIZE]] [[size 90%]]later[[/size]]")

# --- same-rule and cross-rule nesting ----------------------------------
add("sz55-nested-pair", "[[size 80%]]a[[size 90%]]b[[/size]]c[[/size]]")
add("sz56-crossed-pair", "[[size 80%]]a[[size 90%]]b[[/size]]c[[/size]]d")
add("sz57-size-in-span", '[[span class="x"]]a[[size 80%]]b[[/size]]c[[/span]]')
add("sz58-span-in-size", '[[size 80%]]a[[span class="x"]]b[[/span]]c[[/size]]')
add("sz59-cross-size-span", '[[size 80%]]a[[span class="x"]]b[[/size]]c[[/span]]')
add("sz60-size-in-color", '[[color red]]a[[size 80%]]b[[/size]]c[[/color]]')
add("sz61-color-in-size", '[[color red]]a[[size 80%]]b[[/color]]c[[/size]]')
add("sz62-size-in-strike", '[[strikethrough]]a[[size 80%]]b[[/size]]c[[/strikethrough]]')
add("sz63-strike-in-size", '[[strikethrough]]a[[size 80%]]b[[/strikethrough]]c[[/size]]')

# --- inline content in block containers, block content in inline --------
add("sz64-size-in-div", '[[div class="d"]]\n[[size 80%]]x[[/size]]\n[[/div]]')
add("sz65-size-in-blockquote", "[[blockquote]]\n[[size 80%]]x[[/size]]\n[[/blockquote]]")
add("sz66-size-in-list", "* [[size 80%]]x[[/size]]\n* y")
add("sz67-size-in-heading", "+ [[size 80%]]x[[/size]]")
add("sz68-div-in-size", '[[size 80%]]a[[div class="d"]]b[[/div]]c[[/size]]')
add("sz69-list-in-size", "[[size 80%]]a\n* x\n* y\n[[/size]]")
add("sz70-size-crosses-div", '[[size larger]]\n[[div class="outer"]]\nheader\n[[div class="links"]]\nlink\n[[/div]]\n[[div class="content"]]\n[[/size]]\nbody\n[[/div]]\n[[/div]]')

# --- malformed and adjacency shapes from the ftml size corpus ----------
add("sz71-stray-close-bridge", "[[size 80%]]a[[/size]][[/size]]b")
add("sz72-crossed-closers", "[[size 80%]]a[[size 90%]]b[[/size]]c[[/size]]")
add("sz73-code-content-wrapped", "[[size 80%]][[code]]x[[/code]][[/size]]")
add("sz74-bold-crossed", "**[[size 110%]]OVERWATCH COUNCIL**[[/size]]")
add("sz75-list-bold-close", "[[size 80%]]* **a**\n* b\n[[/size]]")
add("sz76-unicode-body", "[[size 80%]]caf\u00e9 \u65e5\u672c\u8a9e[[/size]]")
add("sz77-entities-body", "[[size 80%]]&amp; &lt; &#39;[[/size]]")
add("sz78-comment-in-head", "[[size [% comment %]80%]]X[[/size]]")
add("sz79-nul-body", "[[size 120%]]A\u0000B[[/size]]")
add("sz80-multiple-pairs", "[[size 80%]]a[[/size]] [[size 90%]]b[[/size]]")

with open("battery.jsonl", "w", encoding="utf-8") as f:
    for row in C:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
print("wrote", len(C), "cases")
