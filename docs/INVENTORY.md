# Reference-PHP spec layer — inventory and plan (2026-11-20)

Owner direction (2026-11-20): rather than assembling the expected semantics per family from empirical measurements alone (and modelling ftml, whose design philosophy differs from Wikidot's), build a PHP implementation that fully reproduces live Wikidot's behavior, by updating the fossil Text_Wiki source to current live behavior, and take the Lean formalization from there.

## Why this fits (the G1.4b lesson)

Live Wikidot's parser is a sequential rule pipeline: an ordered list of rules, each transforming the text/token stream. Behaviors that look arbitrary from ftml's AST-first design fall straight out of that architecture. Exhibit A, measured before this direction was given: live include argument substitution is a sequential fold (loop record conformance-g14b, rules X1-X4), and the fossil's own Include rule (lib/Text_Wiki/Text/Wiki/Parse/ Default/Include.php line 128) does exactly that:

    foreach($subsArray as $sub){ ...
        $output = str_replace('{$'.$var.'}', $value, $output);

ftml's map-based resolve_include_arguments was the design philosophy mismatch, and it produced finding F-G14B-1. A spec layer in the original architecture makes the natural behavior the default instead of a per-family discovery.

## What the fossil is (and is not)

Cloned 2026-11-20: github.com/gabrys/wikidot at ref-php/fossil/ (the whole OZONE application; Text_Wiki vendored at lib/Text_Wiki/). STANDING CAVEAT, unchanged from the 2026-11-02 ruling: the fossil is a SKELETON, never behavior evidence. Every rule's fossil form is a hypothesis. The reference implementation earns trust only through differential validation against live behavior, in the loop's evidence order (pins, frozen captures, live probes; fetch once, cache, reuse).

## Inventory facts (read firsthand 2026-11-20)

- Parse rules on disk: lib/Text_Wiki/Text/Wiki/Parse/Default/ has 78 rule files (Anchor ... Wikilink).
- The applied pipeline: Text/Wiki.php line 52, `public $rules`, lists the parse rules IN APPLICATION ORDER; about 70 are active (a handful are commented out in the fossil: Moduledelimiter, Function, Html, Phplookup, Wikilink, Bold, Italic). First rule: Include. Notable order landmarks: Code/Form/Raw early (protected regions), Module, Iftags, Comment, Math, Footnote family, Blockquote/Heading/Toc, Span/Size/Div/Collapsible/ Tabview, List/Deflist, Table/Tableadv, Image, Newline, Paragraph, then the inline family (Url, Email, Mathinline, Interwiki, Colortext, Strong, Emphasis, Underline, Strikethrough, Tt, Superscript, Subscript), Typography, Tighten last.
- Render rules: Render/Xhtml/ has 84 rule files (one per token type, roughly).
- Pipeline frame: php/utils/WikiTransformation.php drives it (`new Text_Wiki()` with the default rule list, line 276; `purifyHtml` at line 59 is the Stage 2 of the 2026-11-04 two-stage ruling; the same file carries the %% template variable layer and ListPages template assembly, which are deepwell-side concerns, not parse semantics).
- The code is PHP 4/5 era (var-less public properties, eponymous constructors); running it on a current PHP needs a compatibility pass before any behavior work.

## Plan

Phase R0 (inventory, this document): fossil layout, rule order, pipeline frame. DONE 2026-11-20.

Phase R1 (runnable skeleton): extract lib/Text_Wiki standalone, shim it onto the WSL's current PHP, and drive it from a CLI harness (wikitext in, token stream and XHTML out). No behavior changes yet; the fossil's divergences from live are expected and are the work list, not a surprise.

Phase R2 (behavior correction, rule by rule): for each rule in application order, differential-test the reference against live (sandbox probes per rule family, the corpus pins, and the frozen render pool at scale), and update the PHP until the differential is clean or every remainder is a recorded finding. This is the same adjudication discipline the loop already uses, concentrated on one executable artifact.

Phase R3 (Lean from the reference): the Lean spec layer mirrors the PHP pipeline: one Lean function per rule over an explicit token-stream state (the Tree.lean AST grows into the token model the parse phase actually produces), proved rule by rule, with bridge-A differentials (Lean vs PHP-ref on generated inputs, PHP-ref vs ftml through the render/AST comparison the existing harnesses provide).

## Open design question for R1/R3

The interface the Lean proof targets. Text_Wiki's parse phase produces a token array interleaved with text; ftml produces an AST. The natural candidate is the token stream after the parse phase (before Xhtml rendering), with a defined correspondence to ftml's AST per construct. Settling this is R1's main design deliverable. The loop's parse-only scope (SPEC-LAYER-PROPOSAL Q2) is unchanged; rendering stays out of the proof, and the PHP-ref is validated at render level only as an oracle for its parse behavior (the frozen-pool method).

## What does not change

- Tier 1 results stand: G1.1, G1.2, G1.3, G1.4, G1.4b are ftml-vs-live statements with their own evidence; the include family's adjudicated rules (S/G/Q/R/X in GRAMMAR-INCLUDE.md) become early validation targets for the reference's Include rule, not discarded work.
- G1.5/G1.6 are ftml-internal machines with no Text_Wiki counterpart; they proceed as planned, independent of R1-R3.
- Tier 2 (the two-stage inline scope model) maps directly onto this pipeline: Stage 1 is the Text_Wiki parse phase, Stage 2 is purifyHtml. The reference makes Tier 2 a mirroring task instead of a reconstruction.
- Findings discipline unchanged: a live-vs-reference divergence updates the reference; a live-vs-ftml divergence is a numbered finding routed as before. The reference never silently redefines the spec: its claim to spec status is exactly its differential record against live.

## R1 DONE (2026-11-20): runnable skeleton

Working copy: ref-php/text-wiki/ (the fossil's lib/Text_Wiki, 768K) plus ref-php/wikidot-root/ (reconstructed OZONE root: lib/Text_Highlighter copied from the fossil, lib/WDStringUtils.php copied from fossil php/utils/, lib/PEAR.php minimal shim, tmp/math, conf/wikiparser) and ref-php/harness/ (transform.php CLI: stdin wikitext, `render` prints Xhtml, `tokens` prints the parse-phase token array as JSON; wiki-config.php mirrors WikiTransformation::resetWiki page mode; ozone-stubs.php provides Ozone::getRunData, DB_PagePeer backed by an in-memory page map, RefPage/RefSite, _(), mkdirfull(), and a no-op LatexRenderer). Runs on the WSL's PHP 8.5.4 at ~/.local/state/wikijump/muse-bhl/lean-ftml-refphp/ (tar-pipe sync from the VM record). All 167+ PHP files lint clean.

Compatibility edits (mechanical, semantics-preserving; full record in ref-php/r1-compat.patch, 81 files):
- 4 eponymous constructors renamed to __construct (Text_Wiki, Text_Wiki_Parse, Text_Wiki_Render, the Embed render rule) and 7 per-rule parse constructors (Wikilink, Url, Smiley, Moduledelimiter, Image, Freelink, Delimiter), whose bodies PHP 8 would otherwise have silently skipped, plus their parent:: constructor calls. This was the one silent-divergence class: e.g. the Delimiter rule's regex is set in its constructor.
- process() signatures unified to by-value: the base declared &$matches and 72 rules copied it, but the ONLY invocation path is preg_replace_callback (base Text_Wiki_Parse::parse), which passes by value; PHP 8 makes the mismatch fatal. 75 sites. Footnoteblock and Bibliography already declared by-value in the fossil, consistent with their own callback parse()s.
- 13 curly-brace string offsets to bracket form; 1 call-time pass-by-reference removed (preg_match_all in Module.php; the callee declares the parameter by-reference itself).
- Wiki.php's two WIKIDOT_ROOT requires made __DIR__-relative.
- One era-semantics bridge, FLAGGED for R2 adjudication: Xhtml render pre() ORs ENT_SUBSTITUTE into the htmlentities flags. Without it PHP >= 5.4 returns '' for the parsed source (it always contains the \xFF token delimiter, invalid UTF-8); the fossil era passed such bytes through. User-text invalid byte handling under this bridge is an open R2 question.
- One PHP-era guard: Footnoteblock reads vars['footnotes'] with ?? array() (PHP 5 count(null) == 0; PHP 8 TypeError).

Smoke battery (conformance-refphp/smoke/, 9 cases, all render with no fatals): paragraphs/bold/italic, heading, list, table, code block, collapsible, div, blockquote, footnote + footnoteblock, freelink (via the page-existence stub), include (via the page-map stub: the G1.4 target page is fetched and spliced), block math (via the fossil's own LaTeX-unavailable error path). Parse produces 68 active rules' worth of tokens; the delimited source uses \xFF as the token delimiter.

Two R2 observations already on record:
- The fossil Include rule differs from ftml's scanner in shape: line-anchored regex with a narrow page-name charset, and parse() recurses the substitution up to 5 levels inline (ftml's include() is one pass; recursion is the caller's). Which parts match live is adjudication work, with the G1.3/ G1.4 grammar (GRAMMAR-INCLUDE.md) as the live-derived baseline. Its substitution fold and guards (non-empty value, static key regex with /i) do match the adjudicated X1-X4.
- CORRECTED 2026-11-20 (R2): the unset-{$marker} disappearance reported in the first R1 draft was a harness bug, not a rule: transform.php's original hardcoded page map held the target text in a PHP double-quoted string, so PHP interpolated {$marker} away before the pipeline ran. A rule-prefix bisection (harness/rule-bisect.php) shows the placeholder survives all 68 parse rules, and with the shared page map (harness/pages.php, escaped literals) it survives the full render too, matching live. No rule consumes it.
