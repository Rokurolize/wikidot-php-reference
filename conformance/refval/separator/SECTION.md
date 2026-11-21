# Rule 4: Separator (`====`, pipeline pos 32, R3.15)

- **Battery**: 80 cases (`refval/separator/battery.jsonl`: 41 R3.15 `sep-*` authored + 0 R3.15 canonical + 21 extension cases `sep-x01`..`sep-x21` + 18 live probe cases `p01`..`p18`).
- **Live probes**: 18 pages `muse-probe-refval-separator-p01` through `muse-probe-refval-separator-p18` on `sandbox-for-codex`. All 18/18 validated (`valid=true`, `stable=true`, `saved_source_matches=true`).
- **Corrections (2)**:
  1. **Render (`ref-php/text-wiki/Text/Wiki/Render/Xhtml/Separator.php`, pre-correction backup `Separator.before-refval.php`)**: Changed self-closing `<div class="content-separator" style="display: none:"/>\n` to explicit closing `<div class="content-separator" style="display: none:"></div>\n` (live preserves the literal `display: none:` colon typo while serving a proper `</div>` closing tag; settled by `muse-probe-refval-separator-p01`–`p03`, `p11`–`p18`).
  2. **Paragraph skip (`ref-php/text-wiki/Text/Wiki/Parse/Default/Paragraph.php`, pre-correction backup `Paragraph.before-refval.php`)**: Added `'separator'` to `Paragraph::$conf['skip']` so standalone separator tokens are not wrapped in `<p><div class="content-separator" ...></div>\n</p>` (settled by `p01`–`p03`, `p11`–`p17`). Note: `Parse/Default/Separator.php` itself is unchanged and matches live 100%, including its single leading newline `"\n" . $token . "\n\n"` proven by `p18` (`a _\n====\nb` rendering two `<br />`s before `<div class="content-separator" ...></div>`).
- **Comparison before vs. after** (`refval/separator/compare-before.txt` -> `refval/separator/compare-after.txt`):
  - Before: 5/18 trim-equal / frame-normalized equal, 13 diffs (every separator wrapped in `<p>` with self-closing `<div .../>`).
  - After: 9/18 trim-equal (`p01`, `p04`–`p06`, `p09`–`p13`), 13/18 frame-normalized equal (`p01`–`p13`). The remaining 5/18 (`p14`–`p18`) are pure Stage 2 framing surfaces (`p14` `<div >`, `p15` `</ul><div`, `p16` `</table><div`, `p17` `@@<div`, `p18` `libtidy` splitting `<p>a<br />\n<br />\n<div></div></p>`).
- **Smoke check**: 9/9 smoke cases byte-identical to baseline (`SMOKE IDENTICAL: True`).
- **R3 stage consequence**: `Parse/Default/Separator.php` (R3.15) is unchanged. Adding `'separator'` to `Paragraph::$conf['skip']` affects **R3.11** (`Paragraph` mirror skip list).
- **ftml candidates**: None.
- **Verdict**: `CORRECTED (2 corrections)`
