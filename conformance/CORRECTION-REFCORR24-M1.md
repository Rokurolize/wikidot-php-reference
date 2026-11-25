# CORRECTION REFCORR24 — over-threshold quoted-head Tableadv

Status: APPLIED in this tree on branch `refcorr24/tableadv-threshold` against
snapshot-48 (`09bb79184b23641e878e72deb7f7ebe0a8284d2d`). Base is the
`refcorr24/tableadv-threshold` branch with zero predecessor commits.

## The question

REFCORR22 R2 split Tableadv parsing by `strlen($wiki->source)` measured at the
Tableadv stage, after earlier rules' placeholder substitution: inputs of at most
8192 bytes used the definitional recursive regex, larger inputs used the
REFCORR16 linear scanner. The split was an implementation fallback for PCRE
failure, not a claimed live semantic. The named remainder was whether live
Wikidot parses quoted-head tables whose stage size exceeds 8192, or leaves them
literal. The r2 witness padded to 9,929 stage bytes rendered literal under both
snapshot-46 and snapshot-47, so the question was open.

## Live evidence

A 45-witness family crosses three quoted-head shapes (`q0` = the exact r2
ambiguous head, `qx` = `x`, `qsp` = `x y`) with three padding placements
(`pre`, `cell`, `post`) and stage sizes 8100, 8192, 8193, 8300, 10000, 16000,
plus small unpadded controls. Source generation and stage instrumentation are in
the lane (`make_witnesses.py`, `measure-tableadv-stage.php`); every verdict uses
the stage-measured size from `stage-measurements.jsonl`, never the source size.

All 45 pages `muse-probe-tadv-thr-<witness-id>` were created once on
`sandbox-for-codex.wikidot.com` and left in place. Their raw HTML was fetched
once each and cached at
`/home/roku/.local/state/wikijump/muse-bhl/post-agy-finish/lanes/tadv-threshold/live-probes/html/<witness-id>.html`
(no failed or empty cache entries). The `#page-content` fragment governs.

Result: **live parses the outer advanced table on all 45 witnesses**, including
all 30 witnesses whose stage size is above 8192. The inner ambiguous quoted-head table stays
literal text in the outer cell, exactly as the definitional grammar predicts;
the outer `[[table]]/[[row]]/[[cell]]` construct becomes real HTML. There are no
UNDECIDABLE witnesses.

Against that evidence the inherited snapshot-48 reference canonically matches
live on 15 of 45 (exactly the witnesses at or under 8192 bytes) and **diverges
on all 30 over-threshold witnesses**: the linear scanner's head approximation
consumes the closer inside the quoted text and drops the outer table to a
literal `<p>`. Forcing the definitional grammar on those inputs confirms the
grammar itself produces live's structure; it does not need changing. The
snag was operational: with PCRE JIT enabled the recursive pattern hits
`PREG_JIT_STACKLIMIT_ERROR` on the over-threshold `cell` and `post` shapes
(18 witnesses), which is why REFCORR22 withheld it from large inputs.

## Correction

The divergence is in the *path selection*, so the correction owns `parse()` in
`text-wiki/Text/Wiki/Parse/Default/Tableadv.php`:

- The 8192-byte split is removed. The definitional recursive expression, which
  REFCORR22 established as the behavioral grammar, now runs at every stage
  size. That matches live's observed behavior on every witness.
- PCRE JIT is switched off for the duration of the single `preg_replace_callback`
  call and restored immediately afterward. JIT's fixed stack, not the grammar,
  was the resource that failed at corpus scale; the interpreted PCRE path
  honors the much larger `pcre.backtrack_limit` / `pcre.recursion_limit` and
  completes the same match with no preg error on all 45 witnesses (max 13.7 ms
  per case). No global PCRE setting is left changed.
- The linear scanner is retained only as a last-resort fallback when PCRE still
  returns null, so a genuine PCRE failure cannot silently truncate a render.

No change was made to the regex, `process()`, attribute handling, or any other
Tableadv behavior. `processPreserveBoundary()` continues to keep the direct
regex path byte-compatible with the scanner's boundary-newline treatment.

## Pins

