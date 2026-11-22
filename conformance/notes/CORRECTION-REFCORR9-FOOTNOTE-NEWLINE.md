# CORRECTION draft — R9-H — REFCORR9 mechanism for C-R5B-R3-1 = C-R5B-P4-1 (deduplicated)

This unit is mechanism R9-H of REFCORR9. It reproduces firsthand the one unique round-5b confirmation that the two lanes C-R5B-R3-1 and C-R5B-P4-1 name for the same source and capture family, derives the minimal reference fix, mirrors the parse-side decision in `lean-ftml/LeanFtml/NotesRules.lean`, and returns a patch payload for coordinator adoption. No canonical, reference, mirror, spec, pin, gate or Main.lean file was edited by this unit; the canonical tree is byte-identical before and after (git status empty for all four named files). All prose is flowing single lines and all Lean invocations went through the serial wrapper.

## Mechanism (root cause, firsthand)

The decisive source is `[[footnote]]@@@@\n@@@@[[/footnote]]` followed by `[[footnoteblock]]`. The two `@@@@` empty-Raw placeholders are placeholder bytes; REFCORR7's `Footnote::process` strip turns the stored body into the single LF between them, and REFCORR8's added `$content = trim($content)` (canonical `Footnote.php:79-81`) folds that LF to an empty stored body. `Footnoteitem::token` then emits `1</a>.</div>` (empty body, no separator space). Live emits `1</a>.<br /></div>`: it keeps the placeholder-bearing body, so `Text_Wiki_Parse_Newline`'s `([^\n])\n(?!\n)` sees an inline `\xFF` byte immediately before the LF and emits a Newline token that renders `<br />`; live's emptiness test for the separator space reads the visible (placeholder-stripped) body, which is empty, so no stray space appears. The naive one-line repair of storing the bare LF does not work: the reference harness then renders `1</a>. </div>` (separator space from `$body !== ''`, and the leading LF deleted by Tighten). Reverting REFCORR7/8 for this shape does not work either: it renders `1</a>. <br />\n</div>`, where the frame mask preserves the separator space (`>. <` is not an inter-tag newline). The minimal faithful fix is therefore two coupled decisions at the parse and separator-consumer sites: keep the pre-strip placeholder-bearing body only for the lone-newline remainder, and derive the separator space from the visible body instead of the raw stored bytes.

## Minimal fix

In `Footnote::process` save `$rawRemainder = $content` immediately before the empty-Raw `preg_replace_callback`, and replace `$content = trim($content)` with a guarded re-trim: when the post-strip remainder matches `/^[ \t]*\n[ \t]*$/D` (exactly one authored LF, optional horizontal flanks: R3B-03/C02 and F02), store `$rawRemainder`; otherwise keep the REFCORR8 `trim($content)`. The `/D` anchor prevents a trailing-LF match from broadening the shape. Every other remainder — empty, tab-only, two-space, NBSP, two-newline and literal-text — keeps the adopted REFCORR8 behaviour unchanged.

In `Text_Wiki_Render_Xhtml_Footnoteitem::token` ('start' arm) replace `$body !== ''` with a visible-body test: apply the same token-aware empty-Raw strip used in `Footnote::process` to `$body`, then test `trim($visible) !== ''`. This suppresses the separator space for the retained placeholder-bearing newline body while keeping it for literal-text bodies (R3B-05, F04) and the NBSP control (C21). The token-aware strip is required rather than stripping all placeholders: a footnote body holding only a non-empty Raw token must still receive its separator space.

In the mirror, `NotesRules.lean` gains a total byte-local predicate `isLoneNewlineRemainder` and `footnoteProcess` stores the pre-strip (`trimBytes body`) bytes when that predicate holds on the stripped body, otherwise the REFCORR8 `trimBytes stripped`. Three rfl theorems pin the new shape and its controls. The compared token wire shape is unchanged: one `Footnote` token with one `id` option, no added or reindexed token, no new DocState field, and no Main.lean audit-line change.

## php -l

`php -l` on the two patched files returns `No syntax errors detected in Footnote.php.refcorr9` and `No syntax errors detected in Footnoteitem.php.refcorr9` (PHP 8.5.4 CLI). All four batch renders exit 0 with zero stderr bytes.

