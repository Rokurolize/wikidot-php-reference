# R2 frame rules: Prefilter and Delimiter (2026-11-20)

The two pipeline-frame rules ahead of the content rules in the fossil's order (Include, Prefilter, Delimiter, Code, ...), corrected against live. Evidence: probe page muse-probe-r2f-frame1 on sandbox-for-codex.wikidot.com (captures.json in this directory's frame/ folder; valid, stable, saved_source_matches=true), carrying a tab in flow text, a code block with a tab and three blank lines, the sequence üü, and the character ÿ (U+00FF). Reference side: transform.php render on the identical source (frame/ref-render.html before the correction, frame/ref-render2.html after).

## Prefilter verdicts, transformation by transformation

- Line endings \r\n and \r to \n: handled at the harness input stage (see R2-INCLUDE.md C1); the in-pipeline Prefilter copy of the conversion is redundant there and stays as the fossil has it. CONFIRMED by the Include stage's CR grid cases.
- Tab expansion to 4 spaces: CONFIRMED on live inside the code block (rendered bytes "line2    tabbed"). In flow text, live's paragraph shows the tab as ONE space where the reference keeps the expanded four; see "open frame items" below.
- Whitespace-only lines emptied: not probed in this round; no verdict.
- 3+ newline runs compressed to 2: CONFIRMED on live inside the code block (three blank lines in the source render as one blank line, bytes "line1\n\nline2").
- Prepend \n / append \n\n: frame shaping, part of the output-shaping difference below.
- üü stripping: REFUTED by live. The fossil removed the sequence utf8_encode("\xFC") twice from the source; live renders "UU-START üü UU-END" with the sequence intact. CORRECTED in the reference: the strip is removed from Prefilter.php (comment records the probe), and the re-render confirms the sequence now survives; the smoke battery re-ran clean after the change.

## Delimiter disposition

The rule tokenizes literal \xFF bytes in the source so they cannot forge token boundaries; it is a guard for Text_Wiki's byte-oriented token encoding. In the UTF-8 era it has no observable counterpart: typed text cannot contain a raw 0xFF byte, and the nearest typed character ÿ (U+00FF) renders as itself on live (probe) and in the reference. ftml has no such mechanism (AST, no delimiter bytes). Disposition: mechanism understood, kept as the fossil has it, no differential owed.

## Open frame items (recorded, not corrected here)

- Paragraph space-run collapse: live renders flow-text "word1<TAB>word2" as "word1 word2" (one space); the reference's Stage 1 output keeps the four expanded spaces. Leading candidate home is Stage 2 (WikiTransformation::purifyHtml, the libtidy pass of the 2026-11-04 two-stage ruling), which the reference does not implement yet; that is Tier 2 (G2.2) territory, not a Prefilter correction.
- Output shaping: the reference joins blocks with extra blank lines and trailing newlines where live's output is tight ("<p>...</p>\n<div..."), and the code block's wrapper differs by one newline ('<div class="code">\n <pre>' on live vs '<div class="code"><pre>' in the fossil render). The joining belongs to the Tighten rule and post-render handling; the wrapper newline belongs to the Code render rule's own R2 turn.

Closure (2026-11-20): the code wrapper newline item above is settled by the Code stage (conformance-refphp/R2-CODE.md, correction C5): live emits '<div class="code">\n<pre>' for plain blocks and the matching newlines inside highlighted blocks, and the reference's Code render rule now emits that shape. The remaining output-shaping item (block joining and trailing newlines) stays with Tighten and post-render handling in Tier 2.
