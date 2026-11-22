# CORRECTION C-SUSPECT-SERVING-2 — Freelink star-prefixed URL (REFCORR3 lane, 2026-11-22)

Status: APPLIED in this tree. The reference's freelink_is_url tested the triple-link target with a leading `*` still attached, so a starred external URL was slugified into a local newpage link. Live treats the star as a new-tab marker and emits an external link with target="_blank". Candidate C-SUSPECT-SERVING-2 is recorded in GAP-LEDGER.md and REPORT-SUSPECT-SERVING.md; the R2 freelink SECTION.md explicitly left this shape unprobed.

## The settling evidence (fresh live probes, all valid, stable, and saved-source-matching)

Probe muse-probe-suspect-serving-free-star-url (conformance-suspect-serving/probe-cases2.jsonl, captures2.json) authored [[[*https://example.com/|Star]]] and the unlabelled form. Live served `<p><a target="_blank" href="https://example.com/">Star</a></p>` and the same with the URL as text; the reference served `<a class="newpage" href="/https:example-com">`. The control muse-probe-suspect-serving-free-plain-url (unstarred) is byte-identical on both sides, so the star is the only delta; the local-star page form is untouched by this correction.

## The correction (reference)

Parse/Default/Freelink.php: when there is no leading space and the trimmed target starts with `*`, the star is stripped before freelink_is_url runs and a `target => '_blank'` option is appended to the URL token in the starred case only, leaving the pinned plain-URL token shape unchanged. Render/Xhtml/Freelink.php: the URL branch emits ` target="_blank"` from that option, ahead of href, with ENT_COMPAT escaping; a plain URL emits no target attribute. Before-copies: ref-php/text-wiki/Text/Wiki/Parse/Default/Freelink.php.before-refcorr3 (SHA-256 787720cc0b7dbe5bd874765a62b6a6cb68c99757532caae0cf486608b3b0d9f6) and Render/Xhtml/Freelink.php.before-refcorr3 (7014e7541013ab914675513d86cf260f44db9c70e81be47cf1cf8ea6cfec6ac7); corrected hashes 2d566e273e934b10... and 671885c5efdc249a....

## Firsthand verification (REFCORR3 lane, 2026-11-22)

The corrected reference renders both starred probe sources byte-identically to the live captures and leaves the plain-URL and local-star controls unchanged. The r43 family (which has no starred-URL case) stands at its baseline; gate tallies are in REPORT-REFCORR3.md.

## Mirror consequence

lean-ftml/LeanFtml/LinkRules.lean's freelinkProcess now strips a leading star before isUrlTarget and carries target="_blank" only on the starred URL token; the local-star and plain-URL branches are byte-unchanged. The r43 gates are re-run; see REPORT-REFCORR3.md.