## Before/after tables

The table below is the rule-level footnote-footer span. `before` is the canonical post-REFCORR8 PHP reproduced firsthand into scratch (hashes matching the conformance ref.jsonl files); `after` is the same harness on the patched PHP; `live` is the cached round-5b capture. Frame-only inter-tag whitespace is masked by the campaign `canon()` (probe.norm plus `>\s+<` collapse), exactly as in `conformance-round5b-r3/compare.py`.

| Row | Source shape | before (canonical ref) | after (patched ref) | live capture | verdict after |
|---|---|---|---|---|---|
| R3B-03 / C02 | `@@@@\n@@@@` | `1</a>.</div>` | `1</a>.<br />\n</div>` | `1</a>.<br /></div>` | CLEAR |
| F02 | `@@@@\n @@@@` | `1</a>.</div>` | `1</a>.<br />\n</div>` | `1</a>.<br /></div>` | CLEAR |
| C01 / R3B-02 | `@@@@\t@@@@` | `1</a>.</div>` | `1</a>.</div>` | `1</a>.</div>` | CLEAR |
| C03 / R3B-01 | `@@@@  @@@@` / three-space run | `1</a>.</div>` | `1</a>.</div>` | `1</a>.</div>` | CLEAR |
| C21 / R3B-06 | `@@@@ @@@@` (NBSP) | `1</a>. &nbsp;</div>` | `1</a>. &nbsp;</div>` | `1</a>. &nbsp;</div>` | CLEAR |
| F03 / R3B-19 | `@@@@\n\n@@@@` | `1</a>.</div>` | `1</a>.</div>` | `1</a>.</div>` | CLEAR |
| R3B-17 | `[[footnote]]\n[[/footnote]]` | `1</a>.</div>` | `1</a>.</div>` | `1</a>.</div>` | CLEAR |
| R3B-18 | `x@@@@\n@@@@y` | `1</a>. x<br />\ny</div>` | `1</a>. x<br />\ny</div>` | `1</a>. x<br />\ny</div>` | CLEAR |
| F04 | `x\ny` | `1</a>. x<br />\ny</div>` | `1</a>. x<br />\ny</div>` | `1</a>. x<br />\ny</div>` | CLEAR |
| R3B-05 | `hello  @@@@  ` | `1</a>. hello</div>` | `1</a>. hello</div>` | `1</a>. hello</div>` | CLEAR |
| F01 | bibliography newline sibling | `1.</div>` | `1.</div>` | `1.</div>` | CLEAR |

Full verification rerendered all 44 round-5b cases (16+3 R3, 21+4 P4) through the patched harness and compared every one against its cached live capture with the campaign `canon()`: 41 CLEAR, 2 owned token-counter digit rows (R5B-P4-C06/C19, the documented +1 residue class, not a rule-level divergence), 1 untestable save-layer row (R5B-P4-C17, invalid capture). Zero rule-level DIFF remains. The two confirmed rows R3B-03/C02 and F02 are now byte-clear after the campaign mask.

## Hashes

