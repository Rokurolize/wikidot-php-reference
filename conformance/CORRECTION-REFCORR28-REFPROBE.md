# CORRECTION REFCORR28 — ref-probe live-fidelity sweep

Status: APPLIED in this tree on branch `ref-probe/live-fidelity-sweep` against
snapshot-51 (`6b9a12d427bdc65d1d8cca7ba8722a00b67d764d`). The correction branch
and PR are named REFCORR28 in the lane record.

## Live evidence

The sweep created 32 run-owned probe pages on `sandbox-for-codex.wikidot.com`
and left them in place: 30 under `muse-probe-refprobe-r28-*` and two precision
follow-ups under `muse-probe-refprobe-r28x-*`. Every capture used the standard
double anonymous GET plus saved-source read-back path; every accepted capture is
`valid=true`, `stable=true`, and `saved_source_matches=true`. Raw HTML governed;
the campaign entity-decoding norm was not used to decide any contested bytes.
The raw captures are copied into `conformance/refcorr28/refcorr28-captures.json`.

Most of the matrix was already settled by the existing conformance pins and is
not re-prosecuted here: date (`conformance/next/date`), user
(`conformance/refval/user`), image (`conformance/para/image`), iframe
(`conformance/next/iframe`), embed (`conformance/refval/embed` plus REFCORR22),
span (`conformance/contain/span`), anchor (`conformance/anchor`), alignment
(`conformance/refval/divalign`/`center`), and line separators
(`conformance/refval/horiz`/`separator`). The fresh probes targeted only the
thin residue: format-letter and scalar date edges, `_pg` and underscore user
spellings, image attribute/source/link matrices, iframe malformed attributes
and URLs, embed scheme-bearing attributes, span/anchor malformed attribute
matrices, bracketed separator negatives, and alignment closer/open edges.

## Confirmed defects and corrections

### R28-IMG-1 — technical image attributes are trimmed at both ends

Live trims leading as well as trailing whitespace in `width`, `height`, and
`class`. The pre-correction reference right-trimmed those values and therefore
emitted `width=" 20"`, `height=" 30"`, and a leading-space class. Fresh live
bytes: `muse-probe-refprobe-r28-image-width-height` I04 and
`muse-probe-refprobe-r28x-image-attr-trim-more` T01/T03. The correction in
`Parse/Default/Image.php` full-trims every accepted technical/presentation key
except `link`; a leading-space `link` is still rejected before normalization,
exactly as the prior C3 evidence requires. `title` and `alt` remain verbatim,
confirmed by T04.

### R28-IMG-2 — spaces in image link hrefs percent-encode

Live serves `link="http://bad host/x"` as `href="http://bad%20host/x"`; the
pre-correction reference emitted the literal space. Evidence:
`muse-probe-refprobe-r28-image-links` I37. The correction in
`Render/Xhtml/Image.php` replaces ASCII spaces with `%20` before the existing
non-ASCII byte encoder and HTML escaping.

### R28-SPAN-1 — explicitly empty `data-*` span attributes survive

Live serves `[[span class="" id="" style="" role="" type="" data-x=""]]X[[/span]]`
as `<span data-x="">X</span>`: the empty scalar attributes drop, but the empty
data attribute keeps its key. The pre-correction reference dropped it unless a
raw placeholder had authored a nonempty value. Evidence:
`muse-probe-refprobe-r28-span-attrs` S02. The correction in
`Parse/Default/Span.php` retains explicitly empty lowercase `data-*` keys.

### R28-EMBED-1 — dangerous-looking non-src attribute values do not suppress embeds

Live passes generic embed iframes verbatim when `foo`, `action`, `data`,
`name`, or `href` contains a `javascript:`, `vbscript:`, or `data:` spelling
and the real `src` is benign. Evidence:
`muse-probe-refprobe-r28x-embed-non-src-schemes` N01-N05 and
`muse-probe-refprobe-r28-embed-schemes` E15. The pre-correction reference
returned the empty string for all such attributes. That suppression arm was
removed. The real `src` arm is unchanged: a `javascript:` or `vbscript:` src
still renders empty, and the negative control is pinned as
`r28-embed-src-js-control`.

## Pins

- `conformance/refcorr28/refcorr28-cases.jsonl` — five minimal regression
  cases, including the src negative control.
- `conformance/refcorr28/refcorr28-expected.json` — byte-level corrected
  reference output for those cases.
- `conformance/refcorr28/refcorr28-captures.json` — the raw valid live capture
  objects cited by the pins.
- `conformance/refcorr28/verify_refcorr28.py` — executable checker.
  Current result: **5/5 exact**.

## Validation

- REFCORR28 pins: **5/5 exact**.
- REFCORR24 pins: **45/45 exact**, live canonical fidelity **45/45**.
- REFCORR-next framing pins: **8/8 exact**, render assertions **8/8**, live
  assertions **5/5**.
- Frozen gates after the correction: `S_local_71` **71/71**, `S_diag_44`
  **44/44**, `S_holdout_step4_150` **150/150**, `S_holdout_fresh_150`
  **150/150**, zero diffs in each set.
- Full corpus before/after movement: see the lane RESULT.md and
  `lanes/ref-probe/corpus-movement.json` for the final register comparison.

## Non-defect residuals explicitly not corrected

- User ids, display names, avatar URLs, local upload hosts, and page-slug path
  segments are serving-environment data. The harness's user fallback and empty
  page name are representation boundaries, not reference defects.
- Embed error-block paragraph placement, spaces left by empty embed tokens,
  libtidy removal of the syntactically invalid `1onclick` attribute, and newline
  placement around image/alignment blocks are Stage-2/serving-frame surfaces
  already adjudicated in the refval records. They do not change the emitted
  embed/image/alignment constructs.
- `[[----]]`, `[[___]]`, and `[[____]]` are not separator rules. Their negative
  controls agree after the established frame treatment. Bare underscore runs
  exercise underline/strikethrough/typography rules, not a separator surface.
