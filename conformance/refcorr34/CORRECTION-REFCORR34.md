# REFCORR34: stage-specific ownership of Span/Size edge whitespace

## Mechanism

REFCORR32 correctly established that horizontal whitespace at the edge of a
`[[span]]` or `[[size]]` body is not rendered inside that inline element: live
hoists a leading edge space before the element and ejects a trailing edge space
after it, with paragraph-edge cleanup dropping the space when appropriate.
Implementing that move entirely inside the Span/Size parse rules nevertheless
created a cross-rule falsehood, because those rules run before List, Newline,
Paragraph and the late paired-marker inline rules.

The correction is stage-specific ownership of the same bytes:

1. Span/Size keep the REFCORR32 outward placement while the block-layout rules
   run, and now record the exact moved bytes in token metadata (`edge_lead` or
   `edge_trail`). This preserves block and wrapper framing such as the
   `nexus-series` size/collapsible construction.
2. Colortext is the first rule in the late inline segment. Before applying its
   own regex it re-internalizes only the recorded edge bytes: leading edge
   whitespace moves back after the Span/Size start token and trailing edge
   whitespace moves back before the end token. The late paired-marker grammar
   therefore sees the inline-scope edges live gives it.
3. Tighten, still the final parse rule, moves edge spaces outward through
   Span/Size, Colortext and the paired inline markers, repeating the local move
   so whitespace exposed inside nested inline scopes propagates outward. The
   established paragraph/newline edge trims then apply. A trailing space at a
   list-item end is trimmed as the same block-edge behavior, evidenced by the
   JP corpus witness below. Span's previously settled bare-list-marker trailing
   exception is preserved with token metadata.

This explains both apparent exceptions that defeated simpler corrections:

- In `**[[span ...]] text[[/span]]**` the edge space must not sit between the
  `**` opener and the Span token when Strong pairs, even though it must render
  outside the span/strong at a paragraph edge.
- In list lines such as `[[size 0%]]__ [[/size]]`, the trailing edge space must
  remain inside the Size scope for underline pairing. Otherwise the two
  underscores in separate list items can be misread as one cross-item `__`
  pair. The same space must not survive as literal bytes before `</li>`.

## Evidence

Corpus evidence, rendered on the ref-crossrule snapshot-56 working tree:

- KO `seacicada` previously diverged at canonical byte 49 because reference
  left `**` literal around explicit color spans. After the correction the whole
  page content agrees; the first remaining difference is only the KO serving
  tail (`clear:both` plus `ko-footer`) that the offline reference harness does
  not emit.
- JP `gohw-chapter-5-dot-js` moves from a canonical mismatch at byte 291 to
  canonical equality. Live serves 29 `<span style="font-size:0%;">__</span>`
  list-item fragments; the reference now preserves the same underscores instead
  of pairing them across list items.
- JP `nexus-series`, which was canonical-equal before the correction, remains
  canonical-equal. This is the negative control against simply deferring all
  edge whitespace handling to Tighten: that broader experiment incorrectly
  emitted `<span style="font-size:larger;"><br /><br /></span>` around the
  collapsible construction.

The exact regression pins in `verify_refcorr34.py` cover leading and trailing
strong/span shapes, the cross-item Size/underline shape, and the existing
mid-text Size edge-space placement.

## Rejected alternatives

- Running the libtidy recovery pass unconditionally repaired some inline shapes
  but rewired established byte surfaces (button attribute spacing, block and
  table pretty-printing, paragraph framing) and failed existing exact pins. It
  is not a viable representation of live at the reference's byte level.
- Deferring all Span/Size edge-space movement until Tighten fixed the two
  positive witnesses but regressed `nexus-series`, showing that block-layout
  rules genuinely need the outward placement before the late inline segment.

## Verification on this branch

- REFCORR34: 4/4 exact
- REFCORR32: 11/11 exact
- REFCORR30: 11/11 exact
- REFCORR29: 12/12 exact
- REFCORR28: 5/5 exact
- REFCORR27: 5/5 exact
- REFCORR-next Form/Raw: angle-raw entities 19/19, freelink apostrophe slug 8/8
- REFCORR24 Tableadv: expected-render byte pins 45/45, live canonical fidelity 45/45
- REFCORR-next framing: expected-render byte pins 8/8, render framing 8/8, live framing 5/5
- frozen gates on the crossrule tree: `S_local_71` 71/71,
  `S_diag_44` 44/44, `S_holdout_step4_150` 150/150,
  `S_holdout_fresh_150` 150/150
