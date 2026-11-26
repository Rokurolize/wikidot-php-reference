# REFCORR31 — CN census residual correction

Date: 2026-11-26. Scope: one independent reference defect isolated while adjudicating the snapshot-55 Chinese-corpus residual census and re-rendered against snapshot-56. Cross-rule paragraph/list/table/collapsible/raw-url ownership cases are not patched here. REFCORR32 overlaps were measured and not re-fixed.

## C1 — External Freelink hash suffixes receive live's second escaping pass

Evidence: four independent cached CN pages show the same surface. In `scp-3249`, the external bibliography link `[[[https://books.google.com.au/...&redir_esc=y#v=onepage&q&f=false | ...]]]` renders on live with ordinary single `&amp;` escaping before the fragment but `&amp;amp;q&amp;amp;f=false` inside the fragment. In `semimonth-202607-01` and `scpdeclassified:scp-6488-part-1`, `https://music.163.com/#/song?id=...&market=...` renders the fragment query ampersand as `&amp;amp;`. In `fragment:cn1000mrblackcat-04`, whose authored fragment already contains `&amp;`, live emits the triple-encoded `&amp;amp;amp;`. The reference escaped the reassembled external href only once.

Correction: in the external-URL branch of the Freelink renderer, escape the peeled `#fragment` or `/#/` hash-route suffix once before concatenating it with the base URL, then keep the existing whole-href escape. Plain query ampersands before the hash and local-page anchors remain single-escaped. After correction the full cached `scp-3249` page compares exactly under the lane's strict census canonicalization; the three music-link witnesses match at the link surface while their pages remain non-exact for unrelated include/harness boundaries. Regression corroboration outside CN is independent and direct: EN `scp-3249` and `scp-4035` and JP `scp-3839` are the only EN/JP byte movements, and each cached live href already carries the same extra escaping layer in the fragment or hash route.

## Rejected Url candidate

An intermediate candidate treated every U+3002 CJK full stop as a bare-autolink terminator. It was rejected before packaging: `guide-for-writing` does terminate after `https://scp-wiki-cn.wikidot.com/my-first-tale`, but its source has an immediately following empty-Raw `@@@@` boundary; conversely `embracechaos` cached live HTML deliberately carries `。` inside a compound bare-URL overclaim. That residual is therefore a Raw/Url cross-rule boundary candidate, not evidence for a Url-local correction.

## REFCORR32 overlap boundary

The snapshot-56 residual re-render showed 23 of the 2,152 exported residuals had reference-output movement from REFCORR32. Eight became byte-exact under the census canonicalization and are reported as already-fixed remainders: `ambrose-awcy-pop-up-shop`, `dread-circuses-hub`, `nexus-series`, `nobody-there-but-the-thing-in-itself`, `number-27-oneiroi-station`, `quhuierduo`, `restless-dreams`, and `sleep-beneath-the-stars`. The other 15 moved but retain cross-rule or unrelated residuals (`apres-aleph`, `gravesloop`, `gohw-chapter-5-dot-js`, `icsutformat`, `log-of-anomalous-items-cn:01591`, `non-rate:scp-cn-3348`, `scp-4239`, `scp-cn-048`, `scp-cn-2017`, `scp-cn-3750`, `scp-cn-979`, `scp-cn-4801`, `shaoxiang`, `scp3000contesthub`, and `144-hour-jam-contest`). REFCORR31 makes no Size, Span, Button, Break, categorized-Freelink, or Url change.

## Pins

`conformance/refcorr31/` contains five cases: positive witnesses for the correction plus plain-query and local-anchor negative controls. Run `python3 conformance/refcorr31/verify_refcorr31.py` (currently 5/5 exact). The pre-correction copy is `Freelink.php.before-refcorr31` in the same directory.

Pre-correction SHA-256: `23aaa508e7c9412314af415085b593f93671215156f72f8b6ff83df43ea51532`; corrected working-tree SHA-256 at validation: `32c05de874adf45eaf824e6070c2d0ef5b6052eaa8a04097dff704e8356b9d7d`.
