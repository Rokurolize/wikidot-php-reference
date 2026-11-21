# G1.4b argument-expression adjudication — RESULTS (2026-11-20)

Question: what does LIVE Wikidot do with `{$name}` references inside include arguments (values and keys), and does ftml's `resolve_include_arguments` (src/includes/parse.rs: bounded recursive map expansion, key expansion, self-reference blocking, fallback dropping) match it?

Method: 14 probe pages on sandbox-for-codex.wikidot.com (kept in place), target `muse-probe-g14b-target` with source "A is {$a}.\nB is {$b}.\nM is {$marker}.\nTARGET-END". Live side: wikidot-probe captures (all valid, saved_source_matches=true); e1 additionally re-verified by a direct anonymous curl. ftml side: the G1.4 Rust dumper (real public include() at 0a96f564e, target in its page map). Inputs: conformance-g14b/inputs.jsonl. Captures: evidence/g14b-captures{,2,3}.json; ftml outputs: evidence/rust-out.jsonl.

## Verdicts (live A/B/M slots; ftml in brackets where different)

- e1-forward `a=HELLO, marker={$a}`: live M=`{$a}` [ftml HELLO]
- e2-backward `marker={$a}, a=LATE`: live M=LATE [agree]
- e3-key-expr `k=marker, {$k}=KEYVAL`: live M=`{$marker}` (the expression-keyed argument does not exist) [ftml KEYVAL]
- e4-self `marker={$marker}`: live M=`{$marker}` [agree]
- e5-cycle `a={$b}, b={$a}, marker={$a}`: live A=`{$a}`, B=`{$a}`, M=`{$a}` [ftml A=`{$b}`]
- e6-undef `marker={$nope}`: live M=`{$nope}` [agree]
- e7-chain `a={$b}, b={$c}, c=DEEP, marker={$a}`: live A=DEEP, B=DEEP, M=`{$a}` [ftml M=DEEP]
- e8-empty `marker=`: live M=`{$marker}` (empty value = argument absent) [agree]
- e9-dup `marker=FIRST, marker=SECOND`: live M=FIRST [agree]
- e10-mixed `a=X, marker=pre-{$a}-post`: live M=`pre-{$a}-post` [ftml pre-X-post]
- e11-double `a=X, marker={$a}{$a}`: live M=`{$a}{$a}` [ftml XX]
- e12-late-ref `b=B, marker={$b}`: live M=`{$b}` [ftml B]
- e13-empty-then-second `marker=, marker=SECOND`: live M=SECOND [agree]
- e14-self-then-second `marker={$marker}X, marker=SECOND`: live M=SECONDX [ftml SECONDXXXX]

## The live rule (fits all 14 cases, no exceptions)

Substitution is a SEQUENTIAL FOLD over the argument list, not a map resolution. Take the arguments in source order (inert segments and empty-valued arguments skipped, exactly as in the G1.4 fragment). For each (key, rawValue) in order, replace EVERY occurrence of the literal text `{$key}` in the current content with rawValue. Consequences, each pinned by a case above:

- Values are never expanded before use; a value's own `{$...}` text lands in the content literally (e1, e10, e11, e12).
- Text inserted by an earlier argument IS rewritten by later arguments whose key it mentions (e2, e5, e7, e14). Order is therefore observable and decisive.
- Keys are never expanded (e3): an expression key names no argument.
- A duplicate key fires only if its placeholder still exists in the content when its turn comes (e9 consumed; e13 the empty first value never consumed; e14 the first value reintroduced the placeholder, so the second fires into the inserted text).
- Self-reference is not special: `{$marker}` as a value simply replaces the placeholder with itself (e4), and can be rewritten by a later duplicate (e14).

## Finding F-G14B-1 (routed 2026-11-20)

