#!/usr/bin/env python3
"""Build the Superscript rule's whole-document battery for R2-INLINE3.

Sources are LF-only with no trailing whitespace, matching what Wikidot stores
on save; a trailing sentinel paragraph is used where an empty shape would
otherwise be trimmed.  Each case is a full document, not a fragment.  The
shape mirrors the Strong rule's battery (R2-INLINE2) with ^^ in place of **,
plus Superscript-specific corpus pins from the read-only ftml checkout.
"""
import json

cases = [
    # basic pairs
    ("sup01", "^^sup^^"),
    ("sup02", "before ^^sup^^ after"),
    ("sup03", "^^one^^ ^^two^^"),
    ("sup04", "^^a^^b^^c^^"),
    ("sup05", "wor^^d^^in"),
    ("sup06", "^^two words^^"),
    # padding and word boundaries
    ("sup07", "^^ sup ^^"),
    ("sup08", "^^sup ^^"),
    ("sup09", "^^ sup^^"),
    ("sup10", "^^a b^^"),
    ("sup11", "^^ a^^b^^ ^^"),
    ("sup12", "^^a^^ ^^ b ^^ ^^c^^"),
    # unpaired, tripled, empty
    ("sup13", "^^unpaired"),
    ("sup14", "unpaired^^"),
    ("sup15", "^^^triple^^^"),
    ("sup16", "^^a^^^"),
    ("sup17", "^^^a^^"),
    ("sup18", "^^^^"),
    ("sup19", "^^ ^^"),
    ("sup20", "^^a^^^^b^^"),
    # nesting with sibling markers
    ("sup21", "^^//em//^^"),
    ("sup22", "//^^sup^^//"),
    ("sup23", "^^__u__^^"),
    ("sup24", "^^--s--^^"),
    ("sup25", "##c00|^^red^^##"),
    ("sup26", "^^##c00|red##^^"),
    ("sup27", "^^{{mono}}^^"),
    ("sup28", "{{^^mono^^}}"),
    ("sup29", "^^,,sub,,^^"),
    ("sup30", ",,OUTER ^^INNER,, TAIL^^"),
    # line breaks and block boundaries
    ("sup31", "^^a\nb^^\nx"),
    ("sup32", "^^a\n\nb^^\nx"),
    ("sup33", "^^a\n----\nb^^\nx"),
    ("sup34", "^^a\n[!-- c --]\nb^^\nx"),
    ("sup35", "^^a\nb^^\n\nx"),
    ("sup36", "^^a\n> quote\nb^^\nx"),
    ("sup37", "^^[[div]]inside[[/div]]^^\nx"),
    ("sup38", "^^a\n* list\nb^^\nx"),
    # table cells
    ("sup39", "|| ^^A^^ || B ||\nx"),
    ("sup40", "|| ^^A || B^^ || C ||\nx"),
    ("sup41", "||a||^^b^^||c||\nx"),
    ("sup42", "|| ^^ A ^^ ||\nx"),
    ("sup43", "|||| ^^span^^ |||| x ||\nx"),
    # headings and link labels
    ("sup44", "= ^^Head^^ =\nx"),
    ("sup45", "^^= Head =^^\nx"),
    ("sup46", "[[^^label^^|target]]"),
    ("sup47", "[[target|^^label^^]]"),
    ("sup48", "[[^^page^^]]"),
    # code and raw shields
    ("sup49", "[code]^^sup^^[/code]"),
    ("sup50", "{{^^mono^^}}"),
    ("sup51", "[[raw]]^^x^^[[/raw]]"),
    ("sup52", "`^^code^^`"),
    ("sup53", "[code]\n^^sup^^\n[/code]"),
    ("sup54", "^^a[code]x[/code]b^^"),
    ("sup55", "[[code]]^^sup^^[[/code]]"),
    ("sup56", "^^a\n[[div]]\nb\n[[/div]]\nc^^\nx"),
    # real Wikidot triple-bracket link labels and anchor-block bodies
    ("sup57", "[[[^^caption^^|target]]]\nx"),
    ("sup58", "[[[target|^^caption^^]]]\nx"),
    ("sup59", "[[a href=\"https://example.com\"]]^^label^^[[/a]]\nx"),
    ("sup60", "[[[^^page^^]]]\nx"),
    # Superscript-specific corpus pins from the read-only ftml checkout
    ("sup61", "^^A ^^B^^ C^^\nx"),
    ("sup62", "^[!--x--]^A^^\nx"),
    ("sup63", "^^OUTER {{INNER^^ TAIL}}\nx"),
    ("sup64", "^^A {{B --C^^ X}} Y--\nx"),
    ("sup65", "//A ^^B __C// X^^ Y__\nx"),
    ("sup66", "[[sup]]X[[/sup]]\nx"),
]

if __name__ == "__main__":
    with open("battery.jsonl", "w") as f:
        for cid, src in cases:
            f.write(json.dumps({"id": cid, "source": src}, ensure_ascii=False) + "\n")
    print(f"wrote {len(cases)} cases")
