# CORRECTION C-SUSPECT-INTERACT-1 — Collapsible label apostrophes (REFCORR3 lane, 2026-11-22)

Status: APPLIED in this tree by adoption of the SUSPECT-INTERACT lane's corrected renderer. Render/Xhtml/Collapsible.php's wikidotLabel escaped labels with htmlspecialchars(..., ENT_QUOTES), so an authored apostrophe in a show or hide label served as &#039; where live serves the raw quote. The divergence was confirmed with a fresh live capture in the SUSPECT-INTERACT lane (REPORT-SUSPECT-INTERACT.md, conformance-suspect-interact/CANDIDATES.md and CORRECTION.md).

## The settling evidence (fresh live probe, valid, stable, and saved-source-matching)

Probe muse-probe-suspect-interact-c1-coll-apostrophe, source [[collapsible show="it's" hide="don't"]]\nX\n[[/collapsible]], captured twice anonymously on sandbox-for-codex (capture html_sha256 ee0c4cf8b359efaad12f0bfdd695707e302b5f3cd6f9f706210e6b9dd58ab001). The reference served it&#039;s and don&#039;t; live served it's and don't. Earlier batteries missed it because their normalization decodes numeric &#\d+; entities. The control probe muse-probe-suspect-interact-x3-div-raw-numeric ([[div style="color:a&#039;b"]] serving <div style="color:a&amp;#039;b">) rules out a Stage-2 entity decode, and there is no single-escaped &#039; anywhere in the conformance-refphp rules.

## The correction (reference)

Render/Xhtml/Collapsible.php only: the single call htmlspecialchars($text, ENT_QUOTES, 'UTF-8') becomes htmlspecialchars($text, ENT_COMPAT, 'UTF-8'), with an explanatory comment. The ordered replacement passes after the call are untouched, so the default labels '+ show block' and the en-dash hide label — which contain no apostrophe — keep their exact +&nbsp;show&nbsp;block and [0xE2,0x80,0x93] ++ &nbsp;hide&nbsp;block bytes. The before-copy is ref-php/text-wiki/Text/Wiki/Render/Xhtml/Collapsible.php.before-refcorr3, SHA-256 21b021f9ac414350a55c62398dcd493b52bc30b4cf17ef4f74415adcc4775871, byte-identical both to this tree's file as found and to the lane's conformance-suspect-interact/Collapsible.php.before-suspect.php. The corrected file's SHA-256 is 459be186cfd628267cb86f3f4691a9f9c25e097f45311386e68cad170c7be900.

## Firsthand verification (REFCORR3 lane, 2026-11-22)

The corrected reference renders the probe's labels as it's and don't, byte-identical to the live capture. The r46 family corpus carries exactly one apostrophe-spelled collapsible case (collapsible/c31-single-quotes) whose frozen state has args: [] and therefore uses the two defaults, and conformance-r46/family-renders-full.jsonl contains no &#039; at all, so C1 produces zero movement in the r46 family, notes and prose gates; any movement there would be unexplained. The notes/prose controls and the r46 family gate re-run are tallied in REPORT-REFCORR3.md.

## Mirror consequence

lean-ftml/LeanFtml/InteractiveRules.lean's wikidotLabel switches from htmlSpecialCharsQuotes to htmlSpecialCharsCompat, and its doc comment follows. lean-ftml/LeanFtml/InteractiveRender.lean re-points the five R4.6 default-label theorems (collapsible_label_default_show, collapsible_label_default_hide, collapsible_start_default, collapsible_start_unfolded, collapsible_end_bottom) plus collapsible_label_spaces and their private escape helpers to the ENT_COMPAT identities; the pinned bytes do not change, but a new characterization theorem pins the apostrophe case. The r46 family gates are re-run; see REPORT-REFCORR3.md.
