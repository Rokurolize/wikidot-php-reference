# CORRECTION AGY-INTERWIKI-FALLBACK — unknown-site fallback escaped with ENT_COMPAT (REFCORR4 lane, 2026-11-22)

Status: APPLIED in this tree. The Antigravity adjudication in GAP-LEDGER.md records that live escapes the unknown-site fallback text with ENT_COMPAT while the reference returned it raw, the X44 residue left after described-label claiming was settled. Valid, stable, saved-source-matching probes muse-probe-agy-suspect-p16-interwiki-unknown-html and -f10-interwiki-unknown-apos show `&lt;i&gt;hi&lt;/i&gt;` and `O'Brien &amp; &lt;b&gt;x&lt;/b&gt;` on live.

## The correction (reference)

Render/Xhtml/Interwiki.php's fallback arm now returns htmlspecialchars($text, ENT_COMPAT, 'UTF-8'), the same idiom the known-site branch already uses for its label and target. Predecessor Render/Xhtml/Interwiki.php.before-refcorr4 (SHA-256 71a5b85f1f10588cff639399d01c84d1a5d0d752fa2dd1a76b75d39b7af42e9f); corrected SHA-256 cd94ff117b3ffb83d767c1b185bf04e4da5712096a1b0e012ce273896f4b8c7e.

## Firsthand verification

Both probes are now byte-identical to their live captures; the r43 and r46 regenerated corpora show no movement outside the one Div case named above, and the smoke battery stays 9/9.

## Mirror consequence

lean-ftml/LeanFtml/InlineSimpleRules.lean renderInterwiki's unknown-site arm uses htmlSpecialCharsCompat, InlineRender.lean's interwiki_unknown_site_raw is restated as interwiki_unknown_site_escaped, SuspectSpec.lean's divergence theorem becomes a conformance theorem, and Main.lean's audit name is updated.
