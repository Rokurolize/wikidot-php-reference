# CORRECTION-REFCORR57: bare-inline block-boundary bytes and empty definition-list shells

## Adjudication

The snapshot-80 re-derivation of all 63 CN register cases started at 31 environment-aware matches and 32 survivors. Fresh grouped sandbox probes separated the surviving family into parser corrections, provenance residues, and remainders:

- Bare inline text left after an empty alignment/div shell or a block close is followed by a newline byte before the next paragraph or block opener in live output. This is a serialization/frame byte owned by the block boundary, not authored horizontal whitespace. The reference emitted the next `<p>`, `<div>`, or `<blockquote>` byte-adjacent to the text. The supplemental whitespace probe (`muse-probe-hunt-cn8-bare-block-whitespace-matrix`) confirmed the same newline ownership after empty/nonempty alignment closes and scored-div closes before paragraphs, quotes, and horizontal rules.
- An inline text line followed by an explicit ` _` break and then a horizontal rule is bare in live output; the rule is not inside a paragraph. The reference wrapped the whole run.
- A centered block opened inside a paragraph is repaired by live's purify pass. The reference already had the purifier but lacked this paragraph/block-crossing trigger, so a centered block directly after inline text remained malformed.
- An empty definition-list shell manufactured by quote text such as `: |` or `: )` is absent in live output. The reference emitted `<dl></dl>`.
- Fresh isolated probes contradicted the original initial-footnote register claim: a document-initial footnote is wrapped on current live Wikidot. Fresh reduced Size probes without empty-Raw layout atoms reopen across horizontal-rule and blockquote boundaries; the corpus size survivors combine that behavior with `@@`/`@@@@` layout atoms and remain open rather than being refuted wholesale. Credit-module pages remain harness/include-environment divergences, and the corrupted-angle/private-use, triple-percent capture-artifact, empty-Raw-whitespace, tab-empty-fragment, printuser-adjacent, heading/TOC-whitespace, and reverse-direction close-to-bare-inline remnants are carried rather than forced into unsupported rules.

## Mechanism and implementation

`Text_Wiki::render()` now emits the measured newline byte when a paragraph, horizontal rule, div/alignment/center, or blockquote start follows output ending in bare inline text; detects a centered div opened while a paragraph is open and routes that malformed assembly through the existing purifyHtml-equivalent pass; and removes empty `<dl>` shells. `Paragraph.php` additionally treats a text run whose line continues through an explicit Break token into a horizontal rule as a bare block-boundary run.

## Pins and pin-byte refreshes

`cases.jsonl` contains the immutable grouped sandbox matrices for the bare-inline/block-boundary shapes and container empty-framing controls. `captures.json` records their stable source-identical captures. `verify_refcorr57.py` checks expected-render bytes and live-canonical fidelity. `Wiki.php.before-refcorr57` and `Paragraph.php.before-refcorr57` are the pre-correction implementation copies.

The newline-boundary correction changes only serialization whitespace in several earlier byte pins. REFCORR29 `r29-module-quoted-closer`, REFCORR37 `PROBE-LAYOUT` and `PROBE-TABLECELL-TRAILING-SEAM`, REFCORR40 `div-attrs`, REFCORR43 `scoredcss` and `scorednested`, and the REFCORR55 explicit-list boundary matrix were refreshed to the new bytes after their live-canonical fidelity checks remained green; the fresh whitespace probe supplies the live evidence for the new byte ownership. No semantic pin expectation was loosened.
