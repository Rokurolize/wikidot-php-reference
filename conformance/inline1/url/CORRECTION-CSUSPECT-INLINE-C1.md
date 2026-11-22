# CORRECTION C-SUSPECT-INLINE-1/2 — Url authored target on anchors and mailto (REFCORR3 lane, 2026-11-22)

Status: APPLIED in this tree. The SUSPECT-INLINE lane confirmed two reference divergences: Render/Xhtml/Url.php force-cleared an authored target on `#` and `mailto:` hrefs, dropping the target="_blank" that live keeps on starred anchor and mailto links. This tree's Url.php already carried the separate HTMLCHARS ENT_COMPAT correction, which the lane's base lacked; the two fixes touch different lines and both are present in the merged result.

## The settling evidence (fresh live probes, all valid, stable, and saved-source-matching)

Probes muse-probe-suspect-inline-url-anchor-star and -anchor-star2 ([*#sec Top]) served `<p><a href="#sec" target="_blank">Top</a></p>` where the reference served no target; -url-mailto-lower and -url-mailto-star2 ([*mailto:a@b.c Mail]) served `<p><a href="mailto:a@b.c" target="_blank">Mail</a></p>` where the reference dropped the target. The unstarred controls -url-mailto-unstar, -url-hash-star, -url-star-http and -url-hash-unstar pin that the `#` -> `javascript:;` substitution still runs before the (now removed) target test and that unstarred links carry no target on either side.

## The correction (reference)

Render/Xhtml/Url.php only: the `if ($href[0] == '#' || strtolower(substr($href,0,7)) == 'mailto:') { $target = ''; }` block is deleted and the comment updated. All four htmlspecialchars calls keep their existing `ENT_COMPAT, 'UTF-8'` arguments, so the HTMLCHARS correction is preserved and no other bytes move. The adopted lane's corrected file was NOT copied verbatim, because it lacked `, 'UTF-8'` at three calls; the merge is the lane's C1 deletion applied to this tree's HTMLCHARS-bearing file. Before-copy: ref-php/text-wiki/Text/Wiki/Render/Xhtml/Url.php.before-refcorr3 (SHA-256 8ea902c37616395102d8962e641d3ddc122966a89268c1cc8e805aa3c112e0bc); corrected SHA-256 0d8cd0553c7f1981....

## Firsthand verification (REFCORR3 lane, 2026-11-22)

The corrected reference emits target="_blank" on the four starred probe shapes and leaves the unstarred controls unchanged. The inline1/url battery is re-run (75/75 as recorded at adoption; the retained dumper comparison stands at its recorded byte-identical/frame-normalized counts) and the 9-case smoke battery stays 9/9. Gate tallies are in REPORT-REFCORR3.md.

## Mirror consequence

lean-ftml/LeanFtml/InlineSimpleRules.lean's renderUrl drops the suppressed-target branch and uses the authored target directly; in LeanFtml/InlineRender.lean the three suppression theorems are restated as target-kept theorems and the hsupp proof scaffolding is removed from the eleven other Url theorems. The r43 gates are re-run; see REPORT-REFCORR3.md.
