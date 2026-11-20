#!/usr/bin/env python3
"""Emit the Equationreference live probe set as JSONL."""
import json

P = [
    ("p-undefined", "X[[eref missing]]Y"),
    ("p-defined", "[[math a]]\nx\n[[/math]]\n[[eref a]]"),
    ("p-forward", "[[eref a]]\n[[math a]]\nx\n[[/math]]"),
    ("p-two", "[[math a]]\nx\n[[/math]]\n[[math b]]\ny\n[[/math]]\n[[eref a]] [[eref b]]"),
    ("p-dup", "[[math a]]\nx\n[[/math]]\n[[math a]]\ny\n[[/math]]\n[[eref a]]"),
    ("p-empty-arg", "[[eref ]]"),
    ("p-no-arg", "[[eref]]"),
    ("p-tab", "[[math a]]\nx\n[[/math]]\n[[eref\ta]]"),
    ("p-two-spaces", "[[math a]]\nx\n[[/math]]\n[[eref  a]]"),
    ("p-uppercase", "[[math a]]\nx\n[[/math]]\n[[EREF a]]"),
    ("p-equation-name", "[[math a]]\nx\n[[/math]]\n[[equation a]]"),
    ("p-eqref-name", "[[math a]]\nx\n[[/math]]\n[[eqref a]]"),
    ("p-case-label", "[[math a]]\nx\n[[/math]]\n[[eref A]]"),
    ("p-multiword", "[[eref a b]]"),
    ("p-pipe", "[[math a]]\nx\n[[/math]]\n[[eref a|text]]"),
    ("p-underscore-label", "[[math a_b]]\nx\n[[/math]]\n[[eref a_b]]"),
    ("p-adjacent", "[[math a]]\nx\n[[/math]][[eref a]]"),
    ("p-space-adjacent", "[[math a]]\nx\n[[/math]] [[eref a]]"),
    ("p-midline", "[[math a]]\nx\n[[/math]]\nHello [[eref a]] world."),
    ("p-div", "[[div]]\n[[math a]]\nx\n[[/math]]\n[[eref a]]\n[[/div]]"),
    ("p-quote", "[[math a]]\nx\n[[/math]]\n> [[eref a]]"),
    ("p-bold", "[[math a]]\nx\n[[/math]]\n**[[eref a]]**"),
    ("p-triple-close", "[[math a]]\nx\n[[/math]]\n[[eref a]]]"),
    ("p-two-refs-one-eq", "[[math a]]\nx\n[[/math]]\n[[eref a]] and [[eref a]]"),
    ("p-unterminated", "[[eref a"),
    ("p-whitespace-label", "[[eref   ]]"),
]

with open("probe-cases.jsonl", "w", encoding="utf-8") as fh:
    for cid, source in P:
        fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
print(f"wrote {len(P)} probes")
