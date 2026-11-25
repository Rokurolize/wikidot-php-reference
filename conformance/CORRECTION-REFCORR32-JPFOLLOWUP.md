# REFCORR32 — JP census follow-up residuals

Date: 2026-11-26. Scope: four independent reference defects isolated while adjudicating the JP residual census. Cross-rule inline-scope/collapsible/table ownership cases are not patched here.

## C1 — Button accepted-name matrix completion

Evidence: JP corpus `wiki-syntax:buttons` renders `[[button site-tools]]` and `[[button lock-page]]` as links where the reference emitted invalid-type blocks, but the XML-RPC cache strips onclick/localizes labels. New valid/stable/source-matched probes `muse-probe-jpfollow-r32-buttons` settle exact sandbox rendering: `site-tools` -> `WIKIDOT.page.listeners.siteTools(event)`, default `site tools`; `lock-page` -> `WIKIDOT.page.listeners.blockClick(event)`, default `lock page`; underscore forms normalize to the same accepted names; `lock` and `sitetools` remain invalid. Correction: add the two names to the allowed, default-text, and onclick tables.

Complete accepted matrix after correction: `edit`, `edit-append`, `edit-sections`, `history`, `print`, `files`, `tags`, `source`, `talk`, `backlinks`, `rename`, `delete`, `parent`, `edit-meta`, `watchers`, `site-tools`, `lock-page`, `set-tags` (the last requiring text). Underscores are accepted only through the existing normalization to hyphens.

## C2 — Size edge whitespace belongs outside the inline scope

Evidence: JP corpus `not-fade-away` and valid/stable/source-matched probe `muse-probe-jpfollow-r32-whitespace` show `A[[size 60%]] x [[/size]]B` -> `A <span ...>x</span> B`: leading horizontal whitespace is hoisted before the span and trailing horizontal whitespace is ejected after it. At a paragraph edge the ejected whitespace is then trimmed by the settled final whitespace pass, preserving the older whitespace-only/end-of-paragraph probes. Correction: capture only ASCII horizontal whitespace at the absolute Size body edges, keep it outside the token pair, and retain the internal line-end stripping behavior.

## C3 — Terminal explicit-break framing remains routed cross-rule scope

JP corpus `macro-7happy7-proposal` and probe `muse-probe-jpfollow-r32-whitespace` initially suggested a terminal-padding defect, but the frozen EN gates proved that the same padding byte is load-bearing in other block-boundary shapes. This is therefore not an independent Newline defect; it is routed to the cross-rule block/paragraph framing seam and REFCORR32 intentionally makes no Break/Newline change.

## C4 — Span trailing space before the final newline must not eat the newline

Evidence: JP corpus `sleep-beneath-the-stars` has `TEXT \n[[/span]]` with one space before the final LF. Live drops the horizontal edge whitespace but preserves the LF as `<br />` inside the span. The reference's unanchored `$` edge-space match removed one byte from the body end, consuming the LF rather than the space. Correction: anchor same-line trailing-space extraction at absolute end (`\z`); space before a final newline remains subject to the settled newline-adjacent trimming while the newline survives. A same-line trailing-space hoisting negative control is pinned.

## C5 — Categorized absolute Freelink targets canonicalize page-slug case

Evidence: JP corpus `old:decomm:scp-723-d` renders `[[[/decomm:723-D-1-testing-log |...]]]` with lowercase `/decomm:723-d-1-testing-log`; the reference bypassed slug canonicalization for every leading-slash path. JP corpus `the-time-after-time-password-hub` preserves bare `/Under`, so the correction is deliberately limited to colon-bearing categorized targets and does not lowercase all absolute paths.

## Pins

`conformance/refcorr32/` contains eleven cases: positive matrices/witnesses for C1-C4 plus the Freelink witness and negative controls against overreach. Run `python3 conformance/refcorr32/verify_refcorr32.py`.
