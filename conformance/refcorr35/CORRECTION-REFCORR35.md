# CORRECTION REFCORR35 — malformed advanced-table heads and leading nested openers

Status: APPLIED in this tree on branch `hunt-at/refcorr35` against snapshot-58
(`766b545b6185aee67d97f4a66733e0335ffee1f3`). Not merged, not tagged; the
coordinator lands it after verification.

## The question

Family F-AT stood with three mechanism candidates: (1) malformed/doubled-quote
advanced-table heads are salvaged or normalized by live rather than merely
demoted; (2) nested `[[table]]` in a cell is treated as literal by the reference
where live serves nested structure; (3) attribute serialization spacing is a
separate normalization layer. Corpus first differences alone could not separate
scanner-level demotion from attribute-normalizer repair.

## Live evidence: one grouped sandbox probe

A single saved page, `muse-probe-hunt-at-malformed-heads` on
`sandbox-for-codex.wikidot.com`, carried six labeled shapes (one probe-page
cycle, two anonymous GETs, byte-exact saved-source verification, stable and
valid). It was created serially at >=1 s pacing with the honest user agent
`ftml-equivalence-probe/1.0 (lane=hunt-at; contact=Rokurolize)` and is left in
place. Source, map, raw capture and ledger rows are in the hunt-at lane.

| shape | source head / body | live output |
|---|---|---|
| S1-VALID | `[[table style="border-collapse:collapse; margin:0 auto;"]]` | `<table style="border-collapse:collapse; margin:0 auto;">` |
| S2-WIDTH | `[[cell style="border: 1px solid black;" colspan="2" width: 50%"]]` | `<td style="border: 1px solid black;" colspan="2&quot; width: 50%">` |
| S3-SPACING | `padding: 0.5em;` + newline + `line-height:` inside a style value | `padding: 0.5em; line-height: 1.75em;` (newline -> one space) |
| S4-NESTED | nested `[[table]]` inside the first cell of a closed outer table | `<td><p>OUTER-S4</p><table>…</table></td>` — real nested structure |
| S5-DQUOTE | `[[table style="border-collapse:collapse; margin:0 auto;""]]` | `<table style="border-collapse:collapse; margin:0 auto;&quot;">` — table parsed, extra quote kept inside the style value |
| S6-DQUOTE-NESTED | doubled-quote outer head + inner `[[table]]` + one closer | `<table style="…&quot;"><tr><td>S6-CELL</td></tr></table>` — outer parsed, inner opener demoted |

Before the fix, the snapshot-58 reference matched S1 and S2 byte-for-byte,
matched S4 only canonically (block-boundary newlines), emitted S3 with the
newline deleted (`padding: 0.5em;line-height:`), and mis-paired S5/S6 so that
S5-CELL was dropped and S6 vanished entirely. The half-second-capable JIT-free
regex head swallowed 194 characters starting at S5's extra quote.

## Mechanism decision

- **Candidate 1 (salvage) is confirmed for the doubled terminal quote.** The
  extra quote belongs to the last attribute value; live parses the table and
  serializes the quote as `&quot;`. This is scanner/head-level demotion repair,
  not a global attribute-normalizer change.
- **Candidate 2 (nested-table literalism) is confirmed for the leading-opener
  shape only.** Live demotes an inner `[[table]]` opener that is the first
  content of an outer body and has no closer of its own; S4 shows that a
  properly closed nested table in a cell already works in the reference, so
  the candidate is not a general cell-scope defect.
- **Candidate 3 (spacing) is confirmed as a separate layer.** Live collapses a
  newline inside a quoted attribute value to one space; the reference deleted
  it as a C0 control byte.
- **Misplaced `width:` is falsified as a live-vs-reference defect.** On the
  fresh probe the reference is byte-identical to live for S2. The cached
  2026-11-02 KO capture for `scp-1981-ko` shows an older live parse
  (`colspan="3" width:=""`), while fresh live renders
  `colspan="3&quot; width: 50%"`, exactly the reference's bytes. The corpus
  first difference there is a stale-capture artifact, not a current divergence.

