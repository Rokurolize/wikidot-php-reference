#!/usr/bin/env python3
"""Emit the Equationreference R2 differential battery as JSONL."""
import json

C = []


def add(cid, source):
    C.append({"id": cid, "source": source})


# Canonical and numbered references
add("e01", "[[eref a]]")
add("e02", "[[math a]]\nx\n[[/math]]\n[[eref a]]")
add("e03", "[[eref a]]\n[[math a]]\nx\n[[/math]]")
add("e04", "X[[eref a]]Y")
add("e05", "[[math a]]\nx\n[[/math]]\nX[[eref a]]Y")
add("e06", "[[math a]]\nx\n[[/math]]\n[[math b]]\ny\n[[/math]]\n[[eref a]] [[eref b]]")
add("e07", "[[math a]]\nx\n[[/math]]\n[[math a]]\ny\n[[/math]]\n[[eref a]]")
add("e08", "[[math a]]\nx\n[[/math]]\n[[eref a]]\n[[math b]]\ny\n[[/math]]\n[[eref b]]")
add("e51", "[[math a]]\nx\n[[/math]]\n[[math b]]\ny\n[[/math]]\n[[eref b]]")
add("e52", "[[math]]\nx\n[[/math]]\n[[math a]]\ny\n[[/math]]\n[[eref a]]")

# Opener and bracket/closer variations
add("e09", "[[eref]]")
add("e10", "[[eref ]]")
add("e11", "[[eref  a]]")
add("e12", "[[eref\ta]]")
add("e13", "[[eref a ]]")
add("e14", "[[eref  a  ]]")
add("e15", "[[EREF a]]")
add("e16", "[[Eref a]]")
add("e17", "[[equation a]]")
add("e18", "[[eqref a]]")
add("e19", "[[eref_a]]")
add("e20", "[[eref-a]]")
add("e21", "[[eref a")
add("e22", "[eref a]")
add("e23", "[[eref a]]]")
add("e24", "[[[eref a]]]")
add("e25", "[[eref a]]]tail")
add("e26", "[[eref a]]\n[[eref b]]")
add("e27", "[[eref]] [[eref a]]")
add("e28", "[[eref a]] [[eref]]")

# Label edges
add("e29", "[[eref   ]]")
add("e30", "[[eref a b]]")
add("e31", "[[eref a-b]]")
add("e32", "[[eref a_b]]")
add("e33", "[[math a]]\nx\n[[/math]]\n[[eref A]]")
add("e34", "[[math A]]\nx\n[[/math]]\n[[eref A]]")
add("e35", "[[math a]]\nx\n[[/math]]\n[[eref a|text]]")
add("e36", "[[math a]]\nx\n[[/math]]\n[[eref a]] and [[eref a]] again")
add("e38", "[[math a type=\"align\"]]\nx\n[[/math]]\n[[eref a]]")
add("e55", "[[math a:b]]\nx\n[[/math]]\n[[eref a:b]]")
add("e57", "[[eref a]]\nafter")
add("e58", "[[math a=b]]\nx\n[[/math]]\n[[eref a=b]]")

# Position and adjacency with Math and other rules
add("e39", "[[math a]]\nx\n[[/math]]\n\n[[eref a]]\n")
add("e40", "[[code]]\n[[eref a]]\n[[/code]]")
add("e41", "[[div]]\n[[eref a]]\n[[/div]]")
add("e42", "[[collapsible]]\n[[eref a]]\n[[/collapsible]]")
add("e43", "text[[footnote]]\n[[math a]]\nx\n[[/math]]\n[[eref a]]\n[[/footnote]]")
add("e44", "[[math a]]\nx\n[[/math]]\n[[$ y $]] [[eref a]]")
add("e45", "[[math a]]\nx\n[[/math]][[eref a]]")
add("e46", "[[math a]]\nx\n[[/math]] [[eref a]]")
add("e47", "> [[eref a]]")
add("e48", "**[[eref a]]**")
add("e49", "[[eref b]] [[math a]]\nx\n[[/math]]\n[[math b]]\ny\n[[/math]]")
add("e50", "[[math a]]\nx\n[[/math]]\n[[eref a]]b[[eref a]]")
add("e54", "[[math a]]\n\\begin{align}\nx \\\\ y\n\\end{align}\n[[/math]]\n[[eref a]]")
add("e56", "[[eref long-label-with-digits-123]]")
add("e53", "[[math a]]\n\\alpha + \\beta\n[[/math]]\n[[eref a]]")

if __name__ == "__main__":
    with open("battery.jsonl", "w", encoding="utf-8") as fh:
        for case in C:
            fh.write(json.dumps(case, ensure_ascii=False) + "\n")
    print(f"wrote {len(C)} cases")
