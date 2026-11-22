# CORRECTION AGY-DIV-ATTR — Div attribute values escaped and placeholder-bearing values cleared (REFCORR4 lane, 2026-11-22)

Status: APPLIED in this tree. The Antigravity adjudication recorded in GAP-LEDGER.md settled two live behaviors the reference's Div render lacked: attribute values are escaped with ENT_COMPAT, and a value carrying a token placeholder is cleared to empty with its key kept. The decisive captures are muse-probe-agy-suspect-f09-div-attr-escapes, -x08-div-raw-attr, -b3-div-raw-class and the p23 control, all valid, stable and saved-source-matching in conformance-agy-suspect/.

## The correction (reference)

Render/Xhtml/Div.php's start-token attribute loop now clears a value containing the 0xFF delimiter before escaping it, clears the bare `u-` shell that Parse/Default/Div.php's isolateId leaves when a whole id value was a placeholder, and emits every value through htmlspecialchars($value, ENT_COMPAT, 'UTF-8') in the Span house style. The vanished-pair guard and the stored attribute order are untouched. Predecessor Render/Xhtml/Div.php.before-refcorr4 (SHA-256 d58c73ee8328e0c3d77df5c660491e07da5f350cc5847b79988a87b3c006e3e4, the REFCORR2 C-STAGE2-2-corrected file); corrected SHA-256 35c175ccf338edd85f72f187bed37cbbf49d0cc904b4d202962bbf2a6702b309.

## Firsthand verification

f09 now renders `<div data-x="a&amp;b&lt;c&gt;d'e&quot;f">`, x08 `<div data-x="">` and b3 `<div id="" class="">` with every attribute key kept and the id's u- prefix gone; only the documented Stage 2 newline insertion after the opening tag remains at frame level. The p23 apostrophe/quote control renders `a&quot;b` exactly as live. Regenerating the r43 PHP-side artifacts moves zero cases in all six corpora; regenerating r46 moves exactly one case, div/attr-id-space, from `<div id="u-">` to `<div id="">`, which is this correction's named shape. All regenerated runs have exact case counts and empty stderr.

Coordinator steering addition: the 24 da-sib-* shapes in the Antigravity SPEC2 differential (conformance-agy-spec2/cases-ws1.jsonl and comparison-ws1.json in the sibling lane tree) were re-rendered through this tree's corrected reference and all match their expected SPEC bytes, including per-field escaping of class/style/role/type/id with the u- prefix kept, double-escaping of an authored &amp;, both scored [[div_]] shapes, per-field placeholder clearing for style/role/type/data-* (including span and date tokens and selective clearing among multiple data attributes), cleared attributes on an empty-body div, and the bare id="" result. The per-case verdicts are in conformance-refcorr4/batchC/spec2-verification.json and are summarized shape by shape in REPORT-REFCORR4.md; no further edit was required.

## Mirror consequence

lean-ftml/LeanFtml/InteractiveRules.lean renderDiv now uses a key-aware divAttrFragment that clears placeholder-bearing values and the id shell and applies htmlSpecialCharsCompat to the rest; InteractiveRender.lean's div_start_class_raw theorem is restated as div_start_class_escaped and gains div_start_placeholder_attrs_cleared, SuspectSpec.lean's two render-level divergence theorems become conformance theorems, Main.lean's audit names are updated, and the spec-incoming copy is kept in step.
