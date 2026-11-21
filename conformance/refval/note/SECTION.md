# Rule 8: Note (`[[note]]\n...\n[[/note]]`, pipeline pos 41, R3.16)

- **Battery**: 82 cases (`refval/note/battery.jsonl`: 42 R3.16 `nt-*` authored + 1 R3.16 canonical `lb35` + 19 extension cases `nt-x01`..`nt-x19` + 20 live probe cases `p01`..`p20`).
- **Live probes**: 20 pages `muse-probe-refval-note-p01` through `muse-probe-refval-note-p20` on `sandbox-for-codex`. All 20/20 validated (`valid=true`, `stable=true`, `saved_source_matches=true`).
- **Reference vs. live comparison** (`refval/note/compare-before.txt`):
  - 2/20 exact (`p04`, `p05`), 3/20 trim-equal (`p04`, `p05`, `p08`), 5/20 frame-normalized equal (`p16`, `p17`).
  - Remaining 15/20 (`p01`–`p03`, `p06`–`p07`, `p09`–`p15`, `p18`–`p20`) all agree with live on `Note` parsing and `<div class="wiki-note">...</div>` rendering, differing solely on Stage 2 pretty-printing newlines inside/around `<div class="wiki-note">` (`p01`–`p03`, `p06`–`p07`, `p09`–`p12`, `p14`–`p15`, `p18`–`p20`) or Stage 2 `libtidy` unwrapping `<p>a <div class="wiki-note"></p>` (`p13`).
- **What live confirms**:
  - Pattern `/(\n)?\[\[note\]\]\n(.*?)\[\[\/note\]\]/msi` matches case-insensitively (`p10`, `p11`), requires a newline immediately after `[[note]]` (`p08`: `[[note]] body\n[[/note]]` stays literal), and does not require a newline before `[[/note]]` (`p09`: `[[note]]\nbody[[/note]]` matches).
  - Optional leading newline is doubled to close the preceding paragraph without `<br />`, while no trailing newline is emitted after `$end`, leaving `y` in `x\n[[note]]\nbody\n[[/note]]\ny` as `<br />\ny` (`p02`, `p14`).
  - Non-recursive: nested `[[note]]\n[[note]]\ninner\n[[/note]]\n[[/note]]` closes at the first `[[/note]]`, leaving the inner opener and trailing closer literal (`p12`).
  - Empty notes (`p04`, `p05`) render `<div class="wiki-note"></div>`.
  - No attributes (`[[note class="x"]]`), no scored form (`[[note_]]`), and no trailing spaces in tags (`[[note]] `, `[[/note ]]`) are accepted (`p16`, `p17`).
  - Lists (`p18`), inline formatting + typography (`p19`), and divs (`p20`) parse normally inside the note body.
- **Corrections**: None. Both `Parse/Default/Note.php` and `Render/Xhtml/Note.php` are unchanged.
- **R3 stage consequence**: None (R3.16 unaffected).
- **ftml candidates**: None.
- **Verdict**: `VALIDATED`
