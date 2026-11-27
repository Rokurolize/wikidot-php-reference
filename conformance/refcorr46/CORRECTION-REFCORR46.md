# CORRECTION-REFCORR46 — html-block opener line ownership

REFCORR46 is the conformance record for the hunt-html sweep. It uses byte-verified sandbox evidence on `sandbox-for-codex`; probe pages are immutable evidence and remain in place. No production page was accessed. The lane used 4 probe-page cycles: three grouped ten-shape recognition matrices and one grouped eight-cell closer-boundary discriminator.

## Measured rule

Live recognizes `[[html` only when the opener is the first byte of a source line. The rest of the line does not have to be empty: a same-line body, trailing text after a valid close, opener attributes, uppercase tag spelling, and horizontal trailing whitespace all still form the iframe. Text before the opener, even ordinary indentation, makes the tokens literal. Structural line ownership has the same negative result in centered, heading, quote, list, advanced-simple-table-cell, and multiline-blockquote positions. A bare opener line inside a `[[div]]` block remains positive because the opener really is at that content line's first byte.

Once a valid opener has been recognized, the block closes at the first `[[/html]]` followed by whitespace or end of input. The closer does not itself have to be line-led. A closer with adjacent non-whitespace trailing text is not a closer: scanning continues through later source until a valid closer, which is why the grouped boundary page swallows the intermediate labels and shapes before surfacing at the next valid boundary. This closer behavior was already present in the reference regex and is pinned rather than changed.

A recognized line-level html block also owns a leading line boundary. When ordinary text occupies the preceding line, live closes that text paragraph before the iframe rather than serving `x<br /><iframe>` in one paragraph. A following line can still be a soft line after the iframe, and a document-initial or blank-line-separated block keeps the same outer paragraph shape.

## Correction

The correction is confined to `text-wiki/Text/Wiki/Parse/Default/Html.php`, the owning recognition stage. The recognizer's `m`-mode regex is again anchored with `^`, so the opener must start a line. This restores the line anchor that the fossil `<html>` rule already had before REFCORR19 widened the `[[html]]` form. The token replacement now begins with one newline, making the recognized block own its leading line boundary in the same way the live paragraph surface does; at document start or after an existing blank line the extra line boundary is invisible, while after ordinary text it creates the measured paragraph separation.

No render-rule change is made. The fixed harness still uses the stand-in html-block endpoint; the live-canonical comparison masks only that serving endpoint/hash and the established per-render environment noise.

## Pins

`cases.jsonl`, `expected.json`, `captures.json`, and `verify_refcorr46.py` pin four grouped live-probe documents covering 38 shape cells: 30 recognition cells (15 positive and 15 negative) and 8 closer-boundary discriminator cells. At the pre-commit local run all 4/4 expected-render byte pins, 4/4 live-canonical fidelity pins, and 4/4 capture-validity checks passed.

The four probe pages are `muse-probe-hunt-html-line-positions`, `muse-probe-hunt-html-structural-lines`, `muse-probe-hunt-html-line-composition`, and `muse-probe-hunt-html-closer-boundary`. Every capture is stable across two anonymous rendered GETs and its saved source is byte-identical to the intended grouped source. Wikidot normalized a raw tab in the first attempted line-positions page to four spaces and stripped the terminal newline; the probe source was canonicalized to that storable byte form before the accepted capture, so the indentation evidence is the byte-verified four-space form.
