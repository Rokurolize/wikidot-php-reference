# Rule 6: Divprefilter (`[[/div]]\s*[[div`, pipeline pos 25, R3.16)

- **Battery**: 80 cases (`refval/divprefilter/battery.jsonl`: 45 R3.16 `dp-*` authored + 1 R3.16 canonical `sz70-size-crosses-div` + 16 extension cases `dp-x01`..`dp-x16` + 18 live probe cases `p01`..`p18`).
- **Live probes**: 18 pages `muse-probe-refval-divprefilter-p01` through `muse-probe-refval-divprefilter-p18` on `sandbox-for-codex`. All 18/18 validated (`valid=true`, `stable=true`, `saved_source_matches=true`).
- **Reference vs. live comparison** (`refval/divprefilter/compare-before.txt`):
  - 1/18 exact (`p16`), 6/18 trim-equal (`p09`, `p10`, `p14`, `p15`, `p16`, `p17`).
  - Remaining 12/18 (`p01`–`p08`, `p11`–`p13`, `p18`) all agree with live on `Divprefilter` behavior and differ solely on Stage 2 `Div` `<div >` / pretty-printing newlines (`p01`–`p08`, `p11`–`p13`) or Stage 2 `libtidy` cloning `<span style="font-size:larger;">` across `<div>` boundaries (`p18` / `sz70-size-crosses-div`, recorded G2.2).
- **What live confirms**:
  - Whitespace (spaces, tabs, single/multiple newlines) between `[[/div]]` and `[[div` is collapsed completely before `Div` and `Newline` run, preventing any `<br />` or `<p>` between adjacent `<div>` blocks (`p01`–`p08`, `p13`, including attributes `[[div class="b"]]` and scored `[[div_]]`).
  - Non-whitespace between divs (`p11`: `x`) and non-div followers (`p12`: `[[span]]`) do not trigger `Divprefilter`, leaving `x` / `<br />` intact.
  - Case-insensitive matching rewrites to literal lowercase `[[/div]][[div` (`p09`: `[[/DIV]]\n[[DIV]]` -> `<p>[[/div]][[div]]</p>`; `p10`: `[[/Div]] [[dIv]]` -> `<p>[[/div]][[div]]</p>`).
  - Matches the bare `[[div` prefix regardless of what follows: `[[/div]] [[divx]]` -> `<p>[[/div]][[divx]]</p>` (`p14`), `[[/div]] [[div` -> `<p>[[/div]][[div</p>` (`p15`), and inline `[[div]]a[[/div]] [[div]]b[[/div]]` -> `<p>[[div]]a[[/div]][[div]]b[[/div]]</p>` (`p17`).
- **Corrections**: None. Both `Parse/Default/Divprefilter.php` and `Render/Xhtml/Divprefilter.php` are unchanged.
- **R3 stage consequence**: None (R3.16 unaffected).
- **ftml candidates**: None.
- **Verdict**: `VALIDATED`
