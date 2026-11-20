# wikidot-php-reference

A standalone, runnable PHP reference implementation of Wikidot's wikitext parser, behavior-corrected rule by rule against the live Wikidot service. It exists to serve as an executable specification of how live Wikidot actually parses wikitext: the corrections are not taken from the old source code's authority but are validated, one rule at a time, against live behavior, with the differential evidence kept in `conformance/`.

This repository is a snapshot publication. Development happens in the ftml Lean equivalence proof loop's working copy (the loop proves, in Lean, that the Rust parser [ftml](https://github.com/Rokurolize/ftml) matches Wikidot's parsing semantics); tagged snapshots are pushed here as correction stages complete.

## Provenance and a warning

The code derives from the Wikidot 1 open-source release (mirrored at [gabrys/wikidot](https://github.com/gabrys/wikidot)), principally its vendored Text_Wiki library, which applies roughly 70 parse rules in sequence. That upstream code is a fossil from the late 2000s and early 2010s: it is the skeleton of this reference, never evidence for how the live service behaves today. Several fossil behaviors have already been refuted by live probes during correction (the Include rule's scanner shape, its reference resolution, and Prefilter's character stripping among them). Trust a rule in this tree as live behavior only where the status table below says it has been corrected and validated. This project is not affiliated with Wikidot.

## Layout

- `text-wiki/`: the working copy of the Text_Wiki library (parse and Xhtml render rules), modernized to run on PHP 8 and corrected per the status table.
- `wikidot-root/`: the minimal reconstructed runtime root the library expects (WDStringUtils, Text_Highlighter, a small PEAR shim, parser configuration).
- `harness/`: command-line drivers. `transform.php` renders wikitext from stdin to Xhtml (or dumps the parse-phase token array). `batch.php` is a JSONL batch driver with three modes: `expand` (Include rule only, the expansion-level view), `render` (full pipeline), and `tokens`. Pages are served from an in-memory map in `harness/pages.php` through the stubs in `harness/ozone-stubs.php`; no database or web server is involved.
- `conformance/`: the differential records behind every correction (inputs, live captures, result catalogs).
- `docs/INVENTORY.md`: the correction plan and per-phase record. `docs/r1-compat.patch`: the mechanical PHP 8 compatibility patch that made the fossil runnable, kept for provenance.

## Correction status

- **R1, runnable skeleton: done.** The fossil runs on PHP 8.5 with only mechanical, semantics-preserving edits (constructor renames, by-value `process()` signatures, bracket string offsets), plus one flagged era-semantics bridge in the Xhtml render pre-pass (ENT_SUBSTITUTE) whose adjudication is recorded as an open item.
- **Include: corrected and validated.** The fossil's regex scanner was replaced with a hand scanner implementing the adjudicated grammar (line-start anchoring, quoted-include consumption, the argument grammar), and a reference-resolution layer was added (normalization, site handling, cross-site fetch), including the completed live resolution rule for colon-edge targets (a character-set gate on page names and on a site pair's page segment, measured across 31 probed shapes). Its argument substitution fold matches live behavior on all 14 probed cases. In the final three-way differential over a 119-case grid, the reference and ftml agree on 104 cases textually and on all but the includer-surface cases in disposition, with zero resolution divergences in either direction.
- **Code: corrected and validated.** The parse rule needed no behavioral correction. The Xhtml render rule took five corrections: instantiating the syntax highlighter factory (the fossil's static call is a fatal error on PHP 8), a bare wrapper element for empty bodies, a line-wise body trim that keeps first-line indentation (with NBSP served as a regular space), PHP 4/5-era escaping defaults (apostrophes stay literal), and the newline live emits after the wrapper's opening tag. The corrected rule's rendered code fragments are byte-identical to live captures on all 15 probed cases, highlighted output included, and match all 37 in-scope ftml corpus pins.
- **Iftags, Comment, Iframe, Date, Math: corrected and validated.** Iftags tag comparison is now case-insensitive, as live is. Comment keeps an indented comment alone on a whitespace-only line from collapsing the line structure. Iframe lost a stray space before the closing bracket of its tag, percent-encodes non-ASCII source bytes, strips line breaks from a greedy source tail, and leaves single quotes literal. Date now emits live's odate span shape with canonical classes, accepts negative timestamps, and renders blank values as nothing. Math's \include/\input guard compiles again under modern PCRE and an immediately adjacent closer terminates the block. Twelve divergences in ftml were cataloged along the way (comment/iftags pairing, iframe tail and quoting, iftags spec splitting, date blanks, math attribute keys, and one math guard case live's save filter would not let us probe).
- **Modulepre, Module, Module654: corrected and validated.** Modulepre (the prefilter that rewrites line-start [[module654]] openers to [[module]] before block matching) needed no correction; live confirms the fossil's rewrite, name charset, and claiming behavior. Module's unknown-module error block now carries live's current wording ("No such module, please check available modules and fix this page", settled byte-for-byte by probes), and an empty module body no longer consumes its [[/module]] closer. Module654 now claims an opener with trailing spaces before its newline, as live does. The stage also cataloged six places where ftml diverges from live (module name validation, the missing prefilter rewrite, trailing-whitespace openers, a rel attribute on the error link, empty-body closer consumption, and module body ownership). Module evaluation itself (what ListPages or Rate compute) is a serving-layer concern, out of scope here.
- **Form, Raw, Rawold: corrected and validated.** Raw's parse rule was rewritten as a scanner implementing live's run arithmetic for adjacent @ signs (runs vanish, leave literals, or form a raw span, including the cross-line forms), and its render rule now emits live's pre-wrap span with the Wikidot raw escape table (spaces as &#32;, apostrophes literal). Rawold (the double-backtick raw form) needed no correction. Form's fossil backend is absent from the snapshot and fataled; live renders a matched [[form]] block on an anonymous page view as literal source text, and the rule now reproduces that display shape (the interactive form itself is a serving-layer concern). The corrected rules match all 24 non-surface live probes byte-for-byte; the stage also cataloged five places where ftml itself diverges from live (no Rawold rule, no [[form]] rule, apostrophe escaping in raw spans, a link-boundary interaction, and an angle-raw extension live does not have).
- **Prefilter: corrected in part.** Its tab expansion and newline compression are confirmed live; its stripping of a specific two-character sequence was refuted by a live probe and has been removed.
- **Delimiter: dispositioned.** It guards the library's byte-oriented token encoding against forged delimiter bytes, which typed UTF-8 text cannot contain; it has no observable behavior and no counterpart in ftml.
- **Every other rule: fossil form.** Not yet validated against live behavior. Expect divergences.

## Running it

Requires PHP 8 (developed and tested on PHP 8.5). From the repository root:

```
php harness/transform.php render < page.wikitext
printf '%s\n' '{"id":"x","source":"Hello **bold** world."}' | php harness/batch.php render
```

## Licenses

This is a mixed-license tree and the per-file headers govern. The Wikidot-derived code is under the GNU Affero General Public License v3 (`LICENSE.txt`). The Text_Wiki library is under the GNU Lesser General Public License v2.1 (`LICENSE-LGPL-2.1.txt`). New material in `harness/` and `docs/` is Copyright (c) 2026 Rokurolize and is distributed under AGPLv3.
