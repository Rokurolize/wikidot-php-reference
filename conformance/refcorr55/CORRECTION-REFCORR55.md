# CORRECTION-REFCORR55: explicit-list boundary framing and loose inline-scope continuation

## Adjudication

The hunt-cn6 snapshot-78 register began with 11 CN corpus candidates. Five were already equal at baseline. The six survivors reduced to three measured parser seams:

- Explicit `[[ul]]`/`[[li]]` items own blank-line continuation inside the item. Live keeps the first fragment inline in the `<li>` and frames later prose fragments as paragraph elements inside the same item. A blank inside a nested block does not belong to the item itself.
- Newlines adjacent to block-only explicit list items are structural. A blockquote-only item has no padding breaks, while a div-only item keeps the measured single trailing break. Prose leading into an explicit list whose item body contains a blockquote remains bare rather than receiving a paragraph wrapper.
- An inline span/size scope left loose after a block boundary keeps blank-line breaks as inline content. The scan must cross a completed inline segment and an empty raw line to find the block boundary. When the same loose scope crosses centered block segmentation, live supplies two leading breaks in every reopened centered segment.
- A generic div directly after an explicit list keeps the intervening newline as a break; a following alignment block does not. Bare prose after an explicit list retains paragraph-separation whitespace before the next paragraph.

Rate-widget HTML and localization of generated footnote headings are environment surfaces, not parser divergence.

## Mechanism and implementation

`Newline.php` now scans backward through completed inline segments and empty raw atoms when deciding whether an open Span/Size scope is loose after a block end. It also inserts the measured two-break continuation at reopened centered alignment segments while the same inline scope remains open, and extends explicit-list/block newline ownership at item edges and list-to-alignment boundaries.

`List.php` now segments blank-line continuations inside explicit items only at explicit-item depth zero, wraps later text fragments in Paragraph tokens, normalizes block-only item trailing whitespace, marks quote-containing list leads, and preserves the measured raw newline after bare prose following an explicit list.

`Paragraph.php` recognizes the measured quote-list lead marker and suppresses the wrapper for that lead.

`Div.php` preserves the newline before a generic div directly after an explicit list as a Newline token rather than paragraph layout.

`Text_Wiki.php` applies the existing tidy-backed recovery pass when a paragraph/list structural crossing is present, matching the live purifyHtml ownership boundary.

## Pins

`cases.jsonl` contains three immutable grouped probe matrices covering 25 reduced shape cells: explicit-list exact/boundary forms, explicit-list lead-context bisects, and loose-scope trigger bisects. The grouped matrices are pinned as whole render outputs because several behaviors are context-sensitive; live fidelity is checked cellwise so the horizontal-rule probe separator does not become a false parser signal.

`captures.json` records the immutable sandbox captures. `verify_refcorr55.py` passes 3/3 expected-render byte pins and 3/3 grouped-matrix live-canonical fidelity checks (25/25 grouped cells). Before/after implementation copies are stored beside the verifier.
