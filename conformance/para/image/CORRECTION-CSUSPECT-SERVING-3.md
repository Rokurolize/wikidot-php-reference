# CORRECTION C-SUSPECT-SERVING-3 — Image link= unanchored scheme (REFCORR3 lane, 2026-11-22)

Status: APPLIED in this tree. The reference's Image parse rule built its URL pattern without a `^` anchor, so a link value whose only valid scheme appears embedded later was claimed and rendered as a malformed clickable image. Live leaves the whole `[[image ...]]` opener literal. Candidate C-SUSPECT-SERVING-3 is recorded in GAP-LEDGER.md and REPORT-SUSPECT-SERVING.md.

## The settling evidence (fresh live probes, all valid, stable, and saved-source-matching)

Probe muse-probe-suspect-serving-img-colonslash-leading (conformance-suspect-serving/probe-cases3.jsonl, captures3.json), source `[[image https://example.com/a.png link="://x http://example.com/y"]]`, served `<p>[[image <a href="https://example.com/a.png">https://example.com/a.png</a> link=&quot;://x <a href="http://example.com/y">http://example.com/y</a>&quot;]]</p>`; the reference had emitted `<a href="/://x http://example.com/y"><img ... /></a>`. The controls muse-probe-suspect-serving-img-scheme-http and -gopher are accepted on both sides and -irc stays literal on both, so only the embedded-scheme shape moves.

## The correction (reference)

Parse/Default/Image.php's constructor pattern gains a leading `^`, so the link value's scheme must be at the head; the existing `preg_match` check then returns the whole opener literal for the embedded-scheme value, exactly as live does. The renderer is left alone: with an anchored parse the malformed value never reaches it, and the pinned http/gopher/irc shapes are untouched. Before-copy: ref-php/text-wiki/Text/Wiki/Parse/Default/Image.php.before-refcorr3 (SHA-256 c1d84d89203825574ebc93f5fd16552c409bd7f2a21809a62ef66edf692ea98b); corrected SHA-256 7e7260b5a488e770....

## Firsthand verification (REFCORR3 lane, 2026-11-22)

The corrected reference renders the decisive probe byte-identically to live and leaves the three controls unchanged. The R2 para/image battery and the r43 family are re-run in REPORT-REFCORR3.md.

## Mirror consequence

lean-ftml/LeanFtml/ParaRules.lean's imageProcess uses the head-anchored imageUrlHere instead of the unanchored imageUrlMatches, with its doc comment restated; the r43 gates are re-run; see REPORT-REFCORR3.md.
