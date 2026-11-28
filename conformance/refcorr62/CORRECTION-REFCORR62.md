# CORRECTION-REFCORR62: Size empty-Raw block and paragraph edges

## Adjudication

REFCORR62 re-derived the four carried REFCORR59 corpus clusters against snapshot-83 before probing. All six target rows diverged at baseline. Two grouped immutable sandbox matrices then isolated the remaining Size/empty-Raw behavior. Every capture used for these pins is stable across repeated anonymous reads and its saved source is byte-identical to the intended source.

The first Size matrix varies an unclosed Size scope opened immediately before a horizontal rule, ordinary and aligned images, empty Raw atoms, visible content before the rule, and quote/no-quote tails. It shows that an aligned image opener is a block boundary for the measured empty-Raw rule even though the Image rule tokenizes after Size: when empty Raw layout follows visible Size content and the next nonblank line is an aligned image opener (`[[=image` and the left/right/float opener forms in the same family), live closes the Size scope before that image container rather than reopening the span inside it. An ordinary inline image is not a boundary. A centered image that occurs before the empty Raw atom still uses the ordinary purifyHtml reopening behavior, so the correction is ordered by the empty-Raw position rather than being a blanket image rule.

The second Size matrix varies long visible text, one or four empty Raw lines, intervening visible prose, zero/one/two horizontal-rule cycles, explicit close omission, and final-tail presence. It shows that once visible inline content has followed such empty-Raw residue, the next blank-line paragraph boundary also ends the Size scope; no horizontal-rule or quote token is required. The scope does not reopen in the following paragraph.

Finally, the consumed trailing `[[/size]]` close after an already terminated scope is layout residue rather than a second rendered `</span>`. It still has to occupy an inline atom so Newline/Paragraph framing keeps the live trailing `<br />`, but rendering it as another end token produced the redundant final close seen in `shijielastday`. Emitting the residue as the established invisible empty Size atom preserves both the line framing and the live tag count.

## Implementation

`text-wiki/Text/Wiki/Parse/Default/Size.php` implements the corrections:

- aligned image opener lines are recognized as block boundaries during Size scope scanning when empty-Raw residue has followed visible content;
- a blank-line paragraph boundary closes the scope after visible content has intervened following that residue;
- the trailing consumed close is represented by a non-rendering empty Size token after a measured split, rather than by a second end token.

The pre-correction parser copy is stored beside this record as `Size.php.before-refcorr62`.

## Pins

`cases.jsonl` contains the two grouped matrices. `captures.json` records the stable byte-verified sandbox captures. `expected.json` stores the corrected reference render bytes, which are byte-identical to those captures. `verify_refcorr62.py` checks both the stored expected bytes and exact live fidelity.

The snapshot-83 six-case register re-derivation improves from 0/6 environment-aware matches at baseline to 2/6 on the corrected tree. `shaoxiang` and `shijielastday` are now both strict- and environment-equal to their saved live captures. REFCORR59's nine grouped pins remain green after this change.

## Boundaries

This correction does not weaken the REFCORR59 empty-Raw rule. It adds the missing aligned-image and blank-paragraph boundary cases and corrects the representation of the consumed trailing close. It does not claim the corrupted sentinel streams, the `scp-cn-1442` token-count provenance gap, or user-runtime whitespace are settled by this record.
