# CORRECTION C-SUSPECT-XRULE-4 — unforgeable NUL Toc sentinel replaces the authorable umlaut pair (REFCORR4 lane, 2026-11-22)

Status: APPLIED in this tree. Live serves authored `üü**x**üü` as `<p>üü<strong>x</strong>üü</p>` and `üüplainüü` as `<p>üüplainüü</p>` while the reference stripped everything between authored pairs; an authored pair in a Toc heading also corrupted the entry. Probes muse-probe-suspect-xrule-x20-ustrip, -x39-ustrip-plain and -x31-toc-ustrip are valid, stable and saved-source-matching in conformance-suspect-xrule/captures-b12.json, captures-b5.json and captures-b34.json. This correction discharges C-SUSPECT-RAWHEAD-5, whose adjudication in conformance-refphp/formraw/ADJUDICATION-CSUSPECT-RAWHEAD-5.md costed exactly this two-file sentinel change as the minimal robust fix.

## The correction (reference)

Render/Xhtml/Toc.php item_start and item_end and Text/Wiki.php's post-render strip pass now share a NUL-pair sentinel that cannot pass the live save layer, while strip_tags still applies to each label between the renderer's own sentinels. This tree's Text/Wiki.php also carries R-UFFFD-1's renderLiteralUfffdRecovery method and dispatch, which were preserved by the merge rather than overwritten with the sibling lane's older file. Byte-identical predecessors Render/Xhtml/Toc.php.before-refcorr4 (SHA-256 7b296aca63b38d6eafa3058aede77c14734eaf4ca441cd7fee67e612bfb82f22) and Text/Wiki.php.before-refcorr4 (SHA-256 dc247e5ea927cc6cf47a082dfb7b6121b22453226458cd3a3ac4d00ada999385); corrected SHA-256 7777246b95c3263f78e61100c8a34b2de743fa87e5d96c41dffc632bfadd2ddb and bc0a782996a35e977383f0d226b7614bc1e6ef17da651b25866577be35f93231.

## Firsthand verification

x20 and x39 match live byte-for-byte; x31's Toc label and heading now carry Grüüße intact, with only the documented Stage 2 table-tag newline framing still differing at frame level, exactly as in the sibling lane's own after-capture. The 56-case Toc battery is byte-identical before and after (SHA-256 7c474c41710c4cf3ec73c144f46ff3551fb26b52c691f7b679411904cee050e8 on both sides, empty stderr), and the smoke battery stays 9/9.

## Mirror consequence

lean-ftml/LeanFtml/RenderCore.lean tocStripDelim is now four NUL bytes and findTocDelim/postStripToc match NUL pairs; postStripToc_go_no_nul and postStripToc_no_nul replace the old no-0xC3 theorems, NotesRender's helper is restated to postStripToc_of_all_no_nul at its five call sites, Main.lean's axiom-audit name is updated, and the symbolic RawHeadingRules.renderToc emission plus RawHeadingRender theorems remain valid against the new constant.