ftml's argument layer implements a different semantics: it first resolves all arguments into a map by bounded recursive expansion (values and keys expanded against the map, self-references blocked or dropped, growth capped at input size + 64 KiB), then substitutes the resolved map into the content once. On ordinary inputs this diverges from live: any argument whose value mentions another argument renders differently (e1 is the minimal shape: `[[include T | a=HELLO | marker={$a}]]` shows `{$a}` on live, `HELLO` in ftml). ftml's own unit test `ordinary_acyclic_include_argument_expansion_is_unchanged` pins the ftml behavior (b={$a}{$a} with a=x resolves to "xx"); that pin is ftml-side evidence only and is contradicted by live (e11). Severity for the parity campaign to judge; the mechanism and the 14-case evidence are here and in the ledger.

## Consequence for this loop

G1.4b models the LIVE rule (the sequential fold), not ftml's resolve_include_arguments. The Lean model is a fold of literal replace-all steps over the ordered argument list; its differential runs against live-derived expectations, and against ftml it must reproduce exactly the F-G14B-1 mismatch set above (no more, no less) until the parity side changes ftml.

## Addendum 2026-11-20: G1.4b PROVEN (model of the live rule)

`lean-ftml/LeanFtml/IncludeExpr.lean` models the live fold: `placeholder` (the literal `{$key}` text), `matchPat` (head match with remainder; `matchPat_eq_some` [propext]), `repPass` (one pass: every occurrence of the placeholder in the original content replaced, inserted text not rescanned within the pass), and `substitute` (the fold over the ordered argument list). Theorems, all proved, audits within [propext, Quot.sound], no sorry: `repPass_no_occurs` (placeholder absent at every offset implies identity), `repPass_first_occurs` (first occurrence splits the content into kept prefix, inserted value, processed tail), `substitute_append` (the fold composes over argument-list concatenation), `substitute_cons`/`substitute_nil` (the fold's step equations). lake build green on VM and WSL.

The G1.4 driver (ConformanceG14.lean) now applies the model's own `substitute` to fetched content; its argument list is the ordered segment list (duplicates kept). Results, VM-built and WSL-built drivers alike:
- G1.4 grid unchanged: 114/114 against ftml (the fold and ftml's map coincide on the literal-value fragment).
- G1.4b probe set: 14/14 against the LIVE expectations (conformance-g14b/expected-live.jsonl, built from the captures).
- Against ftml the model mismatches on exactly the F-G14B-1 set {e1-forward, e3-key-expr, e5-cycle, e7-chain, e10-mixed, e11-double, e12-late-ref, e14-self-then-second}: no more, no less. That set is the finding, reproduced mechanically; it empties if and when the parity side changes ftml.

Closure addendum (2026-11-20): ftml PR #1527 merged (squash; main tip e4b968f76). The differential was re-run the same day against the rebuilt dumper at that tip: the Lean driver and ftml now agree on 14/14, so the F-G14B-1 mismatch set {e1, e3, e5, e7, e10, e11, e12, e14} has emptied completely (rust-out-1527.jsonl). F-G14B-1 is CLOSED end to end: live rule probed, modelled and proven (IncludeExpr), divergence routed, fixed upstream in the fork, and the fix verified by this loop's own differential. The G1.4 grid also held at the new tip, 117/117 (conformance-g14/rust-out-1527.jsonl).

## Addendum 2026-11-21 (G14B-FIX): audit battery adopted; segment split corrected

The AUDIT lane's twenty adversarial cases (audit-g14b/cases.jsonl, target muse-probe-audit-g14b-target) are adopted into this battery: inputs.jsonl and expected-live.jsonl are extended by twenty records each, the captures are preserved at evidence/g14b-audit-captures.json, the cases at evidence/g14b-audit-cases.jsonl, and the audit target is added to the driver's fetchContent page map. Expectations for eighteen cases are the audit's own capture-verified fold outputs; for the two comment cases they are the adjudicated live expansions (cmt-pipe substitutes the value `[!-- a` with the remainder inert; cmt-unclosed substitutes `[!-- unclosed`). Scores: the original fourteen cases stood at 14/14 before the correction and stand at 14/14 after; the audit twenty stood at 18/20 under the old comment-aware splitSegments (failing exactly cmt-pipe and cmt-unclosed, outputs in audit-before-g14bfix.jsonl) and stand at 20/20 under the corrected raw split. Full battery after: 34/34 against live expectations (lean-after-g14bfix.jsonl). Record: REPORT-G14B-FIX.md at the loop root.
