# CORRECTION-REFCORR54: advanced-table and simple-table cell-edge framing

## Adjudication

The 24-case snapshot-77 register re-baseline left three behavioral survivors whose target seams were reproducible in reduced grouped probes. `01`, `scp-cn-530`, and `scp-cn-685` all shared advanced-table boundary framing: inline material glued to `[[table]]` or `[[/table]]` was being folded into one paragraph, while live Wikidot treats advanced-table start and end tokens as hard paragraph boundaries. `soi-004` added two independent target seams: a simple-table cell-edge strike marker and an unscored multiline anchor after an advanced table. `cack-hub` is environment-masked once the missing CSS-module surface is neutralized and is not a REFCORR54 residual. The wanderers and mission pages were already equal under the symmetric baseline method; direct-canonicalization differences there are measurement artifacts, not parser divergence. `exact-springfestival` was already closed by REFCORR50 and remains a positive control.

Fresh sandbox probes on immutable pages supplied the measured rules:

- Advanced-table `start` and `end` tokens are hard paragraph boundaries even when visible inline bytes are glued to them on the same source line. Lead and tail fragments are wrapped in their own `<p>` elements. A newline before the table remains a line break inside the lead paragraph; inserted paragraph separation is different from break ownership.
- Visible non-ASCII bytes after an advanced-table end are tail content. Pure ASCII spacing is formatting and does not create a visible tail paragraph. A simple-table lead control remains bare, so the rule is advanced-table ownership rather than generic table ownership.
- In a simple table, a `--` marker immediately after a leading-whitespace cell edge is not eligible to close a strike scope opened in an earlier cell. It can still participate locally. An unspaced marker at the cell edge can close the earlier scope. A fullwidth space is content rather than edge whitespace and does not receive the ASCII-edge treatment.
- In an unscored multiline anchor containing a scored span, line breaks inside the anchor join into the span, while blank lines outside the anchor still own paragraph separation. After an advanced table the anchor receives normal paragraph wrapping. A scored anchor pair remains bare and is the negative control.

## Mechanism and implementation

`Text_Wiki_Parse_Paragraph::parse()` now performs two measured ownership repairs before normal paragraph parsing. First, advanced-table start/end placeholders are isolated with raw blank lines only when non-whitespace source bytes abut them on the same line. Because newline parsing has already run, these inserted raw newlines cannot become break atoms; they only make the existing paragraph regex close and reopen paragraph runs around the table token. Simple tables are untouched.

Second, scored-span tokenization now distinguishes line-break runs inside an unscored anchor from blank-line runs outside that anchor. The inside side is filtered into the joined span, while the outside side remains available for paragraph separation. This implements the measured anchor-after-table behavior without changing the scored-anchor bare-pair control.

`Text_Wiki_Parse_Strikethrough::parse()` uses the REFCORR44-style temporary vertical-tab guard for a `--` marker immediately after a simple-table `cell_start` token carrying measured leading edge whitespace. The guard makes that marker ineligible as the closing delimiter of a cross-cell first-fit pair during pairing, then removes the guard bytes before later parsing. Fullwidth whitespace is not ASCII edge whitespace and is not guarded.

## Pins

`cases.jsonl` contains 35 reduced grouped-cell or exact-byte inputs:

- exact reduced projections for `scp-cn-530` and `scp-cn-685`;
- five advanced-table lead cells (`l1` through `l5`);
- five advanced-table tail cells (`t1` through `t5`);
- seven simple-table strike-edge cells (`s1` through `s7`);
- eight anchor-after-table matrix cells (`a1` through `a8`);
- seven table-boundary matrix cells (`b1` through `b7`);
- the exact springfestival positive control.

`captures.json` records the immutable sandbox captures used by the verifier. `verify_refcorr54.py` currently passes 35/35 expected-render byte pins and 35/35 live-canonical fidelity pins.

Before/after files:

- `Paragraph.php.before-refcorr54` is the pre-correction implementation copy.
- `Strikethrough.php.before-refcorr54` is the pre-correction implementation copy.
- `../..` is the corrected tree; `verify_refcorr54.py` renders and compares all pins.
