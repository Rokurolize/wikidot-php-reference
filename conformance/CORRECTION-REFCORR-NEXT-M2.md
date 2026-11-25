# CORRECTION REFCORR-NEXT — m2 reference-side findings

Status: APPLIED in this tree on branch `refcorr-next/m2-findings`, based on snapshot-48 (`09bb79184b23641e878e72deb7f7ebe0a8284d2d`). The round number is deliberately left as NEXT: the coordinator assigns it at landing, and REFCORR24 is reserved for the threshold lane. The measured inputs and verdicts are retained in `lanes/m2-measure/outputs/`; the independent primary-source confirmation is `VERIFY-M2.md` item 4. No ftml file was edited.

## FIX 1 — entity decoding inside angle raw (`@<...>@`)

Live Wikidot decodes semicolon-terminated HTML entities in the body of an `@<...>@` raw span *before* the Wikidot raw-escape serialization. The snapshot-48 reference skipped that decode and escaped the source spelling literally, so `@<&gt;>@` rendered a span containing `&amp;gt;` where live renders `&gt;`.

The correction adds `wikidotDecodeRawEntities()` beside the angle-raw branch of `Text_Wiki_Parse_Raw::parse()`. It is a single left-to-right pass modeled on ftml's `decode_semicolon_entities()` (`m2-ftml` `src/parsing/rule/impls/entity.rs`): for each `&`, the next `;` ends the candidate; only a body that actually names a WHATWG HTML entity (named, `#` decimal, or `#x` hex) is replaced; unknown and unterminated bodies such as `&copy` and `&not-an-entity;` are preserved byte-for-byte; and the decoded text is never re-scanned. There is therefore **no repeated decoding**: source `&amp;gt;` becomes the visible text `&gt;`, not `>`. No witness in the m2 corpus or the ftml `left_raw_*` pins shows a second pass, so none is applied. The `@@...@@` form deliberately does not call the decoder (ftml's `double_at_raw_does_not_decode_entities` pin).

A decoded U+00A0 is serialized as the `&nbsp;` entity on live (`art:vasilisa-blud` serves `<span style="white-space: pre-wrap;">&#32;&nbsp;&#32;</span>`). Angle-raw tokens now carry `angle => true`, and the canonical `wikidotEscapeRaw()` in `Render/Xhtml/Form.php` (loaded before `Raw.php`, so it is the live definition) adds the U+00A0 → `&nbsp;` table entry only for that flag. The plain `@@` raw form keeps the original table; a literal NBSP byte there is still emitted literally, consistent with ftml's unmodified `escape_wikidot_raw`.

**Witnesses (cached live at the primary source, read before editing):**

- `canon-hub/html.xmlrpc.html`: the decisive raw span is `&gt;` and `&amp;gt;` occurs zero times in the cached page.
- `art:vasilisa-blud/html.xmlrpc.html`: the sole pre-wrap span is `&#32;&nbsp;&#32;`; `&amp;nbsp;` occurs zero times.
- 11 retained corpus `@<...>@` instances in the m2 `A-ANGLE-RAW-CORPUS` batch (include markup, nested angle brackets / triple links, literal stars, space-only body, glued `>` closer, empty raw, `@@` bytes inside angle raw). None contains an entity, so the decoder is a no-op for them and their byte shape is unchanged.
- Synthetics `a-syn-entity-gt` (`@<&gt;>@`) and `a-syn-entity-amp` (`@<&amp;>@`): the m2 verdicts record that ftml matches the live-established entity-decoding behavior while the old reference preserved the spelling.

**Pins:** `conformance/formraw/refcorr-next-angle-entity-cases.jsonl` (19 cases: 11 corpus + 8 synthetic) and `refcorr-next-angle-entity-expected.json`, with per-case expected HTML and the cached-live raw spans carried in the evidence field. `python3 conformance/formraw/verify_refcorr_next.py` reports 19/19.

**Scope limit:** only the `@<...>@` token body is decoded. The decoder recognizes the WHATWG named-entity set via PHP's `html_entity_decode(..., ENT_HTML5)` under the strict `&name;` / numeric-semicolon scanner; no invented entity or second pass is added. A candidate body containing `&` is rejected, so `&gt&gt;` stays literal rather than picking up a semicolon-less trailing entity (checked against ftml's `render_html_jsonl` at 42349e59). PHP's decoder also rejects the NUL codepoint, so `&#0;` stays visible where ftml accepts it and escapes NUL to a space; no cached live witness covers that shape, so the conservative PHP/live-side behavior is kept rather than widening the decoder. Entity decoding in `@@...@@`, in ordinary text, and in attribute values is untouched.

## FIX 2 — curly apostrophe deletion in the freelink slug

`WDStringUtils::toUnixName()` had no entry for U+2019, and `freelink_transliterate()` routes every unmapped non-ASCII code point to a separator space. A title `O5’s` therefore slugified to `o5-s`. Live deletes the curly apostrophe outright (`o5s`), which also moves the 60-byte href cut one byte later.

The correction adds an explicit `’ => ''` entry to `freelink_transliterate()`'s map (the layer that actually sees the character, because it runs before `toUnixName`) and the same deletion to `WDStringUtils::$CONVERT_ARRAY` so any other direct `toUnixName` caller follows the same slug rule. The straight apostrophe U+0027 is ASCII and stays on the pass-through arm, so live's generic punctuation → hyphen behavior is preserved.

**Witnesses (cached live anchors at the primary source):**

- `adamantine-temptations-hub` (`b-real-adamantine-o5`): live `href="/a-former-o5s-guide-on-how-to-eat-lead-and-destroy-all-of-you"` (60 bytes) against the old reference `o5-s...-yo`.
- Six independent short-title anchors: `isn’t → isnt`, `David’s → davids`, `can’t → cant`, `Lion’s → lions`, `World’s → worlds`, `Who’s → whos`. These settle deletion rather than a truncation artifact.
- Straight apostrophe control: cached live `War is Child's Play` → `/war-is-child-s-play` in `let-s-go-again-shall-we`. Live keeps the hyphen, so the pinned change is specific to U+2019 and does **not** generalize to U+0027. The reference output for this control is unchanged byte-for-byte.

**Pins:** `conformance/link/freelink/refcorr-next-o5-slug-cases.jsonl` (8 cases, 7 curly + 1 straight control) and `refcorr-next-o5-slug-expected.json`, each with the cached-live href in the evidence field. `python3 conformance/formraw/verify_refcorr_next.py` reports 8/8.

**Scope limit:** only U+2019 is deleted. No claim is made about U+2018, U+02BC, or other apostrophe-like code points; the corpus witnesses cover U+2019 and U+0027 only. Page-existence class and the surrounding serving frame remain environment-bound and are not part of the pin bytes.

## Regression surface on the retained m2 cases

Re-rendering all 106 m2 inputs through the corrected reference moves exactly five outputs: the four entity cases (`a-syn-entity-gt`, `a-syn-entity-amp`, `a-real-canon-entity-gt`, `a-real-vasilisa-nbsp`) and `b-real-adamantine-o5`. The four entity cases now match ftml byte-for-byte; the two cached-live corpus cases match their primary-source raw span / href. `a-real-vasilisa-nbsp` and `b-real-adamantine-o5` intentionally differ from ftml because ftml emits a literal NBSP / an unhyphenated-but-untruncated slug; the reference now matches cached live on both decisive bytes. All other 101 cases are byte-identical to the snapshot-48 reference, including the other ten corpus angle-raw instances and the nine other overlong freelink cases.
