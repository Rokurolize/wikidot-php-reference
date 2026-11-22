# CORRECTION C-SUSPECT-XRULE-6 — a named anchor with a placeholder-bearing name stays literal (REFCORR4 lane, 2026-11-22)

Status: APPLIED in this tree. The decisive probe muse-probe-suspect-xrule-x30-anchor-freelink-name (`[[# [[[Bar]]] ]]`) serves `[[# <a class="newpage" href="/bar">Bar</a> ]]` on live, where the uncorrected reference swallowed the Freelink into an empty JavaScript anchor; the capture is valid, stable and saved-source-matching in conformance-suspect-xrule/captures-b34.json.

## The correction (reference)

Parse/Default/Anchor.php parseNamedAnchors() leaves the whole match literal when the captured name contains the delimiter byte, so the earlier token resolves inside the brackets. Byte-identical predecessor ref-php/text-wiki/Text/Wiki/Parse/Default/Anchor.php.before-refcorr4 (SHA-256 05f27557da1f1ba328fe46bdd005ee032ba47123ba7326d6078ba9c59c9a05a0); corrected SHA-256 8f515a82966df5f87141b510405ddbcef6a2275a29997dcacbca66f611a2b5db.

## Firsthand verification

The decisive probe matches live byte-for-byte; the 60-case Anchor battery is byte-identical before and after (SHA-256 52bc65b13e929935ca1991541a423bc2d4d56424698ab198de9f249ee6d6f973 on both sides, empty stderr), and the smoke battery stays 9/9.

## Mirror consequence

lean-ftml/LeanFtml/FinalRules.lean namedAnchorProcess now declines a name containing 0xFF before the blank/valid/invalid name branches.
