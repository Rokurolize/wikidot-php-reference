# REFCORR71 measurement closure — module boundary bytes and body capture

REFCORR71 is a measurement closure, not an executable parser correction. No PHP source file is changed.

## Recovered sub-fact

The m4 evidence was re-derived from the lane artifacts rather than the one-line summary. The important refinement is that, for an attributed inline empty module such as `[[module ListPages ...]][[/module]]`, the suspicious bytes are swallowed into the module **attribute string**, not into `module_body`. At snapshot-91 the opener regex requires a newline after `]]`; the opener's own inline `]]` is not followed by a newline, so the lazy attribute group backtracks through the would-be closer and the opener is closed at that closer's terminal `]]`. The resulting attr ends with the exact bytes `]][[/module` (encoded in the fossil wire as `%5D%5D%5B%5B%2Fmodule`) and `module_body` is empty.

## Probe design

Eight immutable grouped pages were created once on `sandbox-for-codex` under `muse-p-modbody-*` and never edited. Every page read back byte-identical source and every rendered capture was stable across the harness's two anonymous GETs. Well-formed controls are grouped only with other well-formed controls; every malformed or potentially unclosed shape is the sole module opener in its page, so one no-closer shape cannot swallow or rewrite a later independent opener.

The ListPages target is the existing immutable R2 probe page `muse-probe-r2mod-module-mod-basic`, selected by exact name. No target holder page was created. The eight probe-page cycles used the full ordinary budget.

## Measured rule

Live Wikidot and snapshot-91 agree in every probed position:

- Well-formed multiline ListPages bodies, including nested-div bodies and end-of-page bodies, are captured as `module_body` and rendered with `%%title%%` substitution.
- A well-formed empty body produces an empty/default module and leaves the line-start `[[/module]]` as literal residue.
- Unattributed inline `[[module ListPages]][[/module]]` remains literal.
- Attributed inline `[[module ListPages ...]][[/module]]` produces an empty/default ListPages module with no literal closer. The reference token pin shows why: `]][[/module` is in the attr field and `module_body` is empty. Middle-of-page and end-of-page positions agree.
- Attributed inline body text is not captured as the ListPages body, does not render with `%%title%%` substitution, and is not left outside the module. The reference token pin puts the exact bytes `]]LBODY %%title%%[[/module` in attr and leaves `module_body` empty; live behavior is consistent with that parse.
- In `[[/div]][[/module]]`, the adjacent module closer is not a delimiter because the module closer must begin at line start. Both sides produce an empty/default module and leave the nested div text plus literal `[[/module]]` outside.
- An attributed inline opener followed immediately by tail text and no closer remains entirely literal.
- Unknown-module immediate and inline-body shapes have the same parser placement and residue on both sides; serving-layer module expansion remains out of scope.

Because live and the reference already agree, no parser rule correction is warranted. These pins exist to prevent regressions in the measured behavior.

## Pins and comparison discipline

`cases.jsonl` contains the eight immutable page sources. `captures.json` contains the stable byte-verified live captures. `probe-design.json` maps the twelve shape cells. `expected.json` pins exact reference renders, and `expected-tokens.json` pins the decisive module token fields. `verdicts.jsonl` records the per-position adjudication.

`verify_refcorr71.py` checks exact render and token pins, then applies the binding symmetric comparison discipline: live `#page-content` bytes are canonicalized directly; reference output receives exactly one libtidy/purifyHtml-equivalent pass and is never tidied twice. Both sides then receive the same campaign canonicalization. For this lane only, live-expanded ListPages widgets and reference `þmodule "ListPages" ... þ` fossil handoffs are both masked to one module-occurrence node before that shared canonicalization, because module serving expansion is explicitly out of scope; parser residue outside the module is not masked.
