<?php

/**
 *
 *
 * @category Text
 *
 * @package Text_Wiki
 *
 * @author Michal Frackowiak
 *
 * @license LGPL
 *
 * @version $Id$
 *
 */

/**
 *
 * Parses for spans.
 *
 * Live Wikidot (settled by saved-page probes muse-probe-r2contain-span-p01
 * through p34 and by ftml's test/span wikidot pins) keeps only class, id,
 * style, role, type and data-* attributes on a span; every other key is
 * dropped, an empty value is omitted, id carries the user-id prefix u-, and
 * data-* keys are lower-cased. The fossil implementation kept only class and
 * forced a style attribute into every token, and additionally stripped
 * visibility:hidden and display:none from style; live preserves both. A span
 * with no attributes and an empty (or whitespace-only) body is elided
 * entirely on live rather than emitting an empty element.
 *
 * @category Text
 *
 * @package Text_Wiki
 *
 * @author Michal Frackowiak
 *
 */

class Text_Wiki_Parse_Span extends Text_Wiki_Parse {

    /**
     *
     * The regular expression used to find source text matching this
     * rule. The inline %%...%% form is not a span on live (it is a
     * delayed runtime-placeholder form), so it is deliberately absent.
     *
     * @access public
     *
     * @var string
     *
     */

    public $regex = '/\[\[span(\s.[^\]]*)?\]\]((?:(?R)|.)*?)\[\[\/span\]\]/msi';