Canonical before: `Footnote.php` sha256 `10e8522c8c25d244ad8c35674c5b51c3c5e4dc051413553dd4be7f57045fab19`; `Footnoteitem.php` sha256 `b44677fa522d320ef701d55d9b1bbe554db4e36a9505eb21cc4e6c2ded5bb423`; `NotesRules.lean` sha256 `2861712e2414e8a2bc76bb48feb608ab1bcb3a7a209894d6fe99fced61d55902`. After: `Footnote.php.refcorr9` sha256 `bcf736eb5ad2ca2b09a2d2e9a0359874b180b38a7c1e5b8c25cc0ecd6367e557`; `Footnoteitem.php.refcorr9` sha256 `d2c555528daf92e1aeed4fcdca3ad6958c9e34bce8985e21dc8813e7e4c93464`; `NotesRules.lean.refcorr9` sha256 `f05e6755a63a4be4c1aef28fecaf00235497e979fd8368cb33da605d309c2347`. Unified diffs: `Footnote.php.refcorr9.patch` sha256 `b54a0f49b124c209b06fd453708b87ac58e77b89217bebefd57c3a5376df98f6`; `Footnoteitem.php.refcorr9.patch` sha256 `10341be88aaa27dc574f081ef1542637097e221026c7882f1f804fa1d19e5374`; `NotesRules.lean.refcorr9.patch` sha256 `b774cf8e31a14aee32fbadbc22e13e456fddbffddb2abf0cdf136c662bc817b6`. Reproduction renders from untouched canonical PHP matched the recorded conformance hashes exactly (R3 `ref.jsonl` `6b309b5190cbfc31adbd47d4e5a7d7b60920441f0d521c1a0e3de15118049506`, R3 follow-up `b4d2f8d3bcf77bc6bf3d1ac53bb12c6230ae823166f9ebf13e094cee432fba2a`, P4 `2f7d8757c8a9da1efcb4b7c6001b52f9cce8977b277302333d8eded206f1bcbd`, P4 follow-up `121c1b164caab4a5dad02fe26b4bc24d94bb10e31f8f9896282955e77f706861`).

## Lean verification and spec flip check

One wrapped incremental build of the patched scratch tree completed `Build completed successfully (176 jobs)` (log sha256 `fe630aeea9ab200dd808391d7d8786cc7ce20f8cd90e5eef2bcc6b60915ee819`, exit 0). `✔ [83/176] Built LeanFtml.NotesRules` and `✔ [85/176] Built LeanFtml.CoverageNotes` confirm both the mirror patch and the R8-FIX private `bibiPair` repair elaborate; the first attempt failed only on an over-strong rfl control theorem in this unit's new test, which was corrected, and the final build has zero `error:` lines. Main.lean is byte-identical (sha256 `52df1feb01dd4676c12584b27f69ee7b3e832cacf17c2db1afc95d7cb8673ffe`), with 899 literal `#print axioms` occurrences, 898 emitted reports in the build log, and only `[propext]`, `[propext, Quot.sound]` and `[propext, Classical.choice, Quot.sound]`; zero `sorryAx` and zero `native_decide`. A separate wrapped elaboration of `R9H_SpecFlip.lean` (log sha256 `ec71631e84b2bacdff6ce1befccebb743c65b5289480e4456ae9d908bd085848`, exit 0) proves no spec pin flips: `refcorr7_fn_empty_no_space`, `refcorr7_fn_ws_no_space` and `refcorr8_fn_empty_raw_retrim_no_sep` still reduce to rfl, while the new lone-newline examples reduce to the retained pre-strip body and the tab/two-newline/literal controls reduce as before.

## Wire-shape argument and mirror limitation

The compared token entry arity and option shape are unchanged: `footnoteProcess` still appends exactly one `Footnote` token carrying only `id`, and no DocState field is added. The changed value is the stored footnote body bytes for one shape, exactly the class REFCORR8 already changed. Mirror limitation disclosed for the coordinator: the PHP separator-space decision now reads the token table through `$this->wiki->tokens`, but the mirror's `NotesRender.lean:95-96` `renderFootnoteitem` has only `doc.footnotes` and cannot distinguish empty from non-empty Raw placeholders. With the retained placeholder-bearing body, the mirror's `body.isEmpty` separator test would emit a space where live emits none, so full render-level equivalence for this shape needs a companion render-side change or an explicit recorded limitation. This unit did not make that change because its assignment names NotesRules.lean as the mirror site; flagging it here prevents silent adoption of an incomplete mirror claim.

## Adoption payload

Apply three patches to canonical: `Footnote.php.refcorr9.patch` to `ref-php/text-wiki/Text/Wiki/Parse/Default/Footnote.php`, `Footnoteitem.php.refcorr9.patch` to `ref-php/text-wiki/Text/Wiki/Render/Xhtml/Footnoteitem.php`, and `NotesRules.lean.refcorr9.patch` to `lean-ftml/LeanFtml/NotesRules.lean`. Full after-files are provided alongside each patch. No spec, pin, gate, conformance or Main.lean file changes.

COMPLETE
