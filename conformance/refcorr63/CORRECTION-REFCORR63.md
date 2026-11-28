# CORRECTION-REFCORR63 — user-id VT/FF deletion, Unicode separators, and advanced-table attribute edges

## Owning stage

The owning stage is parse-time attribute normalization and user-id isolation. Span and Div shared the REFCORR40 id isolator but still treated VT and FF as collapsible whitespace. Anchor already stripped those bytes in its normalizer but tested the author-supplied `u-` prefix after normalization rather than on the authored value. Tableadv used the same isolator shape, yet its general value normalizer collapsed Unicode separators through a Unicode-aware `\s` class and dropped an authored non-empty technical attribute when normalization made it empty.

## Measured live rule

Eight byte-verified, stable sandbox probe groups (`muse-probe-hunt-spanid2-*`, 71 labeled shapes in the pinned groups) settle the remaining whitespace class:

- VT (`0x0B`) and FF (`0x0C`) are discarded bytes in user ids and technical attribute values. They are not collapsible whitespace, literal identifier characters, or trim-only whitespace: `a<VT>b` and `a<FF>b` serve as `ab`, runs also vanish, edge positions vanish, and a VT/FF-only id serves the bare `u-` shell. ASCII whitespace already in the value still collapses normally, so `a<SPACE><VT><FF><SPACE>b` serves as `a b`.
- The author-supplied-prefix test is on the authored id before discarded-control removal. A leading VT or FF therefore does not expose a following `u-` as an authored prefix: `<VT>u-a` serves as `u-u-a` on span, div, and tableadv. By contrast, `u-a<VT>b` starts with the authored prefix and serves as `u-ab`. Leading ASCII whitespace remains prefix-first, so `  u-x` serves as `u- u-x` on span, div, anchor, and tableadv.
- U+0085, U+1680, U+2028, U+2029, U+202F, and U+205F are literal identifier and technical-value characters. Doubled interior runs stay doubled, edge positions survive, and a separator-only id keeps the separator after the `u-` prefix. They join the REFCORR40-settled literal class containing NBSP, U+2000 through U+200A, and U+3000.
- Tableadv table, row, and cell ids follow the same user-id rule as span/div/anchor for the measured shapes. Tableadv technical attributes use the same control-byte deletion, ASCII-whitespace collapse, edge trim, and Unicode-literal rule; table, row, and cell positions agree where probed.
- An advanced-table attribute authored non-empty keeps the attribute key even when normalization leaves an empty value. This is measured for whitespace-only and control-only `class`, `data-x`, `style`, `role`, and `type` values, which serve as empty attributes, while an id in the same position serves `u-`. A literally empty authored value is still dropped by the pre-existing `value === ''` rule.
- Exact CR versus LF inside a quoted id remains instrument-closed. The grouped CR instrument was immutable once created, but its saved-source readback was not byte-identical: every CR and CRLF in span, div, anchor, tableadv, and bare text read back as LF, the saved source contains no CR byte, and the capture is invalid for byte-sensitive behavior. `conformance/refcorr63/cr-instrument.json` retains the intended source, readback, and capture. The capture is evidence of save-path destruction only, not an independent CR render rule.

## Correction

`Text_Wiki_Parse_Span::isolateId` and `Text_Wiki_Parse_Div::isolateId` now delete VT and FF before applying the measured ASCII whitespace collapse and edge rule, while retaining the authored-value `u-` prefix test. `Text_Wiki_Parse_Anchor` now performs that prefix test on the authored value rather than the normalized value, which corrects both leading-whitespace `u-` shapes and leading-control `u-` shapes without changing its existing normalizer. `Text_Wiki_Parse_Tableadv::normalizeValue` now collapses only the measured ASCII whitespace bytes instead of Unicode-aware `\s`, so the newly probed Unicode separators survive literally. `Text_Wiki_Parse_Tableadv::isolateId` detects edge whitespace after control-byte deletion rather than treating VT/FF as edge whitespace. Tableadv no longer drops an authored non-empty `class`, `id`, `role`, `style`, or `type` solely because normalization emptied it; the literally-empty authored-value drop is unchanged.

No ftml tree was touched. Span/Div technical-value normalization, Anchor href handling, Prefilter, and the table grammar were not changed. CR remains in the conservative ASCII collapse class because exact CR input cannot currently survive the measured save channel.

## Pins and evidence

- `conformance/refcorr63/cases.jsonl`: eight valid grouped byte-verified probe sources, 71 labeled shapes.
- `conformance/refcorr63/expected.json`: exact reference-render byte pins for those groups.
- `conformance/refcorr63/captures.json`: stable live captures for the same eight valid groups.
- `conformance/refcorr63/cr-instrument.json`: invalid CR/CRLF save-normalization witness with intended and saved hashes.
- `conformance/refcorr63/verify_refcorr63.py`: expected-render and live-canonical verifier.
- Lane evidence and analysis: `/home/roku/.local/state/wikijump/muse-bhl/post-agy-finish/lanes/hunt-spanid2/`.

Current verifier result: expected-render byte pins 8/8; live canonical fidelity 8/8.

FTML parity note: no ftml tree was modified. The measured result widens the Unicode-literal id/attribute class beyond the REFCORR40 set and makes VT/FF deletion explicit; any FTML implementation using Unicode `is_whitespace` for these separators or whitespace-collapsing VT/FF in ids diverges from live on the pinned shapes.
