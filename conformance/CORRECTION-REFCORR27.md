# CORRECTION-REFCORR27 — census residual parser corrections

Round: REFCORR27. Source lane: `ref-census` full-corpus census at snapshot-51.
Pins: `conformance/refcorr27/` (`cases.jsonl`, `expected.json`). All five pin
cases render as pinned on the corrected tree; the two control cases preserve
the settled non-empty-fragment and leading-space behaviors.

## C1 — Comment placeholders are invisible to the advanced-table grammar

Live evidence: cached corpus page `note-immortality-amulet`. Its outer advanced
table contains an indented whole-line comment (`[!--add image 1 --]`) between
rows. Live parses the complete nested table structure. Snapshot-51 left the
outer `[[table]]`, `[[row]]`, and `[[cell]]` markup literal.

Mechanism: `text-wiki/Text/Wiki/Parse/Default/Comment.php` intentionally leaves
an opaque empty `Comment` token for a comment occupying its own indented line.
That is correct outside tables for paragraph framing, but
`text-wiki/Text/Wiki/Parse/Default/Tableadv.php` treated the placeholder as
non-row/non-cell text and rejected the table. Tableadv now removes only tokens
whose token type is `Comment` from the advanced-table body before applying its
row/cell grammar. Other token types are unchanged.

## C2 — Exact empty image fragment link renders as javascript:;

Live evidence: cached corpus page `scp-4893`. It repeatedly authors
`[[image ... link="#"]]`; live serves each anchor as `<a href="javascript:;">`.
Snapshot-51 emitted `<a href="#">`.

Mechanism: `text-wiki/Text/Wiki/Render/Xhtml/Image.php` had correctly learned
that non-empty fragment links such as `#x` stay bare fragments, but it applied
that rule to the exact empty fragment `#` too. The renderer now special-cases
the exact value `#` to `javascript:;` and leaves non-empty fragments unchanged
(control pin `image-link-nonempty-fragment-control`).

## C3 — Image-head line folding before source/link URLs

Live evidence: cached corpus page `scorpion-pit`. It authors an image opener
whose file URL begins on the next line and whose quoted `link` value also
breaks immediately after the opening quote:

```text
[[image 
https://scp-wiki.wikidot.com/local--files/scorpion-pit/SCP-748-5.webp link="
https://scp-wiki.wikidot.com/local--files/scorpion-pit/SCP-748-5.webp" height="700px"]]
```

Live serves the image and link normally. Snapshot-51 rejected the opener and
left it literal.

Mechanism: `text-wiki/Text/Wiki/Parse/Default/Image.php` split the head only at
a literal space and applied the settled leading-whitespace link rejection to
the newline. Line breaks at those two positions are image-head folding on
live. The parser now strips leading CR/LF from the head and from the quoted
link value before the existing guards. Leading spaces and tabs still reject
the opener exactly as the earlier C3 probe pinned (control pin
`image-link-leading-space-control`).

## Validation

Frozen gates in the lane record: `S_local_71` 71/71, `S_diag_44` 44/44,
`S_holdout_step4_150` 150/150, `S_holdout_fresh_150` 150/150. Corpus movement
details are in the lane `RESULT.md`; this file records the parser corrections
and their pins.