    /**
     * REFCORR13: the one attribute-value normalizer shared by Div, Span and
     * the Anchor attribute consumer. Drop the live-discarded C0 class D
     * (every byte below 0x20 except TAB 9, LF 10, CR 13 and ESC 27; DEL is
     * kept), collapse runs of space/tab/CR/LF to one space, and trim both
     * ends over the ctype_space / PCRE \s set. Live applies the same rule to
     * a Span's technical values; REFCORR12 left them raw, so class, data-*
     * and type carried authored leading/trailing spaces that live trims
     * (C-R5F-R1-1/2/3, C-R5F-S1-2). The id path keeps its own u- isolation.
     */
    function normalizeValue($value) {
        $value = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1A\x1C-\x1F]/', '', $value);
        $value = preg_replace('/[ \t\r\n]+/', ' ', $value);
        $value = ltrim($value, ' ');
        return rtrim($value, " \t\n\r\v\f");
    }

    /**
     *
     * Generates a token entry for the matched text.  Token options are:
     *
     * 'text' => The full matched text, not including the <code></code> tags.
     *
     * @access public
     *
     * @param array &$matches The array of matches from parse().
     *
     * @return A delimited token number to be used as a placeholder in
     * the source text.
     *
     */

    function process($matches) {

        // Live trims edge spaces of the span body on the same physical
        // line (probes p35/p36) but keeps them in the text flow outside
        // the element: a body of " as will ..." after a comma renders as
        // ", <span>as will ...</span>" on live, not ",<span>..." (the
        // package 2.1 holdout's span instance). Newlines are layout, not
        // edge spaces, so only horizontal whitespace is hoisted.
        $leadSpace = '';
        $trailSpace = '';
        if (preg_match('/^[ \t]+/', $matches[2], $sm)) {
            $leadSpace = $sm[0];
        }
        if (preg_match('/[ \t]+$/', substr($matches[2], strlen($leadSpace)), $sm)) {
            $trailSpace = $sm[0];
        }
        $content = trim($matches[2], " \t");

        $attrText = isset($matches[1]) ? $matches[1] : '';
        $attr = $this->getAttrs(trim($attrText));
        $args = array();
        // REFCORR12 general rule: a data-* attribute whose authored value is
        // non-empty keeps its key even when the captured value empties after
        // a nested-rule placeholder interaction. getAttrs (Parse.php:224-247)
        // assigns the empty substring when the value's closing quote was not
        // captured, and the former `$value === ''` skip then dropped the key;
        // live keeps it and emits data-x="" (C-R5E-R1-3). This records which
        // keys were authored non-empty from the raw opener text; the regex
        // deliberately allows an unterminated quote because Span's opener
        // capture stops at the first `]`. id and class/style/role/type are
        // intentionally not given this retention: cached live rows
        // R5DR1-S1 (id) and R5BR1-S1 (class) drop their key on the same
        // placeholder shape, so only the data-* family is affected.
        $authoredNonEmpty = array();
        if (preg_match_all('/([A-Za-z][A-Za-z0-9_-]*)\s*=\s*"([^"]*)/',
                $attrText, $am, PREG_SET_ORDER)) {
            foreach ($am as $m) {
                if ($m[2] !== '') {
                    $authoredNonEmpty[strtolower($m[1])] = true;
                }
            }
        }
        // Live puts id first and then preserves source order for the rest.
        if (isset($attr['id']) && $attr['id'] !== '') {
            // REFCORR5 Batch 8 (p14): live does not double an author-supplied
            // u- prefix.
            $args['id'] = (strpos($attr['id'], 'u-') === 0)
                ? $attr['id'] : 'u-' . $attr['id'];
        }
        foreach ($attr as $key => $value) {
            if ($key === 'id') {
                continue;
            }
            if ($value === '') {
                $lkey = strtolower($key);
                if (strpos($key, 'data-') === 0
                    && !empty($authoredNonEmpty[$lkey])) {
                    // Key kept with an empty value; the render's 0xFF clear
                    // arm emits data-x="" with the key present, as live does.
                    $args[$lkey] = $value;
                }
                continue;
            }
            if ($key === 'class' || $key === 'style'
                || $key === 'role' || $key === 'type') {
                // REFCORR13: technical values pass through the shared
                // Wikidot attribute normalizer (drop D, collapse W runs,
                // trim both ends); the REFCORR12 empty-value retention and
                // the render 0xFF clear arm are unchanged.
                $args[$key] = $this->normalizeValue($value);
            } elseif (strpos($key, 'data-') === 0) {
                $args[strtolower($key)] = $this->normalizeValue($value);
            }
        }
        // An unattributed empty span is elided on live; an attributed one
        // is kept (test/span/empty-id-preserved).
        if (trim($content) === '' && empty($args)) {
            return '';
        }
        $options = array('args' => $args, 'type' => 'start');

        $start = $this->wiki->addToken($this->rule, $options);

        $end = $this->wiki->addToken($this->rule, array(
            'type' => 'end'));

        return $leadSpace . $start . $content . $end . $trailSpace;

    }

    function parse() {
        do {
            $oldSource = $this->wiki->source;
            $this->wiki->source = $this->_scanSpan($oldSource);
        } while ($oldSource != $this->wiki->source);
    }

    /**
     * REFCORR16: linear-time scan replacing the whole-document recursive (?R) preg_replace_callback, whose PCRE JIT stack exhaustion silently wiped large documents (measured on real pages in the package 2.1 holdout). The public $regex remains the definitional pattern; the scanner reproduces the pattern's pairing semantics exactly, including PCRE's preference order at each body position (closer first, then a complete nested block, then one character) and its demotion backtrack: a nested block that leaves the enclosing block unclosable is demoted to literal text so the enclosing block can close at the nested block's closer.
     */
    private function _scanSpan($src) {
        $n = strlen($src);
        $out = '';
        $last = 0;
        $pos = 0;
        $memo = array();
        while ($pos < $n) {
            $cand = stripos($src, '[[span', $pos);
            if ($cand === false) {
                break;
            }
            $m = $this->_spanBlock($src, $cand, $memo);
            if ($m === false) {
                $pos = $cand + 1;
                continue;
            }
            $out .= substr($src, $last, $cand - $last);
            $out .= $this->process($m[1]);
            $last = $m[0];
            $pos = $m[0];
        }
        return $out . substr($src, $last);
    }

    private function _spanBlock($src, $p, &$memo) {
        $bk = 'b' . $p;
        if (array_key_exists($bk, $memo)) {
            return $memo[$bk];
        }
        if (!preg_match('/\G\[\[span(\s.[^\]]*)?\]\]/si', $src, $om, 0, $p)) {
            return $memo[$bk] = false;
        }
        $bodyStart = $p + strlen($om[0]);
        if (stripos($src, '[[/span]]', $bodyStart) === false) {
            return $memo[$bk] = false;
        }
        $c = $this->_spanBody($src, $bodyStart, $memo);
        if ($c === false) {
            return $memo[$bk] = false;
        }
        $matches = array(substr($src, $p, $c[1] - $p), isset($om[1]) ? $om[1] : '', substr($src, $bodyStart, $c[0] - $bodyStart));
        return $memo[$bk] = array($c[1], $matches);
    }

    private function _spanBody($src, $pos, &$memo) {
        $sk = 's' . $pos;
        if (array_key_exists($sk, $memo)) {
            return $memo[$sk];
        }
        if (preg_match('/\G\[\[\/span\]\]/i', $src, $cm, 0, $pos)) {
            return $memo[$sk] = array($pos, $pos + strlen($cm[0]));
        }
        if (stripos($src, '[[span', $pos) === $pos) {
            $sub = $this->_spanBlock($src, $pos, $memo);
            if ($sub !== false) {
                $rest = $this->_spanBody($src, $sub[0], $memo);
                if ($rest !== false) {
                    return $memo[$sk] = $rest;
                }
            }
        }
        $next = strpos($src, '[[', $pos + 1);
        if ($next === false) {
            return $memo[$sk] = false;
        }
        return $memo[$sk] = $this->_spanBody($src, $next, $memo);
    }

}
