# CORRECTION REFCORR-NEXT — adjacent-paragraph framing at Tableadv boundaries

Status: APPLIED in this tree on branch `refcorr-next/tableadv-framing` against
snapshot-49 (`3149cf6bdb1ff5cdd94545808a62f924e23ede3f`, merge of PR #20).
Base is snapshot-49 with zero predecessor lane commits. PR link is recorded in
RESULT.md once opened; do not merge, do not tag (the coordinator lands rounds).

## The question

REFCORR24 removed the Tableadv 8192-byte size split so the definitional
recursive grammar runs at every stage size. Its corpus run moved 194 large
pages, all tidy-oracle neutral. The coordinator's raw-content verifier sampled
three of them (`7ring`, `a-symphony-of-iron-and-steel`,
`a-brief-overview-of-antimemetic-hazards`) and found that on those pages the
grammar path unwraps the `<p>…</p>` around the spacer line adjacent to a table
into `<br />`, while live keeps the `<p>` wrapper. The scanner path, which those
large pages used before REFCORR24, produced live's framing. The named remainder
was whether this is a large-page-only effect of exposing the grammar at scale,
whether the grammar or the surrounding paragraph machinery owns it, and what
the correct correction is. Verifier report:
`/home/roku/.local/state/wikijump/muse-bhl/verify-tadv-content/VERIFY-TADV-CONTENT.md`
(item 4).

## Verdict

**The reference diverged from live, at every size; the divergence is owned by
Tableadv's own boundary-newline preservation, not by the surrounding paragraph
machinery and not by the REFCORR24 path selection.** Corrected at that layer.
Live behavior is definitionally correct; the corpus tidy oracle is only a
scoring instrument, so the framing claim is judged on raw bytes against cached
live, not on score neutrality.

## Scope — witness table

Stage sizes are measured immediately before the Tableadv rule
(`lanes/tadv-threshold/measure-tableadv-stage.php`), never from source length.
`p` = spacer `<span style="white-space: pre-wrap;">&#32;</span>`.

| witness | stage bytes | shape | before fix (grammar) | live |
|---|---:|---|---|---|
| mini-after-table | 78 | after-table spacer | `</table><br />\n<p-ish span>` | scanner/live keep `<p>{sp}</p>` |
| mini-before-table | 75 | before-table spacer | `{sp}<br />` before `<table>` | scanner/live keep `<p>{sp}</p>` |
| mini-block-boundary | 73 | table then div | `</table><br />\n<div>` | `</table>\n<div>` |
| fragment:scp-5153-2 | 3,714 | after-table spacer | `</table><br />\n{sp}<div>` | `</table>\n<p>{sp}</p>\n<div>` |
| fragment:scp-3272-1 | 7,239 | after-table spacer, then table | `</table><br />\n{sp}<br />\n<table>` | `</table>\n<p>{sp}</p>\n<table>` |
| 7ring | 20,288 | after-table spacer run | `</table><br />\n{sp}<br />…` | `</table>\n<p>{sp}<br />…` |
| a-symphony-of-iron-and-steel | 60,235 | before-table spacer | `{sp}<br />\n<table>` | `<p>{sp}</p>\n<table>` |
| a-brief-overview-of-antimemetic-hazards | 73,534 | table then div | `</table><br />\n<div>` | `</table>\n<div>` |

The first three witnesses are at stage sizes 73–78 bytes: the grammar path was
already used at those sizes in snapshot-48, before REFCORR24. The framing
difference therefore **exists below the old threshold too**; REFCORR24 did not
introduce it, it only exposed it on 194 more pages. All five corpus witnesses
match live's `<p>` framing after the fix; the residual newline count around
`</table>` is the serving-layer normalization the conformance canon collapses
and is identical above and below the threshold.

## Mechanism and owned layer

The Tableadv rule has two paths:

- The linear scanner `_scanTableadv()` replaces a parsed table and explicitly
  re-adds one `\n` before and after it when the source has one there
  (`if ($src[$m[0]] === "\n") $rep .= "\n";`). That extra newline creates a
  blank line around the tokenized table, so the Paragraph rule's
  `/^.*?\n\s*?\n/m` closes the preceding paragraph and starts a fresh one for
  the adjacent spacer line. Live shows exactly that `<p>` wrapper.
- The direct regex path used `preg_replace_callback` with
  `processPreserveBoundary()`. Its comment claimed it "consumes the regex's
  optional boundary newlines as part of the match" and re-added them. But the
  pattern `~\[\[table…\]\]…\[\[/table\]\]~si` has **no** boundary newlines: the
  match starts at `[[table` and ends at `]]`. Both `substr($matches[0],0,1)==="\n"`
  and `substr($matches[0],-1)==="\n"` were always false, so the guard was dead
  code and the regex path never reproduced the scanner's blank line. Without
  it the adjacent spacer line stays inside the table's paragraph and the
  Newline rule serves its line break as `<br />`.

The Paragraph and Newline rules behave correctly on the source stream they
receive: given the scanner's blank line they emit `<p>{sp}</p>`, and given the
regex path's single newline they emit `<br />`. They are not indicted. The
Tableadv grammar, attributes, render and REFCORR24 path selection are not
indicted either. The single indicted layer is `processPreserveBoundary()`'s
failure to reproduce the scanner's boundary-newline treatment.

## Correction

In `text-wiki/Text/Wiki/Parse/Default/Tableadv.php` only:

- `parse()` passes `PREG_OFFSET_CAPTURE` to `preg_replace_callback` so the
  callback can see where the match sits in `$this->wiki->source`.
- `processPreserveBoundary()` unwraps the offset-captured matches, calls
  `process()` with the plain match strings, and — only when the table actually
  parsed (`$replacement !== $full`, mirroring the scanner's own guard) —
  prepends/appends one `\n` when the source byte immediately before/after the
  match is `\n`, exactly as `_scanTableadv()` does.

No regex, `process()`, attribute, render, Paragraph, Newline or path-selection
code changed. PCRE JIT is still disabled only for the one call and restored.

## Pins

- `conformance/table/tableadv/refcorr-next-framing-cases.jsonl` — 8 witnesses
  (3 synthetic at stage 73–78 bytes; 5 corpus pages spanning 3,714–73,534
  bytes), with `id`, `kind`, `source`.
- `conformance/table/tableadv/refcorr-next-framing-expected.json` — fixed
  reference render per witness plus the measured stage size (byte regression).
- `conformance/table/tableadv/refcorr-next-framing-captures.json` — cached live
  `#page-content` fragment for the five corpus witnesses (live-fidelity pin).
- `conformance/table/tableadv/refcorr-next-framing.json` — the canonical
  table-adjacent framing substrings asserted in both render and live.
- `conformance/table/tableadv/verify_refcorr_next_framing.py` — checker:
  expected-render 8/8, render framing 8/8, live framing 5/5.
- The pre-existing REFCORR24 verifier remains green: expected-render 45/45,
  live canonical fidelity 45/45.

## Validation

Four frozen gates (`tools/score_gates.py`, recorded in the lane's
`gates/gates-final.json` and `.log`): `S_local_71` 71/71, `S_diag_44` 44/44,
`S_holdout_step4_150` 150/150, `S_holdout_fresh_150` 150/150 — all green, zero
diffs.

### Full corpus

Command (from the lane directory):

```bash
python3 /home/roku/.local/state/wikijump/muse-bhl/criteria-drain/run_corpus.py \
  --checkout /home/roku/.local/state/wikijump/muse-bhl/post-agy-finish/r5-reference \
  --out-dir /home/roku/.local/state/wikijump/muse-bhl/post-agy-finish/lanes/r5-framing/corpus-run-final \
  --workers 6
```

Result in `corpus-run-final/run-summary.json`: **25,534 pages, zero errors,
339.8 s**, checkout `f219ea14` (the fix commit). Outcome/class counts are
identical to the pristine snapshot-49 baseline: `clean` 25,392;
`near-empty-short-render` 95; `empty-postparse-nonempty` 5;
`clean-empty-source` 13; `empty-token-only` 29. API-scored 25,435 with 107
strict and 136 userdb-masked tidy matches; the pure+user slice is 95 / 122 —
the same scores as the baseline register. Class movements **0**, tidy score
movements **0**, error records **0**.

Output-hash movements against the pristine snapshot-49 register
(`lanes/tadv-threshold/corpus-run-final/register.jsonl`, git head `6d552f01`,
tree identical to snapshot-49): **221**. Of these, 186 are pages from the
REFCORR24 194-movement list (185 byte-identical to the snapshot-48
scanner-based output) and 35 are newly moved small pages below the old split —
the below-threshold scope witnesses. Every movement was re-rendered in
isolation in the baseline, the fixed tree and with the forced linear scanner;
all 221 are scanner-aligned under the conformance canon (220 byte-identical to
the forced scanner, one differing only by one serving-layer newline, canonically
equal), none is a batch artifact. Judged on raw cached-live framing bytes:

- **214** movements move the table-adjacent framing distance to live down;
- **6** are framing-neutral to live (the same mechanism at a boundary where
  live keeps neither a break nor an empty paragraph; the fixed output equals
  the forced scanner's on all six);
- **1** (`the-barrow-station-incident-part-ii`) has no cached live capture (its
  live page now 404s); it is a byte-exact restoration of the snapshot-48
  scanner output, `</table><br /><div>` → `</table><div>`, the same category the
  verifier settled on `a-brief-overview-of-antimemetic-hazards`, and is
  adjudicated by that pin category.
- **0** unexplained or live-diverging movements.

Full per-page adjudication: `lanes/r5-framing/movement-adjudication-final.json`.
