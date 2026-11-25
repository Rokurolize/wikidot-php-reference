# CORRECTION REFCORR30 — ref-probe2 second-tier live-fidelity sweep

Status: APPLIED in this tree on branch `ref-probe2/second-tier-sweep` against
snapshot-53 (`e6034ef7d5980413e667e52a1af81714cd193f75`, the merged REFCORR28
state). The correction round is named REFCORR30 in the lane record.

## Live evidence

The sweep created twenty run-owned probe pages on `sandbox-for-codex.wikidot.com`
under `muse-probe-refprobe2-r30-*`, four focused pages under
`muse-probe-refprobe2-r30x-*`, and one explicit-Span control under
`muse-probe-refprobe2-r30y-*`; all are left in place. Every accepted capture is
`valid=true`, `stable=true`, and `saved_source_matches=true`. Raw HTML governed;
the campaign entity-decoding norm was not used to decide contested bytes. The
five decisive focused captures are copied into
`conformance/refcorr30/refcorr30-captures.json`.

Most of the matrix agreed once already-settled frame and environment surfaces
were masked. `[[code]]` type/attribute/body forms, explicit-list attribute
normalization and semantic attributes, marker-list attribute-like tails,
`[[size]]` value grammar, and explicit-source `[[gallery]]` item structure all
agree with live. The remaining gallery byte differences are the already-recorded
attachments environment branch (`Error selecting page.` in the harness) and
serving chrome (random gallery ids, lightbox scripts, wdfiles host, and pretty
printing); their normalized image/link/literal signatures are identical.

## Confirmed defects and correction

### R30-PURIFY-1 — render-generated TOC title whitespace bypasses Tighten

Live collapses horizontal whitespace runs inside a `[[toc title="..."]]` title
and trims the title edges. The decisive matrix titles
`" leading"`, `"trailing "`, `"in  ner"`, `"   "`, tab-padded text, and
`"  padded  "` render live as `leading`, `trailing`, `in ner`, empty, `tabbed`,
and `padded`. The pre-correction reference emitted the raw attribute bytes.

This is not reachable by the parse-time Tighten rule: the title is carried in a
token attribute and materialized only by the TOC renderer. Live reaches it
because every rendered fragment passes through
`WikiTransformation::purifyHtml`; local libtidy reproduction of that pass
matches the live bytes exactly.

### R30-PURIFY-2 — Size scopes crossing block boundaries need HTML repair

A size body containing a blank line produced crossing tags in the
pre-correction reference, for example
`<span style="font-size:90%;">line1</p>...<p>line2</span>`. Live serves two
well-formed paragraphs and reopens the size span in the second paragraph. The
focused six-case matrix also covers leading and trailing blank lines, three
paragraphs, nested inner size spans, and a single-newline negative control;
local libtidy reproduction of live's purify pass matches every live byte.

The same repair also resolves the already-recorded Size cross-block probes
`list-in-size` and `size-crosses-div`: the corrected reference now matches those
valid live captures exactly. This supersedes the older statement that those
crossings had to remain unrepaired in the sequential token model. It does not
rewrite the Size parse or render rules and does not claim a general Stage-2
implementation.

### Correction mechanism

`Text/Wiki.php` now detects two narrow unrepaired output shapes after the
sentinel strip:

1. a generated TOC title whose raw whitespace differs from the whitespace
   collapse/trim that purifyHtml applies; or
2. a font-size span still open at a paragraph end, whether produced by
   `[[size]]` or by an explicit span style.

Only then does it invoke the reference's existing tidy-backed
`purifyRecoveredHtml()` path, which wraps the fragment in the same strict XHTML
body shape used by live and extracts the repaired body. Well-formed documents
that do not contain one of those shapes keep the established reference frame;
this is intentionally not a global re-indenting purify pass.

## Pins

- `conformance/refcorr30/refcorr30-cases.jsonl` — two positive live matrices,
  one explicit-Span positive control, and two negative controls.
- `conformance/refcorr30/refcorr30-expected.json` — byte-level corrected output;
  all three positive pins are exact live bytes.
- `conformance/refcorr30/refcorr30-captures.json` — the raw valid focused live
  captures cited by the pins.
- `conformance/refcorr30/verify_refcorr30.py` — executable checker.
  Current result: **5/5 exact**.

## Validation

- REFCORR30 pins: **5/5 exact**.
- Frozen gates after correction: `S_local_71` **71/71**, `S_diag_44` **44/44**,
  `S_holdout_step4_150` **150/150**, and `S_holdout_fresh_150` **150/150**, zero
  diffs in each set.
- Battery regression comparison using the same checkout with only
  `Text/Wiki.php` swapped to its pre-correction bytes: code 68/68 unchanged,
  TOC 56/56 unchanged, gallery 88/88 unchanged, explicit lists 50/50 unchanged,
  and Size changes only in the three cross-block cases `sz69-list-in-size`,
  `sz70-size-crosses-div`, and `sz75-list-bold-close`. The first two have prior
  valid live probes and now match those live bytes exactly; the third is the
  same repair class.
- Main sweep after correction: `toc-attr-duplicate-case` and
  `size-nested-linebreaks` are now strict byte-exact, the fresh explicit-Span
  font-size control is byte-exact, and the already exact `size-value-matrix`
  remains byte-exact; TOC-family agreement is 6/6 and Size-family
  agreement is 2/2.
- Full EN corpus movement is recorded in the lane RESULT.md and corpus movement
  artifacts.

## Non-defect residuals explicitly not corrected

- `[[code]]`: unknown/highlighter type handling, ignored `language`, uppercase
  attribute keys, malformed attribute forms, literal wikitext bodies, empty
  bodies, and LF normalization all agree. Live CRLF normalization happens on
  save, before rendering.
- Explicit lists: attribute allowlist/order/case behavior, ignored `start`,
  `value`, and `reversed`, semantic `type` passthrough, and plain-text marker
  tails agree. Remaining differences are paragraph/inter-block frame.
- `[[gallery]]`: no new defect was confirmed. The attachment-query error string
  is the documented harness environment boundary; random gallery chrome,
  lightbox scripts, wdfiles URLs, and pretty-print whitespace are serving
  surfaces. Item image/link/literal signatures agree.
- General cross-rule inline re-nesting outside the detected font-size repair
  shapes remains later-rule/root-owned Stage-2 scope.