- `conformance/table/tableadv/refcorr24-cases.jsonl` — the 45-witness family
  (`id`, `source`), with stage sizes in the two companion files.
- `conformance/table/tableadv/refcorr24-expected.json` — fixed reference render
  per witness (`html`, `source`, `tableadv_stage_len`, `evidence`), a byte-level
  regression pin.
- `conformance/table/tableadv/refcorr24-captures.json` — cached live page
  fragment per witness (`fullname`, `html`, hashes, `tableadv_stage_len`,
  validity flags, `evidence`), the live-fidelity pin.
- `conformance/table/tableadv/verify_refcorr24.py` — executable checker.
  Verification used batch render with canonical `>\s+<` collapse and outer
  newline stripping, matching the repository's `compare_x.py` convention:
  **expected-render 45/45, live canonical fidelity 45/45**.

## Validation

Four frozen gates (`tools/score_gates.py`, recorded in the lane's `gates.json`
and `gates.log`): `S_local_71` 71/71, `S_diag_44` 44/44,
`S_holdout_step4_150` 150/150, `S_holdout_fresh_150` 150/150 — all green, zero
diffs.

### Full corpus

Command (from the lane directory):

```bash
python3 /home/roku/.local/state/wikijump/muse-bhl/criteria-drain/run_corpus.py \
  --checkout /home/roku/.local/state/wikijump/muse-bhl/post-agy-finish/tadv-reference \
  --out-dir /home/roku/.local/state/wikijump/muse-bhl/post-agy-finish/lanes/tadv-threshold/corpus-run-final \
  --workers 6
```

Result in `corpus-run-final/run-summary.json`: **25,534 pages, zero errors,
362.24 s**, checkout `6d552f01` (the REFCORR24 commit). Outcome/class counts are
unchanged from the snapshot-48 baseline: `clean` 25,392; `near-empty-short-render`
95; `empty-postparse-nonempty` 5; `clean-empty-source` 13; `empty-token-only` 29.
API-scored pages 25,435 with **107 strict** and **136 userdb-masked** tidy-oracle
matches; the pure+user slice is **95 / 122**. These are the same numbers as the
base register.

Movement comparison (`tools/score_gates.py`-style register diff, recorded in the
lane's `corpus-movement-analysis.json`, `corpus-movement-classified.json` and
`corpus-movement-pages.txt`) against the snapshot-48 register at
`lanes/r3-statics/corpus-run-collapsible-final/register.jsonl` (git head
`a3917ec`, whose tree is byte-identical to `09bb791`):

- class movements: **0**
- tidy score movements: **0**
- error records: **0**
- output-hash movements: **194**, all re-rendered in isolation in both the base
  checkout and this checkout; **194/194** genuinely differ in isolation, so none
  is a batch artifact.

Every one of the 194 pages carries advanced-table source. The classifier labels
all 194 `tableadv-frame` and finds no `manual` or `manual_or_mixed_review` page;
157 also carry date/email constructs incidentally, but `normalized_same` is false
for all 194, so none is a placeholder-numbering-only change. The exact movement
is the definitional path's boundary-newline handling replacing the scanner's at
table-adjacent block boundaries: 82 pages unwrap a `<p>…</p>` immediately *after*
a `</table>` into a `<br />`, 36 do so immediately *before* a `<table>`, 10 unwrap
an adjacent paragraph, 27 gain a `<br />` at a block boundary, and 39 show the
same one-line whitespace framing variant. These are the same two path
semantics that REFCORR22 already recorded for `adv06-midline-table`: the
recursive grammar and the linear scanner preserve adjoining source newlines
differently. No page newly matches or stops matching the live oracle under
either the strict or the userdb-masked score, which is why the gate and corpus
scores stay green. The complete per-page list with category and diff context is
in the lane's `corpus-movement-pages.txt`.

## Residual

The under/over-threshold quoted-head ambiguity is settled for all three heads,
all three padding placements, and all measured stage sizes through 16,000 bytes.
The only byte-level difference between reference and raw live on the `pre` and
`post` shapes is the pre-existing block-boundary newline count, which the
conformance frame canonically normalizes and which is identical above and below
the threshold; it is not part of this remainder. No residual sub-shape was left
unsettled.
