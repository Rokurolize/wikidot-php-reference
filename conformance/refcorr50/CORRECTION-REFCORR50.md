# REFCORR50 — collapsible size ownership, direct named-anchor block leads, and advanced-table inter-row artifacts

REFCORR50 corrects three measured fossil parser families behind the CN collapsible-structure remainder. The evidence is the saved sandbox probe series `muse-probe-hunt-cn4-*` on `sandbox-for-codex.wikidot.com`, all valid, stable, and saved-source-byte-identical, plus the cached corpus witnesses `foundation-missed-connections`, `no-body-screaming`, `scp-3995`, `scp-cn-2771`, and `springfestival`. Probe pages are left in place; no production page was accessed.

## Corrected mechanisms

1. An empty collapsible written inside a same-line Size pair transfers the size to the generated fold labels without manufacturing inline body content. The reference formerly left the Size pair crossing the collapsible and reconstructed `<span style="font-size:smaller;"><br /><br /></span>` inside otherwise empty content. Live serves size-wrapped folded/unfolded labels and an empty `collapsible-block-content`, at root and inside an advanced-table cell.
2. Size transferred to collapsible labels has positional ownership. When the authored Size closer occurs at the opener before the body, the folded label and top hide label are inside the size scope but the bottom hide link is outside it; `hideLocation="bottom"` and `hideLocation="both"` therefore serve an unwrapped bottom link. If the Size scope really extends across the body, the bottom link remains wrapped. A suppressed opener-only Size end is removed before paragraph formation only at the measured blank-line boundary: the following visible body is empty at the end of the collapsible or blank-line-separated ordinary inline content. A single newline before ordinary inline or block-leading content remains a break-owning boundary, preventing a spurious empty paragraph in the blank-line case while preserving the settled table/center ownership pins from REFCORR36 and the corpus-visible leading break in single-newline bodies.
3. A named anchor target glued to a Div or Collapsible block opener is layout leading directly into that block, not a one-element paragraph. Live serves `<a name="A1"></a><div class="collapsible-block">` bare after a blank-separated preceding paragraph. Horizontal whitespace between the anchor and opener does not change this; a newline does. The same anchor before an advanced table remains wrapped, so the correction is limited to the measured container-block class.
4. An advanced table with at least one valid row remains a table when non-whitespace content occurs between rows. Live carries zero-width characters, whitespace-only Raw atoms, and even ordinary text through the table structure; the serving HTML repair then fosters that material before the table. Content before the first row still prevents recognition, trailing non-row content after the final row still prevents recognition, and non-cell text inside a row remains invalid under the settled strict row grammar. The reference preserves only the measured inter-row material inside the table token stream and invokes the existing tidy-backed purifier, rather than moving the text in source order itself.

## Probe results

`muse-probe-hunt-cn4-collapsible-size-matrix` pins ten cells. Cells S1-S3 and S5-S9 are the positive evidence: plain and size-wrapped empty collapsibles, advanced-table-cell placement, opener-only empty and nonempty bodies, `hideLocation` top/bottom/both, and initially unfolded output. Cell S4 is a simple-table negative control whose residual malformed simple-table/collapsible interaction is outside this correction; cell S10 is a whole-body positive control whose trailing empty inline fragment is a pre-existing loose-inline-scope residue outside this correction. The conformance pins use the measured independent cells rather than claiming those two unrelated residues.

`muse-probe-hunt-cn4-table-separator-matrix` is whole-page canonical-equal after the correction. It establishes the zero-width separator, whitespace-only Raw separator, ordinary-text control, blank/ASCII-whitespace controls, first-row rejection, inside-collapsible forms, and the two-zero-width-line ordering.

`muse-probe-hunt-cn4-anchor-blocklead-matrix` establishes the direct named-anchor container lead and its negative controls. B1 and B3 are canonical-equal positive pins, B4 is the div control, and B7 is the newline negative control. B5 confirms that the table case remains a wrapped anchor; B2 and B8 expose unrelated whitespace/empty-span residues and are not claimed here.

The mandated whole-document probe `muse-probe-hunt-cn4-bare-centered-collapsible` had source exactly `= [[collapsible]][[/collapsible]]` and served these bytes verbatim:

```html
<p style="text-align: center;"></p>
<div class="collapsible-block">
<div class="collapsible-block-folded"><a class="collapsible-block-link" href="javascript:;">+&nbsp;show&nbsp;block</a></div>
<div class="collapsible-block-unfolded" style="display:none">
<div class="collapsible-block-unfolded-link"><a class="collapsible-block-link" href="javascript:;">–&nbsp;hide&nbsp;block</a></div>
<div class="collapsible-block-content"></div>
</div>
</div>
```

The reference already matched that bare-document shape; it is pinned as a non-regression witness.

`muse-probe-hunt-cn4-printuser-matrix` refutes a generic parser rule for the `tanijas-atelier-ecke` user spacing seam: a normal avatar or plain printuser has no generated trailing space before `.`, `,`, a letter, or end of line, inside or outside a collapsible. The cached CN oracle is the XML-RPC HTML surface and the case is stub-mediated user runtime evidence; no user-renderer correction is made.

## Pins

`cases.jsonl`, `expected.json`, `captures.json`, and `verify_refcorr50.py` pin 20 reduced grouped-cell shapes: eight collapsible/size cells, seven advanced-table artifact cells, four named-anchor cells, and the mandated bare centered document. Final result in this checkout: 20/20 expected-render byte pins and 20/20 live-canonical fidelity pins, with no failures.

## Corpus witness outcome

On the cached CN oracle, `foundation-missed-connections`, `scp-cn-2771`, and `springfestival` are canonical-equal after the correction. `no-body-screaming` and `scp-3995` move past their original collapsible seams; their first remaining divergences are later paragraph/block-framing and whitespace ownership residues not caused by the corrected mechanisms. `tanijas-atelier-ecke` remains outside the parser cluster: its first divergence is an existing tabview empty-paragraph residue, and the user-space seam is XML-RPC/user-runtime representation evidence rather than a live parser rule.

## Files changed

The correction is limited to `text-wiki/Text/Wiki.php`, `text-wiki/Text/Wiki/Parse/Default/Collapsible.php`, `text-wiki/Text/Wiki/Parse/Default/Paragraph.php`, and `text-wiki/Text/Wiki/Parse/Default/Tableadv.php`, plus this conformance directory. No corpus file, live probe page, or ftml tree was modified.
