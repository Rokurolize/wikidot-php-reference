# CORRECTION-REFCORR40 — span/div user-id ASCII whitespace isolation

## Owning stage

The owning stage is parse-time user-id isolation in the Span attribute consumer, with the same already-existing isolator corrected in Div. Span had only the REFCORR5 no-double-prefix test and copied the authored id bytes after adding `u-`; it never collapsed or edge-normalized whitespace. Div and Anchor already modeled most of the same live rule, which is why the probe matrix included them as shared-consumer controls.

## Measured live rule

Eleven byte-verified, stable sandbox probe pages (`muse-probe-hunt-spanid-*`, 96 valid labeled shapes in the pinned groups) settle the whitespace class and order:

- ASCII whitespace in an id collapses as a run to one ASCII space for the measured members `space`, `TAB`, and `LF`; the implementation conservatively retains the pre-existing CR/VT/FF membership in that byte class, with CR exact behavior unmeasured because the save path normalizes it.
- The `u-` isolation is prefix-first for leading whitespace: `id="  a"` renders `u- a`, and `id=" u-x"` renders `u- u-x` rather than being treated as an author-supplied prefix.
- Trailing ASCII whitespace is removed after the collapse; a whitespace-only id renders as `u-`.
- `id="u-a<TAB>b"` does not gain a second prefix and renders `u-a b`.
- NBSP and Unicode separators U+2000 through U+200A and U+3000 are literal identifier characters, not whitespace. They are neither collapsed nor edge-trimmed.
- Span `class`, `style`, `role`, `type`, and `data-*` already use the separate technical-value normalizer: ASCII whitespace runs collapse and both ends trim, while Unicode separators remain literal.
- Div and Anchor id controls show the same id isolation. Anchor was already correct in this checkout; Div used PCRE `\s`, which incorrectly treated Unicode separators as whitespace.
- CR/CRLF could not be measured distinctly because the sandbox save path normalized them to LF. The CR/CRLF page is an invalid normalization witness only.

## Correction

`Text_Wiki_Parse_Span` now has an `isolateId` stage and applies it before storing `args['id']`. `Text_Wiki_Parse_Div::isolateId` now uses the measured ASCII whitespace byte class rather than Unicode-aware PCRE `\s`. The regex writes VT and FF as byte escapes (`\x0B`, `\x0C`) rather than `\v`; in a byte-mode PCRE pattern, `\v` can match the UTF-8 continuation byte `0x85` and destroy U+2005, which the live probes show must survive.

No change was made to Span's technical-value normalizer, Anchor, Tableadv, size, color, or ftml. The size/color page was contextual evidence only and is not part of the pinned correction set.

## Pins and evidence

- `conformance/refcorr40/cases.jsonl`: ten valid grouped byte-verified probe sources, 96 labeled shapes.
- `conformance/refcorr40/expected.json`: exact reference-render byte pins for those groups.
- `conformance/refcorr40/captures.json`: stable live captures for the same ten valid groups.
- `conformance/refcorr40/verify_refcorr40.py`: expected-render and live-canonical verifier.
- Lane evidence: `/home/roku/.local/state/wikijump/muse-bhl/post-agy-finish/lanes/hunt-spanid/captures.json` includes the invalid CR/CRLF normalization witness.

Current verifier result: expected-render byte pins 10/10; live canonical fidelity 10/10.

FTML parity note: `/home/roku/src/Rokurolize/ftml/src/id_prefix.rs` uses Rust `char::is_whitespace` in `isolate_ids`, so FTML collapses Unicode separators. For example live/reference now render `id="a\u2003b"` as `id="u-a\u2003b"` while the FTML algorithm produces `id="u-a b"`. No ftml tree was modified.
