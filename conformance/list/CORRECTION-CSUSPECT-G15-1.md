# CORRECTION C-SUSPECT-G15-1 — Explicit-list post-follower (REFCORR3 lane, 2026-11-22)

Status: APPLIED in this tree. After an explicit `[[ul]]`/`[[ol]]` block and a blank line, live emits the first following prose run bare after a `<br />`, while the reference's List/Paragraph driver wrapped it in `<p>`. Candidate C-SUSPECT-G15-1 is recorded in GAP-LEDGER.md and REPORT-SUSPECT-G15.md; the divergence is reference-side, not ftml's.

## The settling evidence (fresh live probes, all valid, stable, and saved-source-matching)

Twenty explicit-list probes in conformance-suspect-g15/conformance-suspect-g15/ (cases-explicit.jsonl, captures-explicit.json, ref-render-explicit.jsonl). e1 ([[ul]]/[[li]]/[[/ul]] then a blank line and ZZTAILZZ) served `</ul>\n<br />\nZZTAILZZ`; e2 (ol) the same; e4 (three newlines) the same; e5 (two paragraphs) served `</ul>\n<br />\nZZTAILZZ\n<p>MORE</p>` — only the first following run is bare; e3 (single newline) already agreed bare on both sides; e6/e7 (scored span/anchor followers) agreed modulo a frame newline; e8 (preceding paragraph) confirmed the preceding block is irrelevant. Native lists wrap on both sides. The full 20-case battery stood at 16 raw agreements, 4 differences, 19/20 after frame-gap normalization.

## The correction (reference)

Parse/Default/List.php's finalizeExplicitListBoundaries() already collapses a single following newline; the correction adds a parallel branch for a run of two or more newlines followed by a non-token, non-closer character: it consumes the whole newline run, emits explicit_br_no_nl followed by explicit_raw_nl tokens between the closer and the prose, and gives the end token a trailing newline, so Paragraph never forms a fresh plain-text match for the first run while a later run still wraps. The single-newline, scored-token, native-list and bracketed-follower paths are untouched. Before-copy: ref-php/text-wiki/Text/Wiki/Parse/Default/List.php.before-refcorr3 (SHA-256 2fd92a9d247e78ad9bc7880a09005249933b163d8bcfadb73df645bce94d346e); this file also carries C-SUSPECT-LISTTABLE-6, recorded separately under conformance-refphp/list/. Corrected SHA-256 242a0b08885344e2....

## Firsthand verification (REFCORR3 lane, 2026-11-22)

The corrected reference renders e1, e2, e4 and e5 byte-identically to the live captures, and leaves e3/e6/e7/e8 at their prior (frame-normalized) agreement. The R2 list batteries and the r43/r44/r46 gate movement are tallied in REPORT-REFCORR3.md.

## Mirror consequence

None. The G1.5-scoped Lean model lean-ftml/LeanFtml/ParagraphStack.lean explicitly defers post-list break followers (module header lines 14-17) and models only the explicit-block flag; there is no transcription of this path to correct. SpecG15.lean (a lane-only file) deliberately does not state the diverging cases. This is reported with file evidence rather than an edit.
