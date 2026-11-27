# CORRECTION-REFCORR53: footnote block-start separators

## Adjudication

Fresh grouped and standalone probes superseded the frozen fixture HTML where they disagreed. The five findings adjudicated as:

| finding | adjudication | correction needed |
|---|---|---|
| f709 `footnote/closer-definition-term-line` | A definition-term closer line closes a proper definition list, but a definition term at a line position that leaves no pending terms/details leaves no empty `<dl>` shell in served HTML. The lead text keeps its trailing `<br />`; the fixture's claim that the line break disappears was refuted. | yes |
| f720 `footnote/list-item-end` | A list that starts at a later line inside footnote content is real list structure. One newline separates preceding inline text from the `<ul>`/`<ol>` start. | yes |
| f800 `footnote/code-in-footnote-suffixed-closer` | The code block is real and crosses the footnote close because there is no valid same-line `[[/code]]`. Served HTML has exactly one newline before `<div class="code">` and one newline before the literal `B[[footnote]]plain` tail. The same-line `intro [[code]]x[[/code]] tail` control remains literal. | yes |
| f841 `bibliography/footnote-first-line-literal` | First-line bibliography syntax remains one inline literal run in footnote content in both exact-byte reference output and fresh served output. The frozen fixture's segmented opener/break/item/paragraph-wrapped close is stale and is refuted as footer-content evidence. | no parse correction |
| f796 `footnote/math-line-start-literal` | First-line math syntax with an invalid adjacent `[[/math]]` close remains literal in both exact-byte reference output and fresh served output, confirming the coordinator's snapshot-73 non-reproduction. | no parse correction |

A redesigned first-line matrix put the math exact shape last. It showed that a valid newline-terminated math close inside footnote content is recognized by live Wikidot, so f796 is an invalid-close lexical case rather than a blanket rejection of math in footnotes. The local harness cannot reproduce live equation markup because the live equation/image endpoint is unavailable; those two valid-math cells are therefore evidence in the lane but are deliberately excluded from conformance pins (a cd04 analog).

## Mechanism and implementation

The shared mechanism is not a footnote parser rewrite. The parsers already recognize the relevant block constructs inside footnote items. The mismatch is recursive/container whitespace repair: Text_Wiki emits compact block HTML inside the footnote footer, while live Wikidot serves newline-separated block starts and removes impossible empty containers. The existing purifier already implements this behavior for ordinary block HTML.

`Text_Wiki::render()` therefore now tracks whether rendering is inside a `Footnoteitem` token and whether a measured block-bearing token (`List`, `Deflist`, `Blockquote`, `Heading`, `Center`, `Code`, `Bibliography`, or `Math`) occurs there. If so, the existing `purifyRecoveredHtml()` repair gate runs. The rule is recursive/container-scoped, not merely top-level-list proximity. Cases without recognized block structure—plain text, first-line literals, same-line code literals, and adjacent-close math literals—do not enter the purifier through this trigger.

## Pins

`cases.jsonl` contains 32 reduced grouped-cell or exact-byte inputs:

- all 9 closer-line matrix cells;
- all 10 body-block-start matrix cells;
- 8 non-math-valid cells from the reordered first-line matrix;
- all 5 standalone fixture projections.

`raw-byte-compare.json` records the served bytes used for exact separator-sensitive comparison. After the correction, 30/32 pins match raw served bytes exactly. The two exceptions (`exact841`, `exact796`) match canonically and have byte-level footer-content equality; their remaining bytes are the broader unpurified footnotes-frame whitespace. For `exact841` the fresh footer content additionally refutes the stale frozen fixture segmentation.

Before/after files:

- `Wiki.php.before-refcorr53` is the pre-correction implementation copy.
- `../..` is the corrected tree; `verify_refcorr53.py` renders and compares all pins.
