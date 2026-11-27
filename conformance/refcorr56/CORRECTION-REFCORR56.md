# CORRECTION-REFCORR56: empty-Raw token boundaries in nonempty footnote bodies

## Adjudication

The hunt-cn7 snapshot-79 register contained four CN corpus candidates. `branch-list` was already closed at baseline. The three survivors separated into one parser correction and two non-parser surfaces:

- `guide-for-writing` was a real parser divergence. In a footnote body, an empty Raw atom produced by `@@@@` is invisible, but it is still a token boundary. Live terminates an immediately preceding bare URL at that boundary; the CJK or ASCII text after the atom remains outside the link. A direct URL followed by CJK punctuation without the empty Raw atom is the negative control: live absorbs the CJK bytes into the URL. An empty Raw atom before the URL does not terminate the URL because it is not after it. A surplus fifth `@` remains visible after the boundary behavior is applied.
- `lorecon2023` did not survive reduction as a parser difference. Fresh adjacent-printuser probes render `</span>&amp;<span>` without inserting a generated space. The cached corpus page's single space at the first long-table seam is associated with that production user rendering (`alt="haplocalyx "` carries trailing-space user data), not a parser-owned space; later equivalent seams for ordinary users in the same cached page have no space.
- `log-of-anomalous-items` did not survive reduction as a parser difference. Fresh interwiki probes serve `https:` for Wikipedia, Polish Wikipedia, Google, and Dictionary references, matching the existing harness configuration. The cached CN page's `http:` Wikipedia URL is capture/render-cache provenance, not current parser behavior.

## Mechanism and implementation

`Footnote.php` already removed empty-Raw placeholders in no-single-authored-LF footnote bodies so that an invisible-only footnote would not manufacture an empty paragraph. It applied that stripping to the whole body even when visible content was present. Because footnote bodies are stored and reparsed, deleting those placeholders also deleted real token boundaries before the Url rule ran.

The fallback now computes the visible projection as before, but uses it only to decide emptiness. If the visible projection is empty, the body is still stripped to the empty visible form. If the body has visible content, discarded C0 bytes are removed while empty-Raw placeholders remain in the stored token stream. They render as nothing and are removed by the final Tighten pass where appropriate, but during reparsing they preserve the measured token boundary. The single-authored-LF branch and its newline-witness semantics are unchanged.

## Pins

`cases.jsonl` contains one immutable grouped sandbox matrix, `raw-url-boundary-matrix`, covering eight reduced shape cells: outside-footnote positive control, footnote CJK and ASCII tails after `@@@@`, direct no-Raw negative control, space after the empty Raw atom, single-newline witness behavior, empty-Raw-before-URL control, and five-`@` surplus control. `captures.json` records the immutable sandbox capture. `verify_refcorr56.py` passes the expected-render byte pin and grouped-matrix live-canonical fidelity check. `Footnote.php.before-refcorr56` is the pre-correction implementation copy.
