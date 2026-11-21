# Rule 2: Break (` _\n`, pipeline pos 34, R3.15)

- **Battery**: 82 cases (`refval/break/battery.jsonl`: 44 R3.15 `br-*` authored + 4 R3.15 canonical + 16 extension cases `br-x01`..`br-x16` + 18 live probe cases `p01`..`p18`).
- **Live probes**: 18 pages `muse-probe-refval-break-p01` through `muse-probe-refval-break-p18` on `sandbox-for-codex`. All 18/18 validated (`valid=true`, `stable=true`, `saved_source_matches=true`).
- **Reference vs. live comparison** (`refval/break/compare-before.txt`):
  - 2/18 exact (`p11`, `p12`), 12/18 trim-equal (`p01`–`p03`, `p05`, `p07`–`p13`, `p15`).
  - Remaining 6/18 (`p04`, `p06`, `p14`, `p16`, `p17`, `p18`) all agree with live on `Break` parsing and rendering, differing only on Stage 2 / serving-layer framing surfaces:
    - `p04` (`a\t_\nb`) and `p06` (`a  _\nb`): `Break` fires on both (confirming `Prefilter` expands `\t` to 4 spaces before `Break` runs). Live renders `<p>a<br />\nb</p>` where the reference renders `<p>a <br />\nb</p>\n\n`: Stage 2 `libtidy` strips a trailing space immediately before `<br />` (the same surface `Tighten.php` models for `Newline` tokens but not `Break` tokens).
    - `p14` (`> a _\n> b`) and `p16` (`[[div]]\na _\nb\n[[/div]]`): Stage 2 pretty-printing inside `<blockquote>` / `<div>` and `<div >`.
    - `p17` (`a _\n----\nb`): `Break` + `Newline` produce two `<br />`s before `<hr />` on both sides; Stage 2 `libtidy` unwraps `<p>a<br />\n<br />\n<hr />\n</p>` to `a<br />\n<br />\n<hr />`.
    - `p18` (`x\n= a _\nb\ny`): `Break` fires before `Center`, producing `<p style="text-align: center;">a<br />\nb</p>` on both sides; only inter-block `\n` differs (resolved by `Center` render correction).
- **What live confirms**:
  - Literal ` _\n` (`/ _\n/`) renders `<br />\n`, including at EOF (`p02`: `a _` -> `a<br />\n<br />` via `Prefilter`'s appended `\n\n`), stacked (`p07`), before blank line (`p08`), line-initial (`p10`), inside list items (`p11`), table cells (`p12`), blockquotes (`p14`), bold/span (`p15`), divs (`p16`), and centered lines (`p18`).
  - Trailing space (`p03`: `a _ \nb`), `a__`, bare `_`, `a _x` (`p09`), and headings (`p13`: `+ head _` claimed by `Heading` earlier) do not trigger `Break`.
  - Doubled `a _ _\nb` (`p05`) matches the second space, rendering `<p>a _<br />\nb</p>`.
- **Corrections**: None. Both `Parse/Default/Break.php` and `Render/Xhtml/Break.php` are unchanged.
- **R3 stage consequence**: None (R3.15 unaffected).
- **ftml candidates**: None.
- **Verdict**: `VALIDATED`
