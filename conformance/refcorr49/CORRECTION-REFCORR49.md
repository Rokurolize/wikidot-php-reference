# REFCORR49 — generic-div blank-run edge ownership

## Evidence

Three valid, stable, saved-source-byte-identical grouped live probes on `sandbox-for-codex` are the primary evidence:

- `muse-probe-hunt-cn3-heading-edges` (`heading-edges`)
- `muse-probe-hunt-cn3-div-boundaries` (`div-boundaries`)
- `muse-probe-hunt-cn3-image-edges` (`image-edges`)

The probe sources, frozen reference renders, verifier, and complete live captures are in this directory. `captures.json` SHA-256 is `976650451056508bceaf72067afd3234d228d9f13c50e06d31b2357566324988`.

## Settled behavior

### 1. Generated space lines at a div-to-div boundary are content, not formatting

A cross-line empty raw pair `@@\n@@` is already settled as one generated space. When successive raw lines form such spaces between two generic `[[div]]` blocks, live does not discard the resulting line structure:

- ten consecutive `@@` lines between two generic divs serve `<p><br />\n<br />\n<br />\n<br /></p>` between the divs;
- one same-line empty-pair sequence `@@@@ @@@@` between the divs serves an empty `<p></p>`;
- one or two consecutive `@@` lines and pure blank lines produce no visible inter-div paragraph;
- a single unterminated `@@` remains literal and serves `<p>@@</p>`;
- ordinary text between the same divs is still a normal paragraph.

The fossil `Divprefilter` rule ran after Raw and removed the entire whitespace span in `[[/div]]\s*[[div`. Because Raw had already lowered the cross-line empty pair to a literal space, the prefilter erased generated content before Newline and Paragraph could own it. Simply preserving every space-bearing span is too broad: the earlier refval divprefilter probes settle that authored horizontal whitespace between div tags is stripped. Raw therefore marks the generated cross-line space with a temporary Unicode-noncharacter sentinel (`U+FFFE U+FFFF`). The sentinel is not whitespace, so the fossil prefilter cannot swallow it as div formatting; immediately after the prefilter pass, Divprefilter restores every sentinel to the same literal space the Raw rule previously emitted. Downstream Newline, Paragraph, and Tighten therefore see the established token/input shape, while authored horizontal whitespace remains on the settled fossil stripping path. The `authored-space-control` pin is the negative control for that boundary.

### 2. A no-toc heading is still a start-typed block opener

The established empty-lead/block-lead paragraph rule already leaves explicit break lines bare when they lead into a block opener. Its token test recognized exact `start` and `*_start` subtypes, but not Heading's `start-notoc` variant. Live serves:

```html
<br />
<br />
<h1><span>H3HEAD</span></h1>
```

for ` _\n+* H3HEAD` immediately inside a generic div, and the same shape at document root. The no-toc marker changes TOC ownership only; it does not make the heading less of a block opener. The correction recognizes hyphenated `start-*` token subtypes as start-typed openers in the existing empty-lead classifier. The ordinary-text control remains paragraph-wrapped (`<p><br />\nH5TEXT</p>`), pure authored blank lines before headings remain absorbed, and the heading itself is unchanged.

### 3. The empty-paragraph image edge was already correct at snapshot-72

The exact probe shape `@@@@ @@@@` at the start of `div.report-box` before the nested image div serves `<p></p>` on live. The untouched snapshot-72 baseline already emits the same canonical shape for both the reduced probe and the full `end-of-the-world-livestream` corpus source when the fixed/reference output is canonicalized directly after its in-render purification stage, as required by the corpus-audit doctrine. The apparent census divergence was an artifact of applying a second offline tidy pass to reference output. No REFCORR49 code change was needed for this subshape; it is a positive control and a pin against regression.

## Implementation

Three parse files changed:

- `text-wiki/Text/Wiki/Parse/Default/Raw.php`
  - before SHA-256 `ed5dbe3f4b2092ea001789ccc499a397786de58eee4e775d0a1455a16e7a3f48`
  - after SHA-256 `ffed3d6fe928fd13048507065e62d37ee91bc2baac097ddfbb0dd0ce4b64dca0`
- `text-wiki/Text/Wiki/Parse/Default/Divprefilter.php`
  - before SHA-256 `4b1a5d62fc9fd5df47f2547f220f7cedd9e3160145ba02809f58f41890e2accb`
  - after SHA-256 `063c5bf6c31d92943ca148f7810ce934923c91bf3e9d31b3a0259c910b557013`
- `text-wiki/Text/Wiki/Parse/Default/Paragraph.php`
  - before SHA-256 `aec1c90de37db0e4ac07c1cbb8da96f6cbaac5d5f7be26386a8be1f1a4c85988`
  - after SHA-256 `36171d57b282dadc8278a50ceeebf607bb988c5c49d5573aae7fc130f4ba4f82`

Exact pre-change copies are preserved as `Raw.php.before-refcorr49`, `Divprefilter.php.before-refcorr49`, and `Paragraph.php.before-refcorr49` in this directory. No render file changed.

## Pins

`verify_refcorr49.py` checks the three grouped probe pages plus the authored-horizontal-whitespace negative control as expected-render byte pins and as live-canonical fidelity pins. The live-canonical comparison canonicalizes reference output directly, without a second tidy pass. Final result: 4/4 expected-render byte pins and 4/4 live-canonical fidelity pins, with no failures.

## Boundary

This correction does not claim ownership of malformed center/blockquote/div crossing repair. In particular, the post-correction first divergence in `scp-cn-3636` is the later shape where a centered block is closed by the quoted line `> [[/=]]`; live's repaired structure and the reference's blockquote/div ordering differ there. That shape is outside the generic-div blank-run family and is left as a remainder for a structural-crossing lane.
