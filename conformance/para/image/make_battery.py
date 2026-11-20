#!/usr/bin/env python3
"""Generate the R2 Image (pipeline rule 37) battery of whole-document Wikidot-source cases.

The battery covers the whole matching space of the [[image ...]] family: the seven
accepted spellings (image, =image, <image, >image, f<image, f=image, f>image) and
uppercase near misses; the source forms (external http/https URL, current-page
attachment with an original-display extension, current-page attachment needing a
resized thumbnail, page-qualified and absolute-path attachments, data:/mailto:/dns:
sources, quoted and nonascii filenames, empty head, and comments in the filename);
the attribute grammar (class, style, width/height in px, bare and percent forms,
title, alt, size, unknown keys, single/double/unquoted quoting and key case); the
link wrapper forms (fragment, page slug, external URL, starred new-tab and the
leading-space literal cases); the caption/[[/image]] body form; malformed openers
(no name, unclosed, doubled markers, bad flags, stray space); and whole documents
that place images next to surrounding text, paragraph breaks and other block
content. Every case id is prefixed i37- to keep this owner's cases disjoint from
the Newline and Paragraph owners and root's cross-rule cases. Sources are LF-only
with trailing newlines stripped, matching Wikidot's save normalization; JSON
stores their newlines as escaped \\n. Both the shared reference harness and the
shared ftml dumper accept the JSONL protocol used here.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "battery.jsonl")

CASES = [
    # --- accepted spellings and alignment -----------------------------------
    ("i37-01-plain", "[[image photo.png]]"),
    ("i37-02-align-center", "[[=image photo.png]]"),
    ("i37-03-align-left", "[[<image photo.png]]"),
    ("i37-04-align-right", "[[>image photo.png]]"),
    ("i37-05-float-left", "[[f<image photo.png]]"),
    ("i37-06-float-center", "[[f=image photo.png]]"),
    ("i37-07-float-right", "[[f>image photo.png]]"),
    ("i37-08-uppercase-name", "[[IMAGE https://example.com/a.png]]"),
    ("i37-09-titlecase-name", "[[Image https://example.com/a.png]]"),
    ("i37-10-uppercase-align", "[[F>IMAGE https://example.com/a.png]]"),

    # --- source forms --------------------------------------------------------
    ("i37-11-external-https", "[[image https://example.com/some-image.webp]]"),
    ("i37-12-external-http-alt-suffix", "[[image https://example.com/a.png?b=c]]"),
    ("i37-13-external-fragment", "[[image https://example.com/a.png#frag]]"),
    ("i37-14-external-trailing-slash", "[[image https://example.com/]]"),
    ("i37-15-local-png", "[[image filename.png]]"),
    ("i37-16-local-jpg-nosize", "[[image landscape.jpg]]"),
    ("i37-17-local-webp-resized", "[[image picture.webp]]"),
    ("i37-18-local-noext-resized", "[[image picture]]"),
    ("i37-19-page-qualified-png", "[[image other-page/photo.png]]"),
    ("i37-20-page-qualified-jpeg", "[[image other-page/photo.jpeg]]"),
    ("i37-21-absolute-path", "[[image /my-picture.png]]"),
    ("i37-22-absolute-page-path", "[[image /some-other-page/my-picture.png]]"),
    ("i37-23-double-leading-slash", "[[image //example.com/x.png]]"),
    ("i37-24-multi-segment-path", "[[image a/b/c.png]]"),
    ("i37-25-nonascii-filename", "[[image 日本語.png]]"),
    ("i37-26-comment-in-filename", "[[image a[!--x--]b.png]]"),
    ("i37-27-comment-gap", "[[image [!--x--] a.png]]"),
    ("i37-28-quoted-url-source", "[[image \"https://example.com/a.png\"]]"),
    ("i37-29-data-source", "[[image data:image/png;base64,AAAA]]"),
    ("i37-30-mailto-source", "[[image mailto:someone@example.com]]"),

    # --- attribute grammar ---------------------------------------------------
    ("i37-31-attr-class-style-title-alt", "[[image foo.gif class=\"animated\" style=\"border: 1em solid\" data-xyz=\"bar\" alt=\"A foobar\" title=\"FOO\"]]"),
    ("i37-32-attr-width-px", "[[image https://example.com/a.png width=\"200px\"]]"),
    ("i37-33-attr-width-bare", "[[image https://example.com/a.png width=\"200\"]]"),
    ("i37-34-attr-width-percent", "[[image https://example.com/a.png width=\"50%\"]]"),
    ("i37-35-attr-width-unquoted", "[[image https://example.com/a.png width=200]]"),
    ("i37-36-attr-width-empty", "[[image https://example.com/a.png width=\"\"]]"),
    ("i37-37-attr-height", "[[image https://example.com/a.png height=\"120\" width=\"200\"]]"),
    ("i37-38-attr-size-small", "[[image photo.jpeg size=\"small\"]]"),
    ("i37-39-attr-size-bogus", "[[image photo.jpeg size=\"bogus\"]]"),
    ("i37-40-attr-size-unquoted", "[[image photo.jpeg size=small]]"),
    ("i37-41-attr-unknown-key", "[[image foo.gif v7UnknownArgument=\"x\"]]"),
    ("i37-42-attr-key-case", "[[image foo.gif CLASS=\"hi\" ALT=\"Hi there\" WIDTH=\"20\"]]"),
    ("i37-43-attr-single-quotes", "[[image foo.gif class='one' style='border:0']]"),

    # --- link wrapper forms --------------------------------------------------
    ("i37-44-link-fragment", "[[image foo.gif link=\"#gif-sucks\"]]"),
    ("i37-45-link-page", "[[image foo.gif link=\"some-page\"]]"),
    ("i37-46-link-external", "[[image foo.gif link=\"https://example.com/\"]]"),
    ("i37-47-link-leading-space-literal", "[[image foo.gif link=\" https://example.com/\"]]"),
    ("i37-48-link-star", "[[image foo.gif link=\"*https://example.com/\"]]"),
    ("i37-49-link-star-space-literal", "[[image foo.gif link=\"* https://example.com/\"]]"),
    ("i37-50-link-star-page", "[[image foo.gif link=\"*some-page\"]]"),
    ("i37-51-link-explicit-overrides", "[[image foo.png link=\"https://example.com/\"]]"),

    # --- caption / body form -------------------------------------------------
    ("i37-52-caption-body", "[[image https://example.com/a.png]]a caption[[/image]]"),
    ("i37-53-caption-with-align", "[[<image https://example.com/a.png]]caption[[/image]]"),

    # --- malformed openers ---------------------------------------------------
    ("i37-54-empty-name", "[[image]]"),
    ("i37-55-empty-head-space", "[[image ]]"),
    ("i37-56-unclosed", "[[image landscape.jpg"),
    ("i37-57-double-equals", "[[==image landscape.jpg]]"),
    ("i37-58-double-float", "[[ff<image https://example.com/a.png]]"),
    ("i37-59-star-flag", "[[*$image landscape.jpg]]"),
    ("i37-60-space-after-marker", "[[= image https://example.com/a.png]]"),

    # --- whole documents / surrounding structure ----------------------------
    ("i37-61-inline-in-text", "BASIC [[image filename.png]]"),
    ("i37-62-blank-line-after", "BASIC [[image filename.png]]\n\nLEFT"),
    ("i37-63-two-images-one-line", "[[<image a.png]] [[>image b.jpg]]"),
    ("i37-64-image-then-paragraph", "[[image a.png]]\n\nafter paragraph"),
    ("i37-65-paragraph-then-image", "before paragraph\n\n[[image a.png]]"),
    ("i37-66-source-typography", "[[image aa<<bb>>cc.png]]"),
    ("i37-67-raw-head-literal", "[[image a.png alt=\"@@a@@\"]]"),
    ("i37-68-size-lookalike-in-alt", "[[=image photo.png alt=\"a size=b\"]]"),
]


def main():
    with open(OUT, "w", encoding="utf-8") as handle:
        for cid, source in CASES:
            handle.write(json.dumps({"id": cid, "source": source}) + "\n")
    print("wrote %d cases to %s" % (len(CASES), OUT))


if __name__ == "__main__":
    main()
