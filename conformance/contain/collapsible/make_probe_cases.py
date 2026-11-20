import json

cases = [
    ("basic", "[[collapsible]]\nApple\n[[/collapsible]]"),
    ("inline", "[[collapsible]]Banana[[/collapsible]]"),
    ("empty", "[[collapsible]]\n[[/collapsible]]"),
    ("showhide", '[[collapsible show="+ Open" hide="- Close"]]\nMango\n[[/collapsible]]'),
    ("showtext", '[[collapsible showText="OPEN" hideText="CLOSE"]]\nMango\n[[/collapsible]]'),
    ("attrs", '[[collapsible id="hider" class="myc" style="color: teal" data-hider="ya"]]\nfoo\n[[/collapsible]]'),
    ("folded-no", '[[collapsible folded="no"]]\nBlueberry\n[[/collapsible]]'),
    ("hideloc-both", '[[collapsible hideLocation="both"]]\nPineapple\n[[/collapsible]]'),
    ("hideloc-bottom", '[[collapsible hideLocation="bottom"]]\nRaspberry\n[[/collapsible]]'),
    ("hideloc-neither", '[[collapsible hideLocation="neither"]]\nHidden\n[[/collapsible]]'),
    ("nested-same", '[[collapsible show="L1"]]\nA\n[[collapsible show="L2"]]\nB\n[[/collapsible]]\nC\n[[/collapsible]]'),
    ("uppercase", '[[COLLAPSIBLE id="up" Show="UPPER" hide="lower"]]BODY[[/COLLAPSIBLE]]'),
    ("singlequote", "[[collapsible show='+ SQ' hide='- SQ']]\nBODY\n[[/collapsible]]"),
    ("unquoted", "[[collapsible show=OPEN hide=CLOSE]]\nBODY\n[[/collapsible]]"),
    ("stray-closer", "text [[/collapsible]] more"),
    ("div-inside", '[[collapsible]]\n[[div class="d"]]inside[[/div]]\n[[/collapsible]]'),
    ("coll-inside-div", '[[div class="d"]]\n[[collapsible]]\ninside\n[[/collapsible]]\n[[/div]]'),
]

with open("probe-cases.jsonl", "w") as f:
    for cid, src in cases:
        f.write(json.dumps({"id": cid, "source": src}) + "\n")
print("wrote", len(cases), "probe cases")
