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
- **Include: corrected and validated.** The fossil's regex scanner was replaced with a hand scanner implementing the adjudicated grammar (line-start anchoring, quoted-include consumption, the argument grammar), and a reference-resolution layer was added (normalization, site handling, cross-site fetch). Against ftml it agrees on 101 of 114 differential grid cases textually and on all 114 modulo padding and includer-surface differences; its argument substitution fold matches live behavior on all 14 probed cases, including the cases where ftml itself diverges (recorded as findings in the proof loop's gap ledger).
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
