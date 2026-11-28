# CORRECTION-REFCORR65: alignment-wrapper placeholder shells

## Adjudication

REFCORR65 continued the REFCORR62 `scp-cn-1442` token-count investigation with immutable per-form sandbox probes. The measurement shape is the reusable interrupted-list/private-use leak from REFCORR62. In that shape purifyHtml exposes adjacent placeholder indexes as digit runs, so the allocation order can be measured without inferring it from visible wrapper markup.

The settled live rule is narrower than a visible-rendering rule: an isolated alignment-wrapper opener or closer placeholder still participates in the Paragraph phase as a paragraph-sized allocation unit. Live allocates a paragraph start/end token pair around that isolated placeholder, but the pair is purifyHtml/framing residue rather than served `<p>` markup. This applies to unmatched openers, empty pairs, complete pairs before or after the leak, left and right forms, and center forms. A complete pair therefore consumes four extra placeholder indexes beyond its two early Divalign tokens: one invisible paragraph shell pair at the opener and one at the closer. An unmatched opener consumes one shell pair.

The sharpest pre-correction failure was the empty right pair. The reference previously allocated only the two early Divalign tokens and ended the leak at the same indexes as the no-wrapper control; live allocated two additional invisible shell pairs. After the correction all nine clean isolated probes are byte-identical to their stable live captures. The enclosing center/raw32 discriminator probes and the exact center-body probes also reproduce the measured leaked index runs.

## Implementation

`text-wiki/Text/Wiki/Parse/Default/Paragraph.php` now recognizes a paragraph run consisting exactly of one isolated Divalign placeholder. Instead of skipping it without allocation, the parser allocates a Paragraph start/end pair marked `divalign_shell` around the placeholder. `text-wiki/Text/Wiki/Render/Xhtml/Paragraph.php` renders those marked shell tokens as the empty string. The tokens therefore preserve live placeholder numbering and traversal order without emitting incorrect `<p>` elements.

The pre-correction parser and renderer copies are stored beside this record as `Paragraph.php.before-refcorr65` and `Xhtml-Paragraph.php.before-refcorr65`.

## Pins

`cases.jsonl` contains nine immutable isolated forms: the no-wrapper leak control; unmatched right and center openers; empty right, center, and left pairs; a complete right pair after the leak; a nonempty right pair before the leak; and an unmatched left opener. `captures.json` records their stable byte-verified sandbox captures. `expected.json` stores the corrected reference render bytes, which are byte-identical to those captures. `verify_refcorr65.py` checks both the stored expected bytes and exact live fidelity.

The snapshot-85 six-case register re-derivation keeps `shaoxiang` and `shijielastday` strict-equal. On `scp-cn-1442`, the first token-count provenance gap improves from reference `267268` versus live `274275` before this correction to reference `271272` versus live `274275` after it. Thus four of the seven missing placeholder indexes are accounted for by the alignment-wrapper shell rule. The remaining three-index gap is bounded but not claimed as settled here: exact-source ablations show that it requires the full prefix/footer combination, while isolated footer, repeated-center, triple-alignment, exact center-body, and prefix probes all match live. That residual is composition-sensitive pre-Paragraph allocation evidence, not a counterexample to the isolated shell rule measured by these pins.

## Boundaries

This correction only models placeholder allocation for isolated alignment-wrapper tokens. It does not change visible wrapper rendering, nested generic `[[div]]` allocation, footnote-block behavior, module rendering, or the composition-sensitive residual in `scp-cn-1442`. The round-three capture tails that included page chrome were not used as byte pins; only their clean leaked-index evidence was used during adjudication.
