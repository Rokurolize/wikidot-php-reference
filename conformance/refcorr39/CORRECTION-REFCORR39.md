# REFCORR39 — control bytes in teletype bodies and scheme links

REFCORR39 settles the byte-verified control-character family measured in the fresh sandbox probes `muse-probe-hunt-ctrl-token-core`, `-token-more`, `-token-neighbors`, `-token-exact`, `-tt-edges`, `-link-vtff`, `-link-c0a`, `-link-c0b`, and `-link-forms`. Every accepted capture is stable across two anonymous GETs and its saved source is byte-identical to the intended source. Probe pages are left in place; no production page was accessed.

## Corrected mechanisms

1. Teletype padding is classified after the live-discarded C0 byte class is removed from the body. The class is the already established `[\x00-\x08\x0B\x0C\x0E-\x1A\x1C-\x1F]` set: TAB, LF, CR and ESC are not in it. A lone VT or FF body therefore disappears with the `{{...}}` pair instead of leaving an empty `<tt></tt>`. The edge matrix shows why the removal happens before padding classification rather than only at final text output: `{{\v x}}` renders ` <tt>x</tt>` with one hoisted leading space, `{{x \v}}` renders `<tt>x</tt> ` with one ejected trailing space, and `{{ \v }}` renders one plain space.
2. Url token output removes the same discarded C0 class from the serialized href and label. Recognition happens before that removal: a control-only label still forms a link and renders `<a href="http://a"></a>`, rather than literalizing the bracketed form. The link-form discriminator shows the same stripping in a bare autolink, an unlabeled bracket autolink, and a described link when the control is interior to the target; terminal controls already terminate the fossil bare-target scan and are unchanged.

## Refuted token-family members

The task-31 summary said a lone FF body in a strong pair was consumed on live. The fresh byte-verified exact probe does not reproduce that claim: both `a**\f**b` and `a**\v**b` render `<p>a****b</p>`, exactly as the reference already did. The grouped matrix also shows VT/FF-only bodies literalizing for emphasis, underline, strike, superscript, and subscript, again matching the reference. NEL, ZWSP, BOM, a combining mark, an ordinary body, a tab body, and the space-padded FF form are unchanged controls and match live. No correction is made in those pair rules. The earlier `ab` reading is treated as refuted probe evidence, and the corresponding ftml behavior is recorded as a parity item in the lane result rather than as a reference fix.

## NUL boundary

The NUL member could not be measured as a stored live source in this lane. Wikidot's save path silently removed NUL despite byte-verified saves of SOH, BS, VT, FF, FS, and US; the NUL capture is therefore invalid evidence and is not one of the canonical pins. The implementation keeps NUL inside the already established discarded-C0 class used elsewhere in the reference, but no new NUL-specific live claim is made here.

## Pins

`cases.jsonl`, `expected.json`, `captures.json`, and `verify_refcorr39.py` pin nine grouped pages: the inline-format matrix, neighbor controls, exact VT/FF forms, the TT edge matrix, the VT/FF link matrix, two additional C0 link matrices, and the link-form discriminator. Verification in this checkout: expected-render **9/9**, live canonical fidelity **9/9**.

## Files changed

The parser correction is limited to `text-wiki/Text/Wiki/Parse/Default/Tt.php`; the link serialization correction is limited to `text-wiki/Text/Wiki/Render/Xhtml/Url.php`. The conformance record is contained in this directory. No corpus file, ftml tree, other parse rule, or production-facing artifact was changed.
