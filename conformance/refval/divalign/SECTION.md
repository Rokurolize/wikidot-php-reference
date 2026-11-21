# Rule 7: Divalign (`[[=]]`, `[[<]]`, `[[>]]`, `[[==]]`, pipeline pos 38, R3.16)

- **Battery**: 82 cases (`refval/divalign/battery.jsonl`: 47 R3.16 `da-*` authored + 0 R3.16 canonical + 15 extension cases `da-x01`..`da-x15` + 20 live probe cases `p01`..`p20`).
- **Live probes**: 20 pages `muse-probe-refval-divalign-p01` through `muse-probe-refval-divalign-p20` on `sandbox-for-codex`. All 20/20 validated (`valid=true`, `stable=true`, `saved_source_matches=true`).
- **Correction (1)**:
  1. **Paragraph skip (`ref-php/text-wiki/Text/Wiki/Parse/Default/Paragraph.php`, pre-correction backup `Paragraph.before-refval.php`)**: Added `'divalign'` to `Paragraph::$conf['skip']` alongside the fossil's stale legacy names (`'divalignleft'`, `'divalignright'`, `'divaligncenter'`, `'divalignjustify'`). Without `'divalign'` in `skip`, `Paragraph` wrapped every `Divalign` start and end token in broken `<p><div style="text-align: ...;"></p>` and `<p></div></p>` pairs (`p01`–`p08`, `p11`–`p18`, `p20`). Adding `'divalign'` removes all spurious `<p>` wrappers and matches live's bare `</div>\n<br />\ny` after a block (`p08`, `p14`). Both `Parse/Default/Divalign.php` and `Render/Xhtml/Divalign.php` themselves are byte-unchanged and match live on all 20 probes.
- **What live confirms about `Parse/Default/Divalign.php`**:
  - All four alignments `=` (`center`), `<` (`left`), `>` (`right`), `==` (`justify`) render `<div style="text-align: <align>;">...</div>` (`p01`–`p04`).
  - Backreference matching and absorption of mismatched inner tags (`p05`: `[[==]]\nx\n[[/=]]\n\n[[=]]\nx\n[[/==]]` forms one justify div).
  - Empty blocks (`p06`, `p07`) render `<div style="text-align: center;"></div>` (exact match).
  - Line anchoring `^` and `$` (`p09`: trailing text on closer defeats match; `p10`: leading space/text on opener defeats match; `p11`: inline body on opener fails, inline body before closer succeeds).
  - Recursive `(?R)` priority (`p12`–`p14`), char-step backtracking past failed `(?R)` (`p15`: `[[=]]\n[[=]]\n[[/=]]`), and closer-with-trailing-text absorption (`p16`: `[[=]]\n[[/=]] extra\n[[/=]]`).
  - No leading/trailing `\n\n` around `$start`/`$end` (`p08`: `x\n[[=]]\nbody\n[[/=]]\ny` yields `<p>x<br /></p>\n<div ...>\n<p>body</p>\n</div>\n<br />\ny`).
  - Rejects attributes and trailing space on opener (`p19`: `[[= class="x"]]`, `[[=]] `).
- **Comparison before vs. after** (`refval/divalign/compare-before.txt` -> `refval/divalign/compare-after.txt`):
  - Before: 1/20 trim-equal, 3/20 frame-normalized equal, 17 diffs (all active blocks wrapped in malformed `<p><div></p>...<p></div></p>`).
  - After: 2/20 exact (`p06`, `p07`), 5/20 frame-normalized equal (`p06`, `p07`, `p09`, `p10`, `p19`), and all remaining 15/20 (`p01`–`p05`, `p08`, `p11`–`p18`, `p20`) match live's exact HTML element structure, differing only in Stage 2 pretty-printing `\n` inside `<div>` (and `libtidy` closing `<p>x<br /></p>` before `<div>` on `p08`).
- **Smoke check**: 9/9 smoke cases byte-identical to baseline (`SMOKE IDENTICAL: True`).
- **R3 stage consequence**: `Parse/Default/Divalign.php` (R3.16) is unchanged. Adding `'divalign'` to `Paragraph::$conf['skip']` affects **R3.11** (`Paragraph` mirror skip list).
- **ftml candidates**: None.
- **Verdict**: `CORRECTED (1 correction)`
