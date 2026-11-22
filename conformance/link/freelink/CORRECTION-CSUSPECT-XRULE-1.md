# CORRECTION C-SUSPECT-XRULE-1 — a Raw placeholder in a Freelink target leaves the form literal (REFCORR4 lane, 2026-11-22)

Status: APPLIED in this tree by merging the sibling SUSPECT-XRULE lane's correction onto this tree's current Freelink.php, which carries REFCORR3's C-SUSPECT-SERVING-2 star-URL handling. The lane's own whole corrected file was not copied, because that would delete the later star handling. The decisive probe muse-probe-suspect-xrule-x2-freelink-raw (`A [[[@@x@@]]] B`) serves `<p>A [[[<span style="white-space: pre-wrap;">x</span>]]] B</p>` on live, where the uncorrected reference emitted `<p>A <a class="newpage" href="/0"></a> B</p>`; the capture is valid, stable and saved-source-matching in conformance-suspect-xrule/captures-b12.json.

## The correction (reference)

Parse/Default/Freelink.php process() now tests the whole match for the 0xFF delimiter and returns it unchanged before any target parsing, following the existing Image-rule guard, so the Raw token resolves in the residual source. Byte-identical predecessor ref-php/text-wiki/Text/Wiki/Parse/Default/Freelink.php.before-refcorr4 (SHA-256 2d566e273e934b105a2337f97377aaedfc438e35ac627c7f29a016043de83755) and corrected SHA-256 9bd3578790d0d5b1475150776bd383d1d2fef67e42299ab3d79e9c125edaef01. The REFCORR3 star branch remains verbatim at the URL claim.

## Firsthand verification

The decisive probe matches live byte-for-byte under the merged file after programme frame shaping; the 60-case Freelink battery renders byte-identically before and after (SHA-256 8bd5366a43547c44112b8fbc6f4b9b6d2af77b244c711f4e7126804ba44fe102 on both sides, empty stderr), and the nine-case smoke battery remains 9/9.

## Mirror consequence

lean-ftml/LeanFtml/LinkRules.lean freelinkProcess now rejects a match containing 0xFF before any other guard; the REFCORR3 star path is untouched.
