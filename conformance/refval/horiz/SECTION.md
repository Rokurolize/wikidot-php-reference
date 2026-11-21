# Rule 1: Horiz (`----`, pipeline pos 31, R3.15)

- **Battery**: 88 cases (`refval/horiz/battery.jsonl`: 45 R3.15 `hz-*` authored + 17 R3.15 canonical + 8 extension cases `hz-x01`..`hz-x08` + 18 live probe cases `p01`..`p18`).
- **Live probes**: 18 pages `muse-probe-refval-horiz-p01` through `muse-probe-refval-horiz-p18` on `sandbox-for-codex`. All 18/18 validated (`valid=true`, `stable=true`, `saved_source_matches=true`).
- **Reference vs. live comparison** (`refval/horiz/compare-before.txt`):
  - 9/18 trim-equal (`p01`, `p05`–`p10`, `p13`, `p18`), 12/18 frame-normalized equal (`p02`, `p03`, `p17` differ only in inter-block `\n\n` vs `\n` and trailing `\n\n`).
  - Remaining 6/18 (`p04`, `p11`, `p12`, `p14`, `p15`, `p16`) all match live on `Horiz` behavior and differ solely on previously classified Stage 2 / serving-layer pretty-printing framing surfaces:
    - `p04` (`x\n---\n--\n-\ny`): `Horiz` does not fire; only difference is `Newline` `\n` before `</span>` (`<br />\n</span>` vs `<br /></span>`, Stage 2 `libtidy`).
    - `p11` (`* one\n----\n* two`), `p12` (`|| a || b ||\n----\n|| c || d ||`), `p16` (`@@\n----\n@@`): Stage 2 pretty-printing newline before `<hr />` (`</ul><hr />` vs `</ul>\n<hr />`, `</table><hr />` vs `</table>\n<hr />`, `@@<hr />` vs `@@\n<hr />`; F-R2-58 family).
    - `p14` (`> quote\n----\nx`): Stage 2 pretty-printing inside `<blockquote>` (`<blockquote><p>` vs `<blockquote>\n<p>`).
    - `p15` (`[[div]]\n----\n[[/div]]`): Stage 2 `Div` `<div >` space and pretty-printing (`<div ><hr />\n</div>` vs `<div>\n<hr /></div>`).
- **What live confirms**:
  - Four or more ASCII hyphens (`/^([-]{4,})$/m`) on their own line render `<hr />`, breaking paragraphs (`p02`, `p03`, `p17`), lists (`p11`), tables (`p12`), and blockquotes (`p14`).
  - Runs of 1–3 hyphens (`p04`), trailing space (`p05`), trailing tab (`p06`), leading space (`p07`), non-hyphen neighbors (`p08`), and Unicode dashes `————`/`––––` (`p18`) do not match `Horiz`.
  - Protected inside `[[code]]`, NOT protected across multi-line `@@\n----\n@@` (`p16`).
- **Corrections**: None. Both `Parse/Default/Horiz.php` and `Render/Xhtml/Horiz.php` are unchanged.
- **R3 stage consequence**: None (R3.15 unaffected).
- **ftml candidates**: None.
- **Verdict**: `VALIDATED`
