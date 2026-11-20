import json

cases = [
    ("x01-basic", "[[collapsible]]\nApple\n[[/collapsible]]"),
    ("x02-inline", "[[collapsible]]Banana[[/collapsible]]"),
    ("x03-empty", "[[collapsible]]\n[[/collapsible]]"),
    ("x04-showhide", '[[collapsible show="+ Open" hide="- Close"]]Mango[[/collapsible]]'),
    ("x05-showtext", '[[collapsible showText="OPEN" hideText="CLOSE"]]Mango[[/collapsible]]'),
    ("x06-folded-no", '[[collapsible folded="no"]]Blueberry[[/collapsible]]'),
    ("x07-hideloc-both", '[[collapsible hideLocation="both"]]Pineapple[[/collapsible]]'),
    ("x08-attrs", '[[collapsible id="hider" class="myc" style="color: teal" data-x="ya"]]foo[[/collapsible]]'),
    ("x09-nested-same", "[[collapsible show=\"L1\"]]\nA\n[[collapsible show=\"L2\"]]\nB\n[[/collapsible]]\nC\n[[/collapsible]]"),
    ("x10-unterminated", "[[collapsible]]\nNever closed\nmore text"),
    ("x11-stray-closer", "text [[/collapsible]] more"),
    ("x12-cross-div", "[[collapsible]]\n[[div class=\"d\"]]inside[[/div]]\n[[/collapsible]]"),
    ("x13-malformed", "[[collapsible show=unquoted]]B[[/collapsible]]"),
    ("x14-double-count", "[[collapsible]]A[[/collapsible]]\n[[collapsible]]B[[/collapsible]]"),
]

with open("explore_battery.jsonl", "w") as f:
    for cid, src in cases:
        f.write(json.dumps({"id": cid, "source": src}) + "\n")
print("wrote", len(cases))
