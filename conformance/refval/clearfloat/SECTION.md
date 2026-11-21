# Rule 5: Clearfloat (`~~~~`, `~~~~>`, `~~~~<`, pipeline pos 33, R3.15)

- **Battery**: 80 cases (`refval/clearfloat/battery.jsonl`: 46 R3.15 `cf-*` authored + 1 R3.15 canonical `toc74-clear-float` + 15 extension cases `cf-x01`..`cf-x15` + 18 live probe cases `p01`..`p18`).
- **Live probes**: 18 pages `muse-probe-refval-clearfloat-p01` through `muse-probe-refval-clearfloat-p18` on `sandbox-for-codex`. All 18/18 validated (`valid=true`, `stable=true`, `saved_source_matches=true`).
- **Reference vs. live comparison** (`refval/clearfloat/compare-before.txt`):
  - 9/18 trim-equal (`p01`–`p03`, `p07`–`p12`), 12/18 frame-normalized equal (`p04`–`p06` differ only in `\n\n` vs `\n`).
  - Remaining 6/18 (`p13`–`p18`) all agree with live on `Clearfloat` parsing and exact `<div style="clear:...; height: 0px; font-size: 1px"></div>` output, differing only on Stage 2 pretty-printing / `libtidy` framing surfaces:
    - `p13` (`[[toc]]~~~~\n\n+ A`): exact `Clearfloat` match; only `Toc` `<table>` internal pretty-printing differs.
    - `p14` (`[[div]]\n~~~~>\n[[/div]]`): Stage 2 `Div` `<div >` and pretty-printing.
    - `p15` (`* item\n~~~~\n* item2`), `p16` (`|| a ||\n~~~~\n|| b ||`), `p17` (`@@\n~~~~\n@@`): Stage 2 pretty-printing newline before `Clearfloat` `<div>` (F-R2-58 family).
    - `p18` (`a _\n~~~~\nb`): `Clearfloat`'s `"\n\n"` head prevents a second `<br />` (unlike `Horiz`/`Separator`), matching live's single `<br />`; only Stage 2 `libtidy` removing `\n` in `<p>a<br />\n</p>` -> `<p>a<br /></p>` differs.
- **What live confirms**:
  - Four or more `~` with optional `>` or `<` on their own line (`/^([~]{4,})(>|<)?$/m`) render `<div style="clear:both; height: 0px; font-size: 1px"></div>`, `clear:right`, or `clear:left` respectively (`p01`–`p07`, `p11`–`p12`).
  - Fewer than 4 tildes (`p08`), doubled/extra side markers `~~~~>>`/`~~~~><`/`~~~~>x` (`p09`), internal/trailing/leading spaces (`p10`) do not match.
  - Protected inside `[[code]]`, NOT protected across multi-line `@@\n~~~~\n@@` (`p17`).
- **Corrections**: None. Both `Parse/Default/Clearfloat.php` and `Render/Xhtml/Clearfloat.php` are unchanged.
- **R3 stage consequence**: None (R3.15 unaffected).
- **ftml candidates**: None.
- **Verdict**: `VALIDATED`