## Correction

All changes are in `text-wiki/Text/Wiki/Parse/Default/Tableadv.php`:

1. The table head grammar gains a doubled-quote alternative
   `(?:"[^"]*""|"[^"]*"|[^\]])*` before the ordinary quoted alternative, in
   the definitional regex, the nested-table scanner opener and the
   outside-row cleanup. A terminal `""` is consumed as a quoted value plus
   one literal quote, so the match ends at the real `]]` instead of reaching
   for a quote in a later block. A quoted `]]` inside a legitimate value
   (`class="a]]b"`) still parses exactly as before.
2. `normalizeValue()` keeps TAB/LF/CR for `\s+` collapsing and drops only the
   other C0 bytes plus DEL. Newlines in style values become one space, matching
   live; no other attribute normalization rule changes.
3. The linear scanner's `_tableadvBody()` demotes a nested `[[table]]` opener
   when it is the first non-whitespace content of an enclosing table body:
   the enclosing table closes at the first available closer and the inner
   opener stays literal. A nested table inside a row or cell keeps its own
   closer and its normal structure. This path matters at corpus scale, where
   the recursive expression can exhaust `pcre.backtrack_limit` and the
   REFCORR24 last-resort scanner is used.

No render rule, no other parse rule and no global PCRE setting changed.

## Pins

- `cases.jsonl`, `expected.json`, `captures.json`, `verify_refcorr35.py` in this
  directory. Six labeled shapes with byte-level expected renders and cached
  live fragments. Verification: expected-render **6/6**, live canonical
  fidelity **6/6**.

## Validation

Frozen gates on this tree: `S_local_71` 71/71, `S_diag_44` 44/44,
`S_holdout_step4_150` 150/150, `S_holdout_fresh_150` 150/150, zero diffs.

Every prior REFCORR pin set: REFCORR27 5/5, REFCORR28 5/5, REFCORR29 12/12,
REFCORR30 11/11, REFCORR31 5/5, REFCORR32 11/11, REFCORR34 4/4,
REFCORR-next form/raw 8/8 and 8/8, REFCORR24 45/45 byte pins and 45/45 live
canonical fidelity, REFCORR-next framing 8/8, 8/8 and 5/5. Full output in the
hunt-at lane (`pins-refcorr35.log`, `gates-refcorr35.log`).

Corpus movement audit (snapshot-58 base worktree vs this tree, full page sets):

- KO 11,243 pages: 19 output movements; 19/19 carry advanced-table source —
  13 `cb:*` pages carry a multiline style value (spacing fix), 6 pages carry a
  doubled terminal quote plus a leading nested opener. KO canonical first
  mismatch improved on 13 pages, regressed on 0; `cb:joke-scps` and
  `cb:scrapped-scps` became canonical-equal.
- EN 25,534 pages: 2 output movements; both carry advanced-table source (one
  multiline style value, one leading nested opener). Neither changes the first
  canonical mismatch; no regression.

Artifacts: `corpus-movement-ko.json`, `corpus-movement-en.json` in the lane.

## Residual and parity

The following are *not* repaired by REFCORR35 and are recorded in the lane
RESULT with both outputs:

- `note-immortality-amulet`: live emits `<p><br /></p>` before a nested table
  inside an outer cell; the reference omits that break-only paragraph. The
  grouping probe's plain nested-table shape is canonical-equal, so this is a
  comment/blank-line ownership seam, not a nested-table parsing defect.
- `scp-879-ko`: after the table fix the first difference is the localized
  footnote title (`각주` live vs `Footnotes` reference), a serving/localization
  environment difference.
- `scp-1982-ko` and `scp-566-ko`: after the table fix the first difference is
  only the live KO serving tail (`clear:both` / `ko-footer`), which the offline
  harness does not emit.
- `scp-1981-ko`: stale cached-capture artifact described above; no live defect
  on the fresh probe.

Unclosed doubled-quote heads with more than one extra quote are unevidenced and
left untouched; only the exact doubled shape is repaired.
