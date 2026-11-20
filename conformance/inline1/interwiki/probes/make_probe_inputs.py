#!/usr/bin/env python3
"""Produce the R2 Interwiki live probe input set under the exclusive muse-probe-r2in1-iw- prefix.

Each probe isolates one contested interwiki shape: the two site-table entries the ftml WIKIDOT table lacks (wikipedia.pl, pl.wikipedia), case handling in both labeled and unlabeled forms, label whitespace and the URL-in-label seam root flagged, path charsets, malformed and unterminated forms, and collisions with the double-bracket freelink, include site-pair, star link and direct URL grammars. Sources are LF-only with trailing newlines stripped because Wikidot rewrites those on save. The create/capture CLI decorates these ids with the prefix and caches everything under probes/."""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe-inputs.jsonl")

CASES = [
    ("p01-wiki-labeled", "[wikipedia:Albert_Einstein Albert]"),
    ("p02-wiki-unlabeled", "[wikipedia:Albert_Einstein]"),
    ("p03-wiki-upper-labeled", "[WIKIPEDIA:Albert_Einstein Upper]"),
    ("p04-wiki-upper-unlabeled", "[WIKIPEDIA:Albert_Einstein]"),
    ("p05-wikipedia-pl-labeled", "[wikipedia.pl:Test Polski]"),
    ("p06-wikipedia-pl-unlabeled", "[wikipedia.pl:Test]"),
    ("p07-pl-wikipedia-labeled", "[pl.wikipedia:Test Pol]"),
    ("p08-pl-wikipedia-unlabeled", "[pl.wikipedia:Test]"),
    ("p09-google-unlabeled", "[google:free+wiki]"),
    ("p10-dictionary-labeled", "[dictionary:wiki Dictionary]"),
    ("p11-unknown-labeled", "[nosuchwiki:Mallard The duck]"),
    ("p12-unknown-unlabeled", "[nosuchwiki:Mallard]"),
    ("p13-wp-labeled", "[wp:SCP_Foundation WP]"),
    ("p14-commons-labeled", "[commons:File:SCP-682.jpg Commons]"),
    ("p15-two-spaces-label", "[wikipedia:Albert_Einstein  Two spaces]"),
    ("p16-tab-label", "[wikipedia:Albert_Einstein\tTab label]"),
    ("p17-empty-label-one-space", "[wikipedia:Albert_Einstein ]"),
    ("p18-empty-label-two-spaces", "[wikipedia:Albert_Einstein  ]"),
    ("p19-label-trailing-space", "[wikipedia:Albert_Einstein Label ]"),
    ("p20-label-url", "[wikipedia:X http://example.com/a]"),
    ("p21-path-colon", "[wikipedia:it:Albert_Einstein Italiano]"),
    ("p22-path-percent", "[wikipedia:Albert%20Einstein Percent]"),
    ("p23-path-nonascii", "[wikipedia:Älbert NonAscii]"),
    ("p24-double-bracket", "[[wikipedia:Albert_Einstein]]"),
    ("p25-include-site-pair", "[[include :wikipedia:Albert_Einstein]]"),
    ("p26-unterminated", "[wikipedia:Albert_Einstein"),
    ("p27-prefix-leading-digit", "[1wiki:Page label]"),
    ("p28-prefix-underscore", "[_wiki:Page label]"),
    ("p29-star-form", "[*wikipedia:Albert_Einstein Star]"),
    ("p30-direct-url", "[https://example.com/ Control]"),
    ("p31-slash-target", "[/path Relative]"),
    ("p32-multiple-on-line", "[wikipedia:A First] and [google:g Second] and [nosuchwiki:N Third]"),
    ("p33-label-with-pipe", "[wikipedia:Albert_Einstein a|b]"),
    ("p34-label-with-brackets", "[wikipedia:Albert_Einstein [x] label]"),
    ("p35-dotted-upper-labeled", "[WIKIPEDIA.PL:Test UpperDot]"),
    ("p36-google-mixed-labeled", "[GoOgLe:free+wiki MixedCase]"),
    ("p37-empty-path", "[wikipedia:]"),
    ("p38-double-colon-path", "[wikipedia::Page DoubleColon]"),
    ("p39-inside-span", "[[span]][wikipedia:Albert_Einstein Lab][[/span]]"),
    ("p40-inline-in-text", "before [wikipedia:Albert_Einstein Albert] after"),
]


def main():
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for pid, source in CASES:
            source = source.replace("\r\n", "\n")
            f.write(json.dumps({"id": pid, "source": source}, ensure_ascii=False) + "\n")
    print(f"wrote {len(CASES)} probes to {OUT}")


if __name__ == "__main__":
    main()
