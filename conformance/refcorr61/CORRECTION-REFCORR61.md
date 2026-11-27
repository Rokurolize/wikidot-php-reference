# CORRECTION-REFCORR61

REFCORR61 covers the two remainder families left by REFCORR41 and REFCORR42: anchor pairs crossing opaque constructs, and reverse/participant inline-inline crossings.

## Measured rules

An anchor pair crossing a `[[code]]` block does not wrap the emitted `<div class="code">` in a link. Live closes the leading anchor segment before the opaque block, places the reopened empty anchor inside the code div immediately before `<pre>`, and leaves trailing text outside the anchor. The result is independent of whether the anchor carries `style="display: contents"`.

An anchor pair crossing the direct error output of an unknown module is distributed inside that error block rather than left as an anchor outside it. Live anchors the literal module-error text up to the internal documentation link, emits an empty copy of the crossing anchor before that internal link, leaves the documentation link and the remaining error text outside the crossing anchor, and does not continue the crossing anchor into trailing text after the module.

`[[embed]]` no-match output already had the live frame under the existing purifier: the anchor covers only the inline break portions, while the embed error div and following text remain outside the anchor. Opener or closer tokens inside opaque module bodies do not pair across the opaque boundary; those shapes were closed by measurement.

Reverse inline-inline crossings, overlapping anchor/strong pairs split over list items, and malformed crossings involving single-bracket links, math-inline spans, or footnote references already match live byte-for-byte under the REFCORR42 repair. Properly nested anchor participants exposed a separate trigger gap: when a rendered single-bracket link or footnote-reference link nests inside an anchor pair, live closes the outer anchor before the inner link. The reference already reached that output whenever another malformed shape caused purification, but its crossing scan did not treat nested anchors as a purification trigger.

## Implementation

`Text_Wiki::outputHasInlineCrossing` now treats an opening `<a>` encountered while another `<a>` is open as malformed input requiring the measured purifier path. This is a trigger correction only; the existing purifier produces the live nested-anchor distribution.

Before purification, `Text_Wiki::redistributeAnchorAcrossOpaqueConstructs` applies the measured opaque-boundary frame. For code blocks it moves the reopened anchor start inside the emitted code div. For unknown-module error blocks it redistributes the crossing anchor around the error text and removes the continuation anchor from the trailing paragraph. Placeholder-rendered module output keeps the placeholder inside the leading anchor segment in this harness, but the same continuation rule removes the trailing anchor segment; a dedicated trigger is needed because that placeholder is inline text rather than a malformed HTML block crossing. The transformation is construct-level and does not key on probe labels or page names. Libtidy alone was measured not to produce live's interior distribution for these opaque blocks, so the redistribution happens before the existing single purifier pass.

## Pins

`cases.jsonl` contains the ten immutable grouped probe matrices used for this round. `captures.json` records their stable sandbox captures. `expected.json` pins the reference render bytes for the grouped matrices. `cell-expectations.json` names the live cells that are byte-exact pins and the opener/closer-inside opaque-module cells whose binding comparison is canonical because their remaining byte differences are the pre-existing module-placeholder/page-frame boundary. `verify_refcorr61.py` passes 10/10 expected-render byte pins, 52/52 exact live-cell pins, 13/13 canonical live-cell pins, and 17/17 module-placeholder-masked canonical live-cell pins in this checkout. The masked class replaces only the harness `þmodule ... þ` handoff marker with the empty body the CSS module serving layer contributes to page content; it does not otherwise alter the rendered anchor structure. `Wiki.php.before-refcorr61` is the pre-correction implementation copy.

The coordinator-requested parity-selfpair page is included as capture evidence but is outside the REFCORR61 correction scope. Its lane readout is in the lane directory as `parity-selfpair-readout.json`.
