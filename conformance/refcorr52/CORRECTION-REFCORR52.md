# CORRECTION-REFCORR52 — quote/div and quoted-close crossings; bare inline before valid div

REFCORR52 is the conformance record for the hunt-quotediv sweep. It uses byte-verified saved-page sandbox evidence on `sandbox-for-codex`; the probe pages are immutable evidence and remain in place. No production page was accessed. The lane used 3 probe-page cycles: three grouped matrices containing 28 labeled cells. One center-close cell was excluded before pinning because it exposes a separate paragraph-ownership residue that this correction does not settle; the final pin set therefore has 27 reduced cells.

## Measured seam

All three assigned items are symptoms of render-time surfaces that still need live's `WikiTransformation::purifyHtml` repair even after the reference's own token assembly and whitespace tightening.

The first family is quote/div crossing. When an unquoted div opener or closer is interleaved with quoted lines, live pairs the div tokens first and then repairs the resulting blockquote/div crossing. Unmarked empty crossed shells dissolve; attributed empty quote shells survive; validly nested quoted bodies remain inside the quote/div structure. The exact corpus regression `scp-cn-3636` is in this family.

The second family is the same crossing expressed through quoted centered-close syntax. A quoted `[[=]]` opener followed before its close by a quoted `[[/=]]` produces an alignment div whose close crosses an outer blockquote close. Live repairs this for center alignment and, as a control, for left alignment; the mechanism is alignment-generic rather than center-specific.

The third family is narrower and byte-framed: when bare literal inline text reaches a valid Div-rule block opener, live's purify pass owns the boundary byte and serves a newline before the `<div>`. This includes the `[[/div]] [[div]]` case left as a remainder in REFCORR51. The stray closer itself remains literal collapsed text; what changes is the boundary before the valid div block.

## Correction

The reference already had the shared tidy-backed `purifyRecoveredHtml` path used by earlier corrections. This correction extends only its detector conditions in `text-wiki/Text/Wiki.php`:

- `outputHasQuoteStructuralCrossing` recognizes rendered block-level container crossings in which a blockquote participates. It is deliberately narrower than every crossing so that the previously pinned bare-div/inline-crossing behavior is not reclassified.
- `outputHasEmptyBlockquote` recognizes an empty `<blockquote></blockquote>` shell left behind by vanished crossed content.
- during token rendering, a valid non-vanished Div start token that directly follows trailing authored literal characters and bare inline output sets `sawBareInlineBeforeDiv`, causing the same purify pass to establish the measured block boundary. Synthetic offline-include error-block Div targets are excluded because missing-include fixtures are harness environment output, not evidence that the authored page contains a valid target div at that boundary.

The helper `outputEndsWithBareInlineText` treats ASCII whitespace as ignorable for this test only; non-ASCII spacing characters remain rendered text bytes. The render loop separately tracks trailing literal source characters and resets that track at every token, so generated module or offline-include text does not masquerade as the authored inline boundary. Neither helper rewrites the source or token stream.

This is not a new general-purpose pretty-printer. The pass is still gated by shape detectors, and well-formed documents that do not contain one of those surfaces keep their established byte frame.

## Pins

`cases.jsonl`, `expected.json`, `captures.json`, and `verify_refcorr52.py` pin 27 reduced grouped-cell shapes:

- 10 quote/div cells (`qd01` through `qd10`);
- 7 center/alignment-close cells (`cd01` through `cd08`, excluding `cd04`);
- 10 valid-div boundary cells (`vb01` through `vb10`).

At the final local run all 27/27 expected-render byte pins, 27/27 live-canonical fidelity pins, and 27/27 capture-validity checks passed. Eighteen pins moved from the snapshot-75 baseline and all 18 moved pins are exact raw served bytes byte-identical to live. The other nine pins did not move and are canonical-equivalent rather than raw-byte-identical because the broad pre-existing newline frame around well-formed block markup is outside this correction's scope.

The grouped probe pages are:

- `muse-probe-hunt-quotediv-quote-div-matrix`
- `muse-probe-hunt-quotediv-center-close-matrix`
- `muse-probe-hunt-quotediv-valid-div-boundary-matrix`

Every capture is stable across two anonymous rendered GETs and its saved source is byte-identical to the intended source. `cd04-quoted-open-unquoted-close` is retained in lane evidence but excluded from the pin set because the correction does not reproduce one remaining byte structure there. Both sides agree on the repaired `<blockquote><div style="text-align: center;"></div></blockquote>` shell, but live wraps the following break-plus-text run as `<p><br />after</p>` while the reference emits bare `<br />after` after purification. That is a paragraph-ownership residue in the unquoted-close shape, not instability in the capture: the grouped capture itself is valid, stable, and saved-source-identical.

## Regression check anchors

The exact `scp-cn-3636` corpus seam was adjudicated separately. Before this correction, direct comparison diverged at the crossed `</blockquote>...<blockquote></div></blockquote>` repair region (first difference 11708). After the correction, the fixed render is byte-equal to the saved live HTML for the full page (`fixed_direct_equal=true`, first difference at end-of-output in the lane adjudication record). Under the doctrine corpus auditor the row remains conservatively `unchanged`, because the baseline is canonicalized through the established tidy pass and that pass hides this raw closing-order advance; the symmetric direct/direct measurement is `improved`.

All prior conformance pins remained green after the detector refinement, including the previously sensitive bare-div/inline-crossing and typography pins, and the frozen gates plus both 150-page holdouts passed.
