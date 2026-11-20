#!/usr/bin/env python3
"""Generate the R2 Interwiki (pipeline rule 43) battery of whole-document Wikidot-source cases.

The battery covers the whole matching space of the single-bracket site:page family: sites inside the R1 resetWiki table (wikipedia, wikipedia.pl, pl.wikipedia, google, dictionary) and outside it (wp, commons, nosuchwiki, banana, thesaurus, ddg, wikipedia.com), case handling in both the labeled and unlabeled forms, label forms including multiword, multiple-space, tab, empty, colon, pipe and bracket seams, path charsets from the live-visible set through percent, question mark, non-ASCII and quote near misses, empty and double-colon paths, malformed or unterminated forms, and collisions with the double-bracket freelink, triple-bracket freelink, include site-pair, star link, direct URL and slash-link forms. Every case id carries the iw43- prefix so these cases stay disjoint from the other three rule owners and root's cross-rule battery. Sources are LF-only with trailing newlines stripped, matching Wikidot's save normalization; JSON stores their newlines as escaped \\n. Both the shared reference harness and the shared ftml dumper accept the JSONL protocol used here."""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "battery.jsonl")

CASES = [
    # Sites inside the configured table, both forms
    ("iw43-01-wikipedia-labeled", "[wikipedia:Albert_Einstein Albert]"),
    ("iw43-02-wikipedia-unlabeled", "[wikipedia:Albert_Einstein]"),
    ("iw43-03-wikipedia-upper-labeled", "[WIKIPEDIA:Albert_Einstein Upper]"),
    ("iw43-04-wikipedia-upper-unlabeled", "[WIKIPEDIA:Albert_Einstein]"),
    ("iw43-05-wikipedia-mixed-labeled", "[Wikipedia:Albert_Einstein Mixed]"),
    ("iw43-06-wikipedia-pl-labeled", "[wikipedia.pl:Test Polski]"),
    ("iw43-07-wikipedia-pl-unlabeled", "[wikipedia.pl:Test]"),
    ("iw43-08-pl-wikipedia-labeled", "[pl.wikipedia:Test Pol]"),
    ("iw43-09-pl-wikipedia-unlabeled", "[pl.wikipedia:Test]"),
    ("iw43-10-google-labeled", "[google:free+wiki Google]"),
    ("iw43-11-google-unlabeled", "[google:free+wiki]"),
    ("iw43-12-dictionary-labeled", "[dictionary:wiki Dictionary]"),
    ("iw43-13-dictionary-unlabeled", "[dictionary:wiki]"),
    ("iw43-14-google-upper-labeled", "[GOOGLE:free+wiki Upper]"),
    ("iw43-15-dictionary-upper-unlabeled", "[DICTIONARY:wiki]"),

    # Sites outside the configured table
    ("iw43-16-wp-labeled", "[wp:SCP_Foundation WP]"),
    ("iw43-17-wp-unlabeled", "[wp:SCP_Foundation]"),
    ("iw43-18-commons-labeled", "[commons:File:SCP-682.jpg Commons]"),
    ("iw43-19-nosuchwiki-labeled", "[nosuchwiki:Mallard The duck]"),
    ("iw43-20-nosuchwiki-unlabeled", "[nosuchwiki:Mallard]"),
    ("iw43-21-banana-labeled", "[banana:fruit-salad Banana]"),
    ("iw43-22-thesaurus-unlabeled", "[thesaurus:oak]"),
    ("iw43-23-ddg-labeled", "[ddg:oak Duck]"),
    ("iw43-24-wikipedia-com-labeled", "[wikipedia.com:Test Near]"),
    ("iw43-25-wiki-labeled", "[wiki:Test Plain]"),

    # Case handling on dotted and mixed sites
    ("iw43-26-wikipedia-pl-upper-labeled", "[WIKIPEDIA.PL:Test UpperDot]"),
    ("iw43-27-pl-wikipedia-upper-unlabeled", "[PL.WIKIPEDIA:Test]"),
    ("iw43-28-wikipedia-pl-mixed-labeled", "[Wikipedia.pl:Test MixedDot]"),
    ("iw43-29-google-mixed-labeled", "[GoOgLe:free+wiki MixedCase]"),
    ("iw43-30-dictionary-mixed-unlabeled", "[Dictionary:wiki]"),

    # Label forms and seams
    ("iw43-31-multiword-label", "[wikipedia:Albert_Einstein The great physicist]"),
    ("iw43-32-two-spaces-label", "[wikipedia:Albert_Einstein  Two spaces]"),
    ("iw43-33-tab-label", "[wikipedia:Albert_Einstein\tTab label]"),
    ("iw43-34-empty-label-one-space", "[wikipedia:Albert_Einstein ]"),
    ("iw43-35-empty-label-two-spaces", "[wikipedia:Albert_Einstein  ]"),
    ("iw43-36-label-with-colon", "[wikipedia:Albert_Einstein See: Einstein]"),
    ("iw43-37-label-with-brackets", "[wikipedia:Albert_Einstein [x] label]"),
    ("iw43-38-label-with-pipe", "[wikipedia:Albert_Einstein a|b]"),
    ("iw43-39-label-trailing-space", "[wikipedia:Albert_Einstein Label ]"),
    ("iw43-40-label-leading-and-trailing", "[wikipedia:Albert_Einstein  Padded  ]"),

    # Path charsets
    ("iw43-41-path-colon", "[wikipedia:it:Albert_Einstein Italiano]"),
    ("iw43-42-path-plus", "[google:free+wiki]"),
    ("iw43-43-path-underscore-hyphen-dot-slash", "[wikipedia:a_b-c.d/e Pathy]"),
    ("iw43-44-path-visible-special", "[wikipedia:a#b&c(d)e+f-g.h:i;j=k~l Specials]"),
    ("iw43-45-path-percent", "[wikipedia:Albert%20Einstein Percent]"),
    ("iw43-46-path-nonascii", "[wikipedia:Älbert NonAscii]"),
    ("iw43-47-path-question", "[google:what?query Question]"),
    ("iw43-48-path-quote", "[wikipedia:it's Quote]"),
    ("iw43-49-empty-path", "[wikipedia:]"),
    ("iw43-50-double-colon-path", "[wikipedia::Page DoubleColon]"),

    # Malformed and unterminated forms
    ("iw43-51-unterminated-unlabeled", "[wikipedia:Albert_Einstein"),
    ("iw43-52-unterminated-labeled", "[wikipedia:Albert_Einstein Some label"),
    ("iw43-53-prefix-leading-digit", "[1wiki:Page label]"),
    ("iw43-54-prefix-underscore", "[_wiki:Page label]"),
    ("iw43-55-prefix-digit-unlabeled", "[1wiki:Page]"),
    ("iw43-56-space-after-open", "[ wikipedia:Page label]"),
    ("iw43-57-empty-prefix", "[:Page label]"),
    ("iw43-58-star-form", "[*wikipedia:Albert_Einstein Star]"),
    ("iw43-59-label-only-spaces", "[wikipedia:Albert_Einstein    ]"),

    # Collisions with other bracket grammars and document structure
    ("iw43-60-double-bracket", "[[wikipedia:Albert_Einstein]]"),
    ("iw43-61-include-site-pair", "[[include :wikipedia:Albert_Einstein]]"),
    ("iw43-62-triple-bracket", "[[[wikipedia:Albert_Einstein]]]"),
    ("iw43-63-in-paragraphs", "before\n\n[wikipedia:Albert_Einstein Albert]\n\nafter"),
    ("iw43-64-multiple-on-line", "[wikipedia:A First] and [google:g Second] and [nosuchwiki:N Third]"),
    ("iw43-65-inside-span", "[[span]][wikipedia:Albert_Einstein Lab][[/span]]"),
    ("iw43-66-inside-code", "[[code]][wikipedia:Albert_Einstein Lab][[/code]]"),
    ("iw43-67-data-scheme", "[data:text/plain,Hello Data]"),
    ("iw43-68-direct-url", "[https://example.com/ Control]"),
    ("iw43-69-slash-target", "[/path Relative]"),
    ("iw43-70-interwiki-in-heading", "= Heading [wikipedia:Albert_Einstein Albert]"),
]


def main():
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for cid, source in CASES:
            source = source.replace("\r\n", "\n")
            f.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
    print(f"wrote {len(CASES)} cases to {OUT}")


if __name__ == "__main__":
    main()
