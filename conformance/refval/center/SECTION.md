# Rule 3: Center (`= ...`, pipeline pos 52, R3.15)

- **Battery**: 93 cases (`refval/center/battery.jsonl`: 43 R3.15 `ce-*` authored + 26 R3.15 canonical + 6 extension cases `ce-x01`..`ce-x06` + 18 live probe cases `p01`..`p18`).
- **Live probes**: 18 pages `muse-probe-refval-center-p01` through `muse-probe-refval-center-p18` on `sandbox-for-codex`. All 18/18 validated (`valid=true`, `stable=true`, `saved_source_matches=true`).
- **Corrections (2)**:
  1. **Parse (`ref-php/text-wiki/Text/Wiki/Parse/Default/Center.php`, pre-correction backup `Center.before-refval.php`)**: Changed `$regex` from `'/\n\= (.*?)\n/'` to `'/^= (.*)$/m'` and trimmed the captured line in `process()` (`trim($matches[1])`). Settled by `muse-probe-refval-center-p10` (`x\n= a\n= b\ny`), `p11` (`x\n= a\n= b\n= c\ny`), and `p08` (`x\n=  padded\ny`). The fossil regex consumed the trailing newline of each match, causing every second consecutive `= ` line to miss the rule and fall into an ordinary paragraph; live Wikidot centers every consecutive `= ` line and strips leading/trailing spaces inside the centered `<p>`.
  2. **Render (`ref-php/text-wiki/Text/Wiki/Render/Xhtml/Center.php`, pre-correction backup `Center.before-refval.php`)**: Appended trailing `\n` to the closing tag (`"</p>\n"` instead of `'</p>'`) to match live's block boundary newline (`p02`, `p04`–`p08`, `p10`–`p13`, `p18`).
- **Comparison before vs. after** (`refval/center/compare-before.txt` -> `refval/center/compare-after.txt`):
  - Before: 2/18 trim-equal, 4/18 frame-normalized equal, 14 diffs (including real parse failures on `p10`, `p11` and leading space on `p08`).
  - After: 3/18 trim-equal (`p01`, `p02`, `p09`), 15/18 frame-normalized equal (`p01`–`p13`, `p17`, `p18`). The only 3 remaining diffs (`p14` `<div >`, `p15` `<blockquote><p>`, `p16` `</ul><p>`) are Stage 2 pretty-printing on the surrounding `Div`, `Blockquote`, and `List` blocks.
- **Smoke check**: 9/9 smoke cases byte-identical to baseline (`SMOKE IDENTICAL: True`).
- **R3 stage consequence**: **R3.15** (`LeanFtml/MiddleRules.lean` `centerScan` and `ConformanceR315` fixtures/worked examples) — `Center`'s parse pattern changed from newline-consuming `/\n\= (.*?)\n/` to line-anchored `/^= (.*)$/m` with `trim($matches[1])`. Note that `REPORT-R315.md` specifically flagged the consecutive-lines miss as a fossil quirk now refuted by live.
- **ftml candidates**: None.
- **Verdict**: `CORRECTED (2 corrections)`
