# REFCORR36: break-only leads into a block after a suppressed Size pair

## Mechanism

One clause in `Paragraph::runIsEmptyLeadBlockLead()` was wrong. The rule already
bears a break-only run ahead of a skipped block opener (div, table,
collapsible, horizontal rule, module) so live's bare break layout survives, and
it already treats an empty Raw placeholder as layout. When a Size pair that
`Collapsible::process()` suppressed to transfer its font size to the fold labels
sits in that lead, the suppressed tokens remained in `runIsEmptyLeadBlockLead`'s
scan as an unrecognized non-layout token. The function returned false, the
Paragraph rule wrapped the run, and the leading break inside a collapsible body
was served as `<p><br /></p>` where live serves a bare `<br />`.

REFCORR36 treats a `Size` token whose `type` is `suppressed` as layout in that
scan, exactly like a Newline, a Break, or an empty Raw. It changes no other
rule, no token is re-typed, and the suppressed token still renders nothing. The
change is confined to `text-wiki/Text/Wiki/Parse/Default/Paragraph.php`.

## Evidence

- JP `scp-1000-jp` (cached `api-response.json`, 2026-11-02):
  live `<div class="collapsible-block-content"><br /><table class="wiki-content-table">`,
  snapshot-59 `<div class="collapsible-block-content"><p><br /></p><table ...>`.
  Source shape: `[[size smaller]][[collapsible show=...]][[/size]]` followed by a
  simple table row, inside an advanced-table cell. The minimal fragment on the
  fixed tree renders the exact live bytes, and the full 31,405-byte page is
  canonical-equal.
- Protected control: JP `nexus-series` has the opposite edge (`[[size larger]]
  [[collapsible ...]] [[/size]]` on one line, with spaces and no newline at the
  size/collapsible seam). Its size tokens are ordinary `start`/`end`, are not
  suppressed, and remain unaffected: it is canonical-equal before and after.
- Two grouped sandbox probe pages (`muse-probe-hunt-block-breakwrap`,
  `muse-probe-hunt-block-divscope`, 6 + 5 labeled shapes) established that the
  unmodified reference already agrees with live on plain blank-first-line
  collapsibles, on size-wrapped collapsibles with zero, one, two and three
  leading newlines, on explicit `content-panel` div opener/closer pairs with and
  without a TOC, on nested collapsibles, on a closed collapsible after a rule,
  and on an unclosed collapsible at EOF. Those are retained as pins, not changed.

## Not corrected here

- JP `scp-1722-jp` still differs at canonical byte 1701: live serves
  `<span style="font-size:85%;"><br /><br /></span>` before the collapsible,
  while both the reference and ftml omit it. The probe matrix shows the leading
  break survives only when a preceding inline scope and a blank-first-line
  collapsible body coexist, so a fix needs stage-specific ownership of break-only
  Size edge bytes across a block boundary. That is a different, broader seam
  than REFCORR34 already bounded; no confined change was established that keeps
  `nexus-series` canonical-equal. It is a sharpened remainder, not a silent
  omission.
- KO `scp-ko-series-2-tales-edition` and both `yorucontest2021-hub` captures are
  truncated cached sources (they end mid-sentence / mid-list item). The matched
  `[[div]]` and `[[collapsible]]` closers exist only in the full live page, so
  the reference's literal opener on the truncated input is correct. Masked-diff
  artifacts in the lane directory report exactly which user-identity spans were
  masked and where the remaining difference sits.
- JP `their-own-vestiges-jp` remains as previously refuted: the settled
  `div-scored/internal-blank-line-paragraphs` capture shows live collapsing
  blank lines in the minimal scored-div shape, which cannot explain the page's
  paragraph segmentation.

## Verification

- REFCORR36: 14/14 expected-render byte pins, 14/14 live-canonical pins.
- Frozen gates: `S_local_71` 71/71, `S_diag_44` 44/44,
  `S_holdout_step4_150` 150/150, `S_holdout_fresh_150` 150/150.
- Prior pins: REFCORR27 5/5, REFCORR28 5/5, REFCORR29 12/12, REFCORR30 11/11,
  REFCORR31 5/5, REFCORR32 11/11, REFCORR34 4/4, REFCORR35 6/6 byte and 6/6
  live, REFCORR-next Form/Raw 19/19 + 8/8, REFCORR24 45/45 byte and 45/45 live,
  REFCORR-next framing 8/8 + 8/8 + 5/5.
- Corpus movement: see `corpus-movement-{en,jp,ko,cn}.json` in the lane directory.
