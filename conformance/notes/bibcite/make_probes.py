import json

cases = []
def add(cid, source):
    cases.append({"id": cid, "source": source})

add("p-id-defined", "[[bibliography]]\n: alpha : Alpha source\n[[/bibliography]]\n\n((bibcite alpha))")
add("p-id-two-cites", "((bibcite alpha)) and ((bibcite beta))\n\n[[bibliography]]\n: alpha : A source\n: beta : B source\n[[/bibliography]]")
add("p-id-forward", "((bibcite alpha))\n\n[[bibliography]]\n: alpha : Alpha source\n[[/bibliography]]")
add("p-undef", "A((bibcite alpha))B")
add("p-two-space", "((bibcite  alpha))\n\n[[bibliography]]\n: alpha : A\n[[/bibliography]]")
add("p-three-space", "((bibcite   A9))\n\n[[bibliography]]\n: A9 : A9 source\n[[/bibliography]]")
add("p-tab-sep", "((bibcite\tTabbed))\n\n[[bibliography]]\n: Tabbed : T\n[[/bibliography]]")
add("p-newline-sep", "((bibcite\nalpha))\n\n[[bibliography]]\n: alpha : A\n[[/bibliography]]")
add("p-dup-label", "((bibcite bell)) ((bibcite guy))\n\n[[bibliography]]\n: bell : first bell\n: bell : second bell\n: guy : a guy\n[[/bibliography]]")
add("p-case-mismatch", "((bibcite ALPHA))\n\n[[bibliography]]\n: alpha : A\n[[/bibliography]]")
add("p-block-defined", "[[bibcite alpha]]\n\n[[bibliography]]\n: alpha : A\n[[/bibliography]]")
add("p-block-score-defined", "[[bibcite_ alpha]]\n\n[[bibliography]]\n: alpha : A\n[[/bibliography]]")
add("p-comment-label", "[[bibliography]]\n: key : def\n[[/bibliography]]\n\n((bibcite k[!--x--]ey))")
add("p-empty-label", "X((bibcite ))Y")
add("p-raw-owner", "@@((bibcite alpha))@@")
add("p-anchor", '[[a href="/A"]]x((bibcite b1))y[[/a]]\n\n[[bibliography]]\n: b1 : Title\n[[/bibliography]]')
add("p-footnote", "[[footnote]]A note[[/footnote]]\n\n[[bibliography]]\n: alpha : A\n[[/bibliography]]\n\n((bibcite alpha))")
add("p-malformed", "((bibcite alpha beta)) ((bibcite alpha\n\nbeta)) ((bibcite")

with open("probe-cases.jsonl", "w", encoding="utf-8") as f:
    for case in cases:
        f.write(json.dumps(case, ensure_ascii=False) + "\n")
print("wrote", len(cases), "probe cases")
