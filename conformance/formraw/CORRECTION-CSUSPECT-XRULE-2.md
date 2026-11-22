# CORRECTION C-SUSPECT-XRULE-2 — Form body lines drop earlier-rule placeholders (REFCORR4 lane, 2026-11-22)

Status: APPLIED in this tree. The decisive probe muse-probe-suspect-xrule-x18-form-code (`[[form]]` around a code block) serves a fourth `<br />` on live where the uncorrected reference leaked a delimiter-wrapped Code token index inside a pre-wrap span; the capture is valid, stable and saved-source-matching in conformance-suspect-xrule/captures-b12.json. The Form/Raw controls -x37-form-raw-body and -x38-form-code-midline were already byte-identical, because Form runs before Raw and inline Raw markup never becomes a placeholder before Form's process().

## The correction (reference)

Parse/Default/Form.php process() strips every delimiter-wrapped decimal placeholder from each body line before storing it, so an emptied line takes the existing blank-token branch and keeps the surrounding newline structure. Byte-identical predecessor ref-php/text-wiki/Text/Wiki/Parse/Default/Form.php.before-refcorr4 (SHA-256 8e2741f2d03d2cbdd9527aea72ca5aeebf02489f3832f66641ad7796b292f98c); corrected SHA-256 cde34fee2c6c4d7543e6013e27b32879f36716b91ac399a0db42a4050e6246bb.

## Firsthand verification

The decisive probe matches live byte-for-byte; the 68-case Form/Raw battery is byte-identical before and after (SHA-256 e306a90ca4cd6c9eab1adb4ee6199c1f8a1d507c76b62681693bdc91916ef753 on both sides, empty stderr), and the smoke battery is 9/9.

## Mirror consequence

lean-ftml/LeanFtml/FormRawRules.lean gains stripFormPlaceholders and formProcess applies it before the blank/text decision.
