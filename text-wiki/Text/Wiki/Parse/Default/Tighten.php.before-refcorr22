<?php

/**
*
* The rule removes all remaining newlines and performs the final
* output-shaping pass over the residual source text.
*
* @category Text
*
* @package Text_Wiki
*
* @author Paul M. Jones <pmjones@php.net>
*
* @license LGPL
*
* @version $Id$
*
*/

/**
*
* The rule removes all remaining newlines and performs the final
* output-shaping pass over the residual source text.
*
* @category Text
*
* @package Text_Wiki
*
* @author Paul M. Jones <pmjones@php.net>
*
* @license LGPL
*
*/

class Text_Wiki_Parse_Tighten extends Text_Wiki_Parse {

    /**
    *
    * Apply tightening directly to the source text.
    *
    * This is the last parse rule, so every other rule has already replaced
    * its own body with a token placeholder. What is left in the source is
    * ordinary text plus token delimiters, which makes this the one place
    * where whole-document output shaping can be applied without touching a
    * construct's own content. Three operations are owed to live here; the
    * fossil rule had only the first.
    *
    * Newline removal is the fossil behavior and stays as it was: it drops
    * the framework's leading and trailing padding newlines. Block renderers
    * emit their own inter-block newlines afterwards, so this cannot erase a
    * paragraph or a line break.
    *
    * Live's WikiTransformation::purifyHtml (the libtidy pass) folds a
    * horizontal whitespace run to one space in rendered text. Live probes
    * muse-probe-r2in3-tighten-tighten18, -tighten19, -tighten22 and
    * -tighten23 (a  b, a   b, a\t\tb and a \t b) each render as <p>a b</p>
    * on the saved page, and ftml's legacy-layout dumper agrees. Because
    * bodies are already tokenized, this fold reaches only residual text; a
    * double space inside [[code]] stays inside a token placeholder and is
    * preserved, as live and ftml both require (adhoc case adh02).
    *
    * Live also moves edge spaces out of an inline color scope rather than
    * leaving them inside the span: a space just after a color opener is
    * hoisted to before the opener, and a space just before a color closer
    * is ejected to after the closer. At a paragraph edge the hoisted or
    * ejected space is then dropped. Live probes tighten40 through tighten44
    * settle this, the frozen ftml fixtures span/leading-space and
    * color/whitespace-only-body-span-open-hoist pin it, and the color
    * owner's probe c53 settles the ejected-space-followed-by-text shape,
    * which the verify-cases.jsonl v01 record reproduces.
    *
    * Finally, a space exposed at a paragraph or line-break edge by a later
    * rule's token deletion, or left after a break by an authored leading
    * space, is trimmed here. The Paragraph rule trims its source run before
    * the Underline rule deletes an empty ____ pair, so a plain trailing
    * space is removed but the space the deletion exposes is not; live
    * probes tighten51 and tighten53 settle the paragraph edges and tighten14
    * and tighten56 settle the break edges. This is the whitespace component
    * of the Underline section's p02 residual, and it is owned by this final
    * pass rather than by Underline.
    *
    * @access public
    *
    */

    function parse()
    {
        $source = $this->wiki->source;

        // Fossil behavior: remove all remaining newlines.
        $source = str_replace("\n", '', $source);

        // R11-CONCAT: live's purifyHtml drops the discarded C0 control set
        // from residual plain text (0x00-0x08, 0x0B, 0x0C, 0x0E-0x1A,
        // 0x1C-0x1F): TAB, LF, CR and ESC are kept. The same byte class the
        // Size rule already uses; form feed 12 is the round-5d witness. Token
        // placeholders hold only 0xFF and digits, so no token body is touched.
        // Drop here as well as in the footnote body path so both seams agree.
        $source = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1A\x1C-\x1F]/', '', $source);

        $delim = $this->wiki->delim;

        // REFCORR5 Batch 6: an empty Raw token renders as nothing, so its
        // placeholder must be transparent to the horizontal-space collapse
        // below. Without this, "a @@@@ b" would move from the pinned "a b"
        // to "a  b". Removing the placeholder from the residual stream is
        // safe: the token stays in the token array (so indices and Date
        // format strings that reference it are unchanged) and its render
        // would have been the empty string. REFCORR7 (idx-after): when the
        // document carries a literal U+FFFD the recovery path walks the
        // whole adjacent placeholder run and leaks every index, so the
        // empty Raw placeholder must stay in the residual stream exactly
        // as live keeps it; dropping it loses its leaked digit.
        $hasUfffd = strpos($source, "\xEF\xBF\xBD") !== false;
        foreach ($this->wiki->tokens as $tid => $tok) {
            if (! $hasUfffd && is_array($tok) && $tok[0] === 'Raw' && isset($tok[1]['text'])
                && $tok[1]['text'] === '') {
                $source = str_replace($delim . $tid . $delim, '', $source);
            }
        }

        // Fold residual horizontal whitespace runs to one space. Token
        // delimiters hold no spaces or tabs, so tokenized bodies survive.
        $source = preg_replace('/[ \t]+/', ' ', $source);

        // Move an edge space out of an inline color scope. Hoisting the
        // leading space to before the opener and ejecting the trailing space
        // to after the closer is what live's Stage 2 repair does; the
        // paragraph-edge pass below drops the space when the scope sits at
        // a paragraph boundary.
        foreach ($this->wiki->tokens as $tid => $tok) {
            if (! is_array($tok)) {
                continue;
            }
            $literal = $delim . $tid . $delim;
            $pattern = preg_quote($literal, '/');
            $type = isset($tok[1]['type']) ? $tok[1]['type'] : '';
            if ($tok[0] === 'Colortext' && $type === 'start') {
                $source = preg_replace('/' . $pattern . ' /', ' ' . $literal, $source);
            } elseif ($tok[0] === 'Colortext' && $type === 'end') {
                $source = preg_replace('/ ' . $pattern . '/', $literal . ' ', $source);
            }
        }

        // Hoisting and ejecting can create a new run of two spaces; fold
        // again before the edge trims so both are single-space decisions.
        $source = preg_replace('/[ \t]+/', ' ', $source);

        // Trim a space at a paragraph or line-break token edge. This removes
        // a hoisted or ejected space at a paragraph boundary and a single
        // space that a later rule's token deletion exposed at a paragraph or
        // break edge. Live probes tighten51, tighten53, tighten14 and
        // tighten56 settle the deletion-exposed cases at both edges.
        foreach ($this->wiki->tokens as $tid => $tok) {
            if (! is_array($tok)) {
                continue;
            }
            $literal = $delim . $tid . $delim;
            $pattern = preg_quote($literal, '/');
            if ($tok[0] === 'Newline') {
                $source = preg_replace('/' . $pattern . ' +/', $literal, $source);
                $source = preg_replace('/ +' . $pattern . '/', $literal, $source);
                continue;
            }
            if ($tok[0] !== 'Paragraph') {
                continue;
            }
            $type = isset($tok[1]['type']) ? $tok[1]['type'] : '';
            if ($type === 'start') {
                $source = preg_replace('/' . $pattern . ' +/', $literal, $source);
            } elseif ($type === 'end') {
                $source = preg_replace('/ +' . $pattern . '/', $literal, $source);
            }
        }

        $this->wiki->source = $source;
    }
}
