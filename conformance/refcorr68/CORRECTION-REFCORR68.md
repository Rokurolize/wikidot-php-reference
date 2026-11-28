# CORRECTION-REFCORR68 — `scp-cn-1442` residual adjudication; no parser correction

REFCORR68 is the conformance record for the hunt-1442 sweep. It uses byte-verified immutable sandbox evidence on `sandbox-for-codex`; probe pages remain in place. No production page was accessed by this lane. The lane used 19 probe-page cycles: 12 first-round composition pages, 6 second-round link-environment pages, and 1 recapture of the first-round exact positive control after its internal link targets were created.

## Question

REFCORR65 left a three-placeholder residual on the cached production capture of `scp-cn-1442`: after the alignment-wrapper shell correction, the reference first leaked `271272` where the cached production HTML leaked `274275`. The REFCORR65 record bounded the residual as composition-sensitive pre-Paragraph allocation evidence requiring the full prefix/footer combination. This lane tested that composition directly.

## Result: the residual does not reproduce in current live parsing

The exact corpus source, including the initial right-aligned Rate module, collapsible containment text, corrupted center body, external empty-Raw lines, footnoteblock, and footer wikiwalk navigation, was saved byte-for-byte as `muse-p-h1442-posfull`. Fresh anonymous live output was stable and saved-source byte-identical. Its first leaked index run was `271272`, exactly the reference run, not the cached production `274275`.

The twelve-case composition matrix then varied the collapsible close, the number and position of empty Raw lines, and the footer boundary. Every variation had the same first leaked index run in reference and current sandbox live output:

| case | reference | current live |
| --- | ---: | ---: |
| `posfull` | `271272` | `271272` |
| `collclosed` | `270271` | `270271` |
| `collunclosed` | `270271` | `270271` |
| `collextra` | `271272` | `271272` |
| `raw0` | `207208` | `207208` |
| `raw1` | `209210` | `209210` |
| `raw2` | `211212` | `211212` |
| `raw16` | `239240` | `239240` |
| `raw31` | `269270` | `269270` |
| `rawbefore` | `272273` | `272273` |
| `rawafter` | `270271` | `270271` |
| `boundary` | `271272` | `271272` |

`token-summary.jsonl` records the reference token-table summaries for these cases. The exact positive control has 366 token entries with maximum key 366. `tokens-positive.json` preserves the complete post-parse source and token table. In that table the reference leak spans Paragraph end token 271 and Paragraph start token 272. The cached production leak spans positions three slots later, but no current live variation exhibits those three additional pre-leak allocations.

## Link-existence environment control

The exact source contains five internal links that exist on the production CN wiki but initially did not exist on the sandbox: `tuftos-proposal`, `scp-231`, `scp-2317`, `scp-cn-1441`, and `scp-cn-1443`. To exclude page-existence environment as the hidden composition input, the lane created five run-owned holder pages at those exact target names and then saved a fresh byte-identical positive control as `h1442-poslinks`.

With all five targets existing before the positive control was first saved, current live still leaked `271272`. The visible link markup did change to existing-page links, so the environment control was effective. As a second control, the original `muse-p-h1442-posfull` was recaptured without editing it after target creation. Its five links changed from `class="newpage"` to existing-page links, while its leak remained `271272`. Thus link existence is dynamically reflected in served markup but does not move the placeholder numbering.

## Cached-production isolation

`production-cached-evidence.json` stores the local corpus-cached production HTML and metadata for comparison; it is cache evidence already present locally, not new production access. Its first leak is `274275`.

The current sandbox `poslinks` HTML and the cached production HTML were compared under a narrow serving-layer canonicalization: remove only the anonymous Rate widget body, restore the API fragment's leading/trailing newlines, and mask six-digit leaked token-index runs. Under that canonicalization the two fragments are byte-identical. The comparison is recorded in `canonical-comparison.json` and re-checked by `verify_refcorr68.py`.

That equality is important in both directions. It means the corruption chain, block structure, Raw layout, footer composition, and purify/repair output are the same in the cached production fragment and the fresh sandbox projection. The only isolated semantic difference is the placeholder numbering exposed by the leak. Because the same exact source now renders with the reference numbering under current live behavior, the cached `274275` fragment is not current evidence of a reference parse defect.

## Adjudication

No reference correction is made. The interaction hypothesized by REFCORR65 is not determined as a current parser interaction; it is dissolved as a cached-capture/projection artifact in the sense already used by the shared live index (`capture-stale/*` rows): exact-source projection onto a fresh sandbox page renders as the reference does, not as the cached HTML does.

This record does not claim to identify Wikidot's internal cache-generation mechanism. The recapture control shows that link existence can be dynamically updated while token numbering stays fixed, but it does not prove when or how the cached production fragment's numbering was generated. The adjudication is narrower and evidence-bound: current live parsing of the byte-identical source agrees with the reference at every measured composition point, so adding three phantom tokens to the reference would regress all thirteen current-live pins without any supporting live mechanism.

## Pins and verification

`verify_refcorr68.py` performs five offline checks:

1. renders all 13 exact-source probe cases through the reference harness and checks their first leaked index runs against `expected-leaks.json` — 13/13 passed;
2. checks the recorded current-live leaks against the same reference runs — 13/13 passed;
3. re-parses all cases and checks token entry count, maximum key, and per-rule token counts against `token-summary.jsonl` — 13/13 passed;
4. checks that the post-link-creation recapture is stable, valid, source-identical, has no `newpage` links, and still leaks `271272` — passed;
5. re-runs the cached-production canonical comparison and checks cached `274275` versus fresh sandbox `271272` — passed.

## Tree verification

The final tree passed the full verifier sweep enumerated from the repository itself: 43/43 verifier scripts, including the non-`verify_*`-named verifier scripts. The four frozen gates were also run against the final tree and passed with zero diffs: `S_local_71` 71/71, `S_diag_44` 44/44, `S_holdout_step4_150` 150/150, and `S_holdout_fresh_150` 150/150. Because this record ships no parser or renderer implementation diff, there was no correction-induced corpus movement to audit.

## Sharpest remaining discriminator

If a future lane challenges the capture-stale dissolution, the sharpest discriminator is no longer another sandbox composition variation. It is a same-generation production-serving comparison under explicit authorization: compare the corpus-cached API `html` for `scp-cn-1442` with a current anonymous or API render obtained in the same serving generation, without editing the production page. A current production-serving `271272` would confirm the stale-capture account directly; a reproducible current production-serving `274275`, together with the sandbox `271272` evidence here, would reopen the question as a branch/site-generation environment boundary rather than a composition-sensitive parser rule. That production read was outside this lane's authorization and was not performed.

## Boundaries

This record changes no parser or renderer implementation. It does not model historical parser versions, Wikidot cache invalidation, branch-specific site configuration, module rendering, or production-only serving state. It does not weaken the REFCORR65 isolated alignment-wrapper shell correction. It only retires the remaining `scp-cn-1442` three-index residual as evidence for a further reference correction.
