# REFCORR37 — paragraph-boundary and break accounting (F-PB)

REFCORR37 corrects a family of fossil parser behaviors where invisible or whitespace-only constructs either disappeared with the newline/block boundary they owned, or preserved the wrong newline. The evidence is the saved sandbox probe series `muse-probe-hunt-pb-*` through `muse-probe-hunt-pb4-*`, the cached corpus witnesses named in the hunt-pb lane, and the local frozen gates. Probe pages are left in place; no production page was accessed.

## Corrected mechanisms

1. A whitespace-only pre-wrap Raw atom is invisible content, not paragraph text. It still occupies its inline position, but it does not make a spacer paragraph nonempty and does not suppress the paragraph boundary around adjacent tables or tabviews.
2. Raw scanning treats a completed raw's closing `@` as a token boundary for a glued angle raw. In the `@@x@@@<&nbsp;>@` run, the surplus `@` of a three-at closer can open the following complete angle raw, so the decoded NBSP is serialized rather than leaking literal `@<&nbsp;>` fragments.
3. A truly empty line-led list is removed as a list but retains the block boundary that the swallowed marker line owned. Thus `a`, `* `, `b` renders as two paragraphs rather than either a list or one joined paragraph.
4. A whitespace-only/empty definition-list item retains an empty `<dl>` token pair long enough to preserve its block boundary; tidy then removes the empty element. A malformed `> : term` line inside a blockquote is swallowed with its line and does not force surrounding quote text into a separate live-incompatible shape.
5. An empty center marker is context-dependent. In mid-document it is consumed and renders an empty centered paragraph; exactly at end of input, before the harness's synthetic padding, a bare `= ` remains literal text. Consecutive empty center lines remain independent centered-empty paragraphs.
6. Empty spans are invisible atoms rather than ordinary text. A truly empty or whitespace-only unattributed span disappears, but a body consisting of two or more newlines still leaves those paragraph-breaking newlines behind. A body of exactly one newline is not empty on live and renders `<span><br /></span>`; an id-carrying empty span remains visible.
7. Inside an advanced-table cell, an explicit break immediately before a nested table owns a paragraph boundary even though the Break rule consumed its newline. The nested-table replacement restores that boundary, yielding `<p><br /></p><table>…</table>` rather than a bare break glued to the table.
8. The same cell-scope accounting applies to a whitespace seam around a nested table. When horizontal whitespace occurs both before the newline after the cell opener and as indentation before the nested table, live preserves one break-only paragraph before the table. Symmetrically, horizontal whitespace after the nested table closer plus indentation before the enclosing cell closer preserves one break-only paragraph after the table. A comment may occupy the seam without changing the result; spaces alone on only one side, indentation alone, no indentation, and ordinary leading text do not create the paragraph.

## Probe results

The grouped probe comparisons are canonical-equal for the layout matrix, raw/NBSP matrix, degenerate matrix, initial span matrix, initial advanced-table-cell matrix, generic terminal-break probes, the span-newline matrix, the table-cell comment matrix, the empty-div terminal probes, and the trailing-seam matrix. The terminal Rate probes are not whole-page canonical pins because live expands the Rate module on anonymous page serving while the corpus/reference representation suppresses that module; their trailing break counts are the generic N+2 sequence, and the empty-div terminal probes are also canonical-equal. The grouped witness-matrix page itself has label-separator differences outside the measured table shapes, so the isolated leading-seam shape is pinned instead.

## Pins

`cases.jsonl`, `expected.json`, `captures.json`, and `verify_refcorr37.py` pin 18 shapes: the grouped live probes listed above, the isolated leading advanced-table whitespace seam, and the EOF empty-center literal shape. The EOF center capture is a structural pin rather than a byte-verified saved-source capture because Wikidot normalizes a trailing space in the saved source; this limitation is recorded in the capture metadata. All 18 expected-render byte pins and all 18 live-canonical pins pass in this checkout.

## Corpus witness outcome

The cached live HTML for `en:note-immortality-amulet` and `jp:note-immortality-amulet` is canonical-equal after the table-cell whitespace-seam correction. The prior pre-wrap atom differences in `ko:defense-treaty` and `ko:whgustj37` and the angle-raw NBSP leakage in `ko:falling-nemesis` are cleared; those pages now reach non-F-PB serving/localization residues (`Footnotes` versus `각주`, or the KO clearfloat/footer serving tail). `jp:old:scp-3247` is dissolved as article-content evidence because its cached live HTML is the deleted-page template, not article HTML.

`jp:macro-7happy7-proposal` remains a sharply bounded residue: cached XML-RPC HTML has four terminal breaks after an empty centered Rate container, while the reference and all anonymous serving probes of terminal breaks after nonempty or empty centered divs produce five for three authored breaks. Fresh anonymous probes with a visible Rate widget also produce the generic count, so the remaining one-break difference is specific to the XML-RPC/module-mediated surface and is not converted into a parser rule without a discriminating API-serving probe.

## Superseded legacy pin

The REFCORR27 `tableadv-comment-indented-line` byte expectation was generated before the live break-only paragraph in this exact advanced-table seam had been discriminated. Fresh live probes and both note-immortality witnesses show the `<p><br /></p>` paragraph, so that legacy byte pin is updated to the corrected live-verifiable output rather than preserved as a fossil regression. All other prior pin artifacts are unchanged.

## Files changed

The correction is limited to `Center.php`, `Deflist.php`, `List.php`, `Paragraph.php`, `Prefilter.php`, `Raw.php`, `Span.php`, and `Tableadv.php`, plus this conformance directory. No render rule, module implementation, corpus file, or ftml tree was changed.
