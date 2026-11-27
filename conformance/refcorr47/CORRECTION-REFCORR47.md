# CORRECTION-REFCORR47 — collapsible structural-line placement

REFCORR47 is the conformance record for the hunt-collapse sweep. It uses byte-verified sandbox evidence on `sandbox-for-codex`; the four probe pages are immutable evidence and remain in place. No production page was accessed. The lane used 4 probe-page cycles: four grouped ten-shape matrices, 40 labeled cells in all.

## Measured rule

Live's structural-line behavior for a recognized collapsible is the behavior of the parsed fragment after the serving pipeline's purifyHtml repair, however malformed the intermediate nesting is.

On a heading line whose sole body is a collapsible pair, live serves an empty heading first and then a sibling collapsible repair. The fold labels and the content edge carry repeated heading elements at the same level and with the same `tocN` id. This is stable for `+` through `++++++`; an attributed pair still honors `show`, `hide`, `folded`, and `hideLocation`. With text beside the pair, the leading text forms the first heading and trailing text is outside the collapsible repair. A no-toc heading uses the same structure without the id. This shape was already produced byte-for-byte by snapshot-70 under both reference harnesses because the existing inline-crossing trigger ran the purifier.

A centered line surrenders the collapsible itself to the purifier repair. A sole pair leaves an empty `<p style="text-align: center;"></p>` shell and then a standalone collapsible; the collapsible is not centered. Leading text remains in the centered paragraph, the body remains inside `div.collapsible-block-content`, and trailing text is outside the repair. A centered multiline body is repaired in the same frame.

A quote line does not surrender its wrapper: the collapsible remains inside the blockquote, and a non-empty single-line inline body stays inside `div.collapsible-block-content` (hidden until unfolded). The empty pair has an empty content div. This confirms the parity chat's finding-868 row on this lane's own venue.

A list line keeps the collapsible container inside the list item, but the same-line inline body is repaired outside the list as a following paragraph; ordered and unordered lists agree. A collapsible as the sole body of a div content line is normal: it remains inside the div with its body in the content div. A bare pair is the normal standalone collapsible control.

When a heading-line collapsible has same-line text followed by later body lines, the first text is owned by the heading-collapsible repair rather than wrapped as a separate outside paragraph. In the measured composition cell, `line1` appears inside the repeated heading in the collapsible content while `line2` is outside it.

## Harness adjudication

There is no genuine dual-harness output difference on snapshot-70. The 40-cell matrix rendered through `harness/batch.php` and `harness/batch-census.php` is byte-identical between the two harnesses. The apparent clean single-`<h1><span>` nesting in the older dual-render pin is the pre-purification seam; the census harness's repeated-heading form is the post-purification frame and is exactly what live serves for the same-line heading forms.

## Correction

The correction has two narrow ownership changes.

First, `Text_Wiki::render()` now recognizes when a rendered collapsible is caught in a centered paragraph or list-item boundary and uses the existing tidy-backed purifier for that frame. The trigger is deliberately not every collapsible: bare, quote, div, table, size, and nested-scored-div collapsible frames keep their established reference byte frame and prior pins. The trigger is also not a harness change. Centered and list-line forms are the measured places where the intermediate fragment crosses a block boundary without crossing an inline token, so the former inline-only purifier trigger missed them.

Second, the collapsible parse rule marks the exact heading-end token caught in the first line of a collapsible whose opener directly follows the heading-start token. The paragraph rule leaves that marked crossing run unwrapped. This is the ownership difference measured in the multiline heading composition cell; ordinary headings and ordinary collapsible bodies are unaffected.

## Pins

`cases.jsonl`, `expected.json`, `captures.json`, and `verify_refcorr47.py` pin four grouped live-probe documents covering 40 independent labeled shape cells. At the pre-commit local run all 4/4 expected-render byte pins, 4/4 live-canonical fidelity pins, and 4/4 capture-validity checks passed. Because each grouped document contains a measured structural-crossing shape, the fixed render of the whole document is already in the post-purify frame; the expected-render bytes are byte-identical to the live captures for all four grouped pages. The canonical comparison still canonicalizes live and fixed captures directly, without a second tidy pass.

The four probe pages are:

- `muse-probe-hunt-collapse-heading-matrix` — heading levels `+` through `++++++`, attributes, folded state, text beside the pair, and no-toc
- `muse-probe-hunt-collapse-center-quote-matrix` — centered empty/body/attribute/multiline forms and quote empty/body/attribute/multiline forms
- `muse-probe-hunt-collapse-list-div-matrix` — bare controls, ordered and unordered list forms, and div sole-body/context forms
- `muse-probe-hunt-collapse-composition-matrix` — multiline heading/center/quote/list composition, preceding and following text, two pairs on a heading line, and hideLocation variants

Every capture is stable across two anonymous rendered GETs and its saved source is byte-identical to the intended grouped source. The anonymous GET user agent identified this lane as `wikidot-php-reference-hunt-collapse/REFCORR47`.
