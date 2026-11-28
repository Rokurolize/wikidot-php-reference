# REFCORR69 measurement closure — control bytes and separators in TT bodies and labels

REFCORR69 is a measurement closure, not an executable parser correction. No PHP source file is changed.

## Scope and instrument decision

The fresh immutable sandbox pages are `muse-probe-hunt-ctrl2-tt-escdel`, `muse-probe-hunt-ctrl2-tt-c1`, `muse-probe-hunt-ctrl2-tt-usep`, `muse-probe-hunt-ctrl2-labels-escdel`, `muse-probe-hunt-ctrl2-labels-c1`, and `muse-probe-hunt-ctrl2-labels-usep` on `sandbox-for-codex`. The brief's logical `[[tt]]...[[/tt]]` position is measured with Wikidot's established teletype source form `{{...}}`, the same form used by the REFCORR39 instrument. Label positions cover all three plausible live label carriers: described scheme links, `[[a href=...]]...[[/a]]` bodies, and `[[span class=...]]...[[/span]]` bodies.

Every page was hex/sha-verified before render comparison. Intended and saved UTF-8 source hashes match exactly for all six pages; no byte family is instrument-closed. All six pages were stable across two anonymous rendered GETs.

The C1 family is Unicode C1 control codepoints U+0080 through U+009F encoded in UTF-8, excluding U+0085 because the brief measures U+0085 in the Unicode-separator family. The probe includes detailed U+0080/U+008D/U+009F edge, interior, and run shapes plus census shapes containing the full remaining U+0080-U+009F sequence.

## Measured rule

In the probed positions, ESC U+001B, DEL U+007F, the C1 control codepoints, and the separators U+0085, U+1680, U+2028, U+2029, U+202F, and U+205F are preserved literally by live Wikidot. They are not collapsed to ASCII spaces, deleted, replaced by U+FFFD, or entity-encoded. That holds for control-only bodies/labels, interior singletons, leading and trailing edges, interior runs, doubled control-only runs, and the full C1 census sequence. Live and the snapshot-88 reference are byte-identical for every extracted cell segment and for each grouped page-content fragment after removing the reference driver's trailing newline.

Because live and the reference already agree exactly, no parser rule is inferred beyond the measured literal-preservation closure and no executable correction is warranted. These pins exist to prevent regressions in the current behavior.

## Pins

`cases.jsonl` contains the six immutable grouped page sources. `captures.json` contains the byte-verified live captures. `probe-design.json` maps all 272 labeled cells to family, position, surface, shape, markers, and authored byte hex. `expected.json` pins the current exact reference render for each grouped page. `verify_refcorr69.py` checks exact expected renders and canonical live fidelity under the established one-purify comparison discipline.
