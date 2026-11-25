# CORRECTION-REFCORR29 — JP census residual parser corrections

Round: REFCORR29. Source lane: `ref-census-jp` full-corpus census at
snapshot-53. Pins: `conformance/refcorr29/`. The pin battery renders 12/12
byte-exact on the corrected tree.

The JP census used the cached XML-RPC saved-page HTML as its oracle, with the
same campaign/tidy masks as the EN census. Residual adjudication then used
run-owned saved-page probes on `sandbox-for-codex`; the probe pages are left
in place. Their raw captures are in the lane's `live-probes/captures.json`.
Every accepted probe capture is `valid=true`, `stable=true`, and
`saved_source_matches=true`.

## C1 — whitespace-only Size constructs are invisible atoms, not absent text

Live evidence: probes `muse-probe-jpcensus-wssize-single`,
`wssize-two`, `wssize-two-blank`, `wssize-empty-nospace`, and
`wssize-nonzero`; corpus witnesses include `open-open-open`,
`one-attendant-of-the-dreams`, `the-warrior-and-the-dragon`,
`kusottare-pencil`, `not-fade-away`, and `ultimate-sacrifice`.

A whitespace-only `[[size ...]] … [[/size]]` pair emits no span on live, but
the pair still exists as an inline atom while Newline and Paragraph run.
Consecutive size-only source lines therefore preserve consecutive `<br />`
positions and can retain a trailing break before a paragraph split. The
fossil parser returned the empty string from Size, deleting the atom and
collapsing those line positions.

`Parse/Default/Size.php` now claims the invisible body with a Size token of
type `empty`. The existing renderer emits nothing for that type. A nested
body consisting only of horizontal whitespace and such empty atoms is itself
reduced to one invisible atom, avoiding regression of the settled nested
empty-pair suppression.

## C2 — scored-div blank stripping may not cross blockquote tokens

Live evidence: probe `muse-probe-jpcensus-bq-scored-div` and corpus witness
`colors` (`06907-colors`). A blank quote line inside a blockquote creates
separate quote paragraphs on live both inside and outside `[[div_]]`.

The scored-div fast path stripped blank-line runs at child-Div depth zero but
did not recognize already-tokenized Blockquote start/end tokens. It therefore
deleted the paragraph separation inside a quote contained by the scored div.
`Parse/Default/Div.php` now treats Blockquote bodies as opaque while applying
the same depth-zero stripping rule. Plain scored-div stripping outside
blockquote tokens is unchanged.

## C3 — the module body closer is line-start anchored

Live evidence: probe `muse-probe-jpcensus-module-rate-quoted-closer` and
corpus witness `oem-hub`. In the probe, a standalone right-floated Rate
module is followed by quoted example lines:

```text
> [[module CSS]]
> x
> [[/module]]
```

Live leaves all three quoted module lines literal. The fossil's unanchored
body search used the quoted `[[/module]]` as the closer for the earlier Rate
module, swallowing the intervening page text. `Parse/Default/Module.php` now
requires the optional body closer at line start. The prior R2 empty-body
correction is unchanged: an empty module body still leaves its closer literal.

## C4 — no trailing visible break after a final nested explicit list

Live evidence: corpus pages `wiki-syntax:lists` and `wiki-syntax:side`,
confirmed by fresh anonymous browser reads in the adjudication record. Live
ends an item whose final structural child is a nested explicit list as
`</ol></li>` or `</ul></li>`; it does not emit `</ol><br /></li>`.

`Parse/Default/List.php` already had this discipline for one narrow exact
newline-plus-placeholder shape. Indentation before the nested-list placeholder
or a same-line nested opener fell through to the generic trailing-newline
path, which inserted an `explicit_br_no_nl` token after restoring the nested
list. The final-nested-list branch now accepts indentation and same-line
placement. A same-line nested opener adds no break before the child; a child
on a following line keeps the existing authored pre-list break. The newline
before the parent close remains structural in both forms.

## C5 — three legacy embed allowlist entries are retired on live

Live evidence: corpus pages `video-logs`, `wiki-syntax:embedding-code`, and
`the-administrator-s-biography`, confirmed by fresh anonymous browser reads.
Current live serves the standard error block for all three shapes:

```html
<div class="error-block">Sorry, no match for the embedded content.</div>
```

The fossil deployed-pattern file still passed through:

- legacy YouTube Flash `<object>` embeds through the misleadingly named
  `googlevideo` pattern (`video-logs`);
- the Alexa graph widget (`wiki-syntax:embedding-code`);
- Google gadget `gmodules.com/ig/ifr` scripts
  (`the-administrator-s-biography`).

`wikidot-root/conf/wikiparser/embed/default.php` now retires those three
entries. Other live embed patterns and the existing script/event/src safety
arms are unchanged.

## Pins

- `conformance/refcorr29/refcorr29-cases.jsonl` — 12 minimal cases.
- `conformance/refcorr29/refcorr29-expected.json` — byte-level corrected
  reference output.
- `conformance/refcorr29/verify_refcorr29.py` — executable checker.
  Current result: **12/12 exact**.

## Validation

- REFCORR29 pins: **12/12 exact**.
- Frozen gates after the corrections: `S_local_71` **71/71**, `S_diag_44`
  **44/44**, `S_holdout_step4_150` **150/150**, `S_holdout_fresh_150`
  **150/150**, zero diffs in each set. These gates are EN regression gates;
  they are unchanged by the JP corrections.
- Full JP corpus movement and residual accounting are recorded in the lane
  `RESULT.md`; this file is the parser-correction record.

## Residuals adjudicated but not corrected here

The census adjudication separated several additional mismatch families from
these minimal parser corrections:

- category-template composition/chrome, including the five `how-to-write`
  pages — absent from the offline page-source input;
- fabricated user identities, localized footnote/bibliography/collapsible/TOC
  labels, social-module fossil wire, upload-authority/file-label comparator
  order, the XML-RPC `(%%%TRIPLE_PERCENT%%%)` placeholder, and the
  empty-canonical `_404` comparison edge — harness/comparator representation;
- malformed advanced-table head resegmentation, inline emphasis/subscript
  pairing across table/list boundaries, and some collapsible/span wrapper
  placement — cross-rule block/inline scoping surfaces already routed in the
  R2/inline conformance records, not independent minimal per-rule corrections
  in this round;
- `site-tools` and `lock-page` button types — a real residual candidate, but
  not included because the JP census evidence did not isolate the complete
  live behavior matrix needed for a minimal correction.
