# CORRECTION C-SUSPECT-XRULE-3 — an unknown Module leaves a placeholder-bearing body and closer literal (REFCORR4 lane, 2026-11-22)

Status: APPLIED in this tree. The decisive probe muse-probe-suspect-xrule-x19-module-code serves the unknown-module error block followed by the rendered code block and a literal `[[/module]]` on live, where the uncorrected reference emitted the error block alone; controls -x34-module-unknown-body and -x35-module-unknown-nobody (ordinary and absent bodies) are byte-identical on both sides and unchanged by this correction. Captures in conformance-suspect-xrule/captures-b12.json and captures-b5.json are valid, stable and saved-source-matching.

## The correction (reference)

Parse/Default/Module.php process() still emits the error token framed by blank lines, but when the captured body contains a delimiter byte it now re-emits the untrimmed captured body and the literal closer after the token. Byte-identical predecessor ref-php/text-wiki/Text/Wiki/Parse/Default/Module.php.before-refcorr4 (SHA-256 48c55ded1cf6eb3ec8084909575e16896b0b75da283ee26b32e6b7a6d2ff68dd); corrected SHA-256 aaacb6d5a5eb89a37b192043b626b87c397bb8b9a84b2dab6dcde4399709ac71.

## Firsthand verification

The decisive probe matches live byte-for-byte and both controls stay byte-identical; the 52-case Module battery is byte-identical before and after (SHA-256 a5cfdc079c4b016af73e13d1e0b55f81bdc5e8cdbc97aaa8126c68744c12a4db on both sides, empty stderr), and the smoke battery is 9/9.

## Mirror consequence

lean-ftml/LeanFtml/ModuleRules.lean moduleTryCands now appends the untrimmed body and literal closer to the replacement when the body contains 0xFF; modulePasses then sees only residual source with no new opener.
