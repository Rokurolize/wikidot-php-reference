#!/usr/bin/env python3
"""Generate the root R2-inline3 cross-rule interaction battery.

This is the FINAL R2 stage; the battery owns the seams the five per-rule
batteries cannot own: the five Inline-2 markers composed with this stage's
Tt {{}}, Superscript ^^ and Subscript ,, forms, typography replacements
inside and outside paired markers, monospace shielding of everything inside
it, super/subscript pairing against the emphasis family, Tighten's effect on
every earlier rule's settled output, and the pipeline-final check that the
whole inline family composes in source order. Sources are LF-only with no
trailing newline because Wikidot strips one on save.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The five paired markers of the Inline-2 family.
I2 = {
    "C": ("##red|", "##"),   # Colortext
    "B": ("**", "**"),       # Strong
    "I": ("//", "//"),       # Emphasis
    "U": ("__", "__"),       # Underline
    "S": ("--", "--"),       # Strikethrough
}
# This stage's three new paired markers.
NEW = {
    "T": ("{{", "}}"),       # Tt (monospace)
    "P": ("^^", "^^"),       # Superscript
    "R": (",,", ",,"),       # Subscript
}
ALL = {**I2, **NEW}


def main():
    cases = []

    def add(cid, source, note):
        cases.append({"id": cid, "source": source, "note": note})

    n = 0

    # 1. Each new marker crossed with each Inline-2 marker: ordered crossing
    #    and proper-nesting control, both orientations by construction.
    for nm in ("T", "P", "R"):
        no, nc = NEW[nm]
        for k, (ko, kc) in I2.items():
            n += 1
            add(f"x{n:02d}", f"{no}a{ko}ab{nc}ba{kc}",
                f"cross {nm}-outer {k}-inner: {no} a {ko} ab {nc} ba {kc}")
            n += 1
            add(f"x{n:02d}", f"{no}a{ko}ab{kc}ba{nc}",
                f"nested control {nm}-outer {k}-inner: {no} a {ko} ab {kc} ba {nc}")
            n += 1
            add(f"x{n:02d}", f"{ko}a{no}ab{kc}ba{nc}",
                f"cross {k}-outer {nm}-inner: {ko} a {no} ab {kc} ba {nc}")
            n += 1
            add(f"x{n:02d}", f"{ko}a{no}ab{nc}ba{kc}",
                f"nested control {k}-outer {nm}-inner: {ko} a {no} ab {nc} ba {kc}")

    # 2. Crossings among the three new markers themselves.
    keys = list(NEW)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            ao, ac = NEW[a]
            bo, bc = NEW[b]
            n += 1
            add(f"x{n:02d}", f"{ao}a{bo}ab{ac}ba{bc}",
                f"cross {a}-outer {b}-inner")
            n += 1
            add(f"x{n:02d}", f"{ao}a{bo}ab{bc}ba{ac}",
                f"nested control {a}-outer {b}-inner")
            n += 1
            add(f"x{n:02d}", f"{bo}a{ao}ab{bc}ba{ac}",
                f"cross {b}-outer {a}-inner")
            n += 1
            add(f"x{n:02d}", f"{bo}a{ao}ab{ac}ba{bc}",
                f"nested control {b}-outer {a}-inner")

    specials = [
        # Monospace shielding: everything inside {{}} is literal on all sides.
        ("monospace shields every inline marker",
         "@@skip@@ {{**b** //i// __u__ --s-- ^^p^^ ,,s,, ##red|c##}}"),
        ("monospace shields typography dashes and ellipsis",
         "{{a --- b ... c ``d'' `e' <<f>> 12 34}}"),
        ("monospace shields a protocol-relative URL",
         "{{see //example.com/path and http://x//y}}"),
        ("monospace with an unmatched inner closer",
         "{{a // b}} and {{c ,, d}}"),
        ("monospace pair at word boundaries and inside words",
         "pre{{mid}}post and {{ spaced }} and a{{}}b"),
        # Typography replacements inside and outside paired markers.
        ("dash and ellipsis outside markers",
         "a -- b --- c ... d"),
        ("dash and ellipsis inside strong / emphasis / underline",
         "**a -- b** //c --- d// __e ... f__"),
        ("dash and ellipsis inside super / sub / monospace",
         "^^a -- b^^ ,,c --- d,, {{e ... f}}"),
        ("dash run crossing a paired-marker boundary",
         "**a ---b--- c** and ^^d ---e--- f^^"),
        ("quote and guillemet typography inside paired markers",
         "**``a''** ^^`b'^^ ,,<<c>>,,"),
        ("number/unit typography inside monospace",
         "{{10 kg and 2 3 and 5px}}"),
        ("typography entity spellings inside a link label",
         "[https://example.com a -- b ... c]"),
        # Super/subscript pairing against the emphasis family, boundary forms.
        ("superscript inner body with an emphasis pair",
         "^^a **b** c^^ and **^^a^^**"),
        ("subscript inner body with a monospace pair",
         ",,a {{b}} c,, and {{,,a,,}}"),
        ("superscript and subscript with padded and empty bodies",
         "^^ a ^^ ,, b ,, ^^^^ ,,,, ^^x^^^^ ,,,,y,,,,"),
        ("superscript crossing a newline and a paragraph break",
         "^^a\nb^^ and ^^c\n\nd^^"),
        ("subscript commalist prose beside a real pair",
         "a, b, c,,sub,, d, e and ,,a, b,, c"),
        # Tighten's effect on earlier rules' settled output.
        ("newline shaping in plain text and between paired markers",
         "a\nb\n\n**c**\n,,d,,\n{{e}}\n^^f^^"),
        ("whitespace at span edges around this stage's forms",
         "a ^^b^^ c ,,d,, e {{f}} g **h** i ##red|j## k"),
        ("consecutive newlines inside a color span and a monospace span",
         "##red|a\n\nb## and {{c\n\nd}}"),
        ("soft break crossing super and sub pairs",
         "^^a\nb^^ ,,c\nd,, **e\nf**"),
        ("underline empty-pair trailing-space surface with Tighten",
         "a____b and __ __ and __a__   b"),
        ("colortext leading/trailing span whitespace surface",
         "##red|  lead## ##red|trail  ## ##red| both ##"),
        # Pipeline-final: whole inline family in source order and reversed.
        ("whole inline family in pipeline source order",
         "##red|C**B//I__U--S{{T}}^^P^^,,R,,--S__U//I**B##C"),
        ("whole inline family in reverse open order",
         ",,R,,^^P^^{{T}}--S__U//I**B##red|C##"),
        ("three-level nesting of this stage's forms inside the family",
         "**b ^^p ,,s {{t}},, ^^ ** and //i {{a ^^b^^ c}} //"),
        ("all eight markers adjacent, none crossed",
         "##red|c## **b** //i// __u__ --s-- {{t}} ^^p^^ ,,r,,"),
        ("unpaired markers of every family member left literal",
         "a ##red| b ** c // d __ e -- f {{ g ^^ h ,, i"),
        # Container / block / cell / label / heading seams with new markers.
        ("new markers crossing a div container",
         "{{a[[div]]b}}c[[/div]] and ^^d[[div]]e^^f[[/div]]"),
        ("new markers crossing a native list item",
         "* ^^a\n* b^^ c\n* d and * {{e\n* f}} g"),
        ("new markers inside a table cell",
         "|| h || h ||\n| ^^a^^ | {{b}} |\n| ,,c,, | d |"),
        ("new markers inside a footnote body",
         "^^a[[footnote]]b^^c[[/footnote]]"),
        ("new markers inside link labels",
         "[https://example.com ^^a^^ {{b}} ,,c,,]"),
        ("new markers inside a heading",
         "= ^^a^^ {{b}} ,,c,, ="),
        ("new markers inside a code block shield",
         "[[code]]^^a^^ {{b}} ,,c,,[[/code]]"),
        ("new markers crossing an include seam",
         "^^a[[include:foo]]b^^c"),
    ]
    for note, source in specials:
        n += 1
        add(f"x{n:02d}", source, note)

    out = HERE / "xbattery.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for c in cases:
            # Only id and source go on the wire; note is documentation.
            f.write(json.dumps({"id": c["id"], "source": c["source"]},
                               ensure_ascii=False) + "\n")
    notes = HERE / "x-notes.json"
    notes.write_text(json.dumps({c["id"]: c["note"] for c in cases},
                                ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out} with {len(cases)} cases")


if __name__ == "__main__":
    main()
