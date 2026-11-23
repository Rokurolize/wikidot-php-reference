<?php

/**
 *
 * Parses divs.
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
 * Parses divs.
 *
 * @category Text
 *
 * @package Text_Wiki
 *
 * @author Michal Frackowiak
 *
 * @license LGPL
 *
 */

class Text_Wiki_Parse_Div extends Text_Wiki_Parse {

    /**
     *
     * The regular expression used to find source text matching this
     * rule. Group 2 is the scored alias marker ("_" for [[div_]]):
     * live and ftml recognize the standalone scored opener and render a
     * paragraph-stripped div, which the fossil skeleton missed (the
     * Concatlines N1 residual). Group 3 is the attribute tail and group 4
     * the body; the recursive body match keeps first-closer discipline.
     *
     * @access public
     *
     * @var string
     *
     */
    public $regex = '/(\n)?\[\[div(_?)(\s.*?)?\]\] *\n((?:(?R)|.)*?)\[\[\/div\]\] */msi';

    /**
     * Wikidot normalizes every HTML attribute value by dropping control
     * characters and collapsing runs of whitespace to one space, with any
     * leading whitespace removed. This mirrors ftml's
     * normalize_wikidot_html_attribute_value.
     */
    function normalizeValue($value) {
        $value = preg_replace('/[\x00-\x1F\x7F]/', '', $value);
        $value = preg_replace('/[ \t\r\n]+/', ' ', $value);
        return ltrim($value, ' ');
    }

    /**
     * Wikidot isolates user ids: collapse whitespace, prefix "u-" unless
     * the value already begins with it, and turn a whitespace-only value
     * into "u-". This mirrors ftml's isolate_ids.
     */
    function isolateId($value) {
        if ($value === '') {
            return '';
        }
        // REFCORR10 general rule: an authored id whose body carries a 0xFF
        // token placeholder is preserved verbatim for ANY body, including
        // one that already starts with u-, so the render's single 0xFF
        // clear arm emits id="" with the key kept (C-R5C-R1-1, C-R5C-S1-1).
        // The former u- prefix exclusion made the /u collapse return null
        // and the caller drop the id, contradicting live. A whitespace-only
        // authored id has no placeholder and still isolates to the bare
        // u- shell (R5R1-D1), which the render emits verbatim.
        if (strpos($value, "\xFF") !== false) {
            return $value;
        }
        if (preg_match('/^\s/u', $value)) {
            $leading = true;
        } else {
            $leading = false;
        }
        $collapsed = preg_replace('/\s+/u', ' ', trim($value));
        if ($collapsed === '') {
            return 'u-';
        }
        if (strpos($value, 'u-') === 0) {
            return $collapsed;
        }
        return 'u-' . ($leading ? ' ' : '') . $collapsed;
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
        $score = isset($matches[2]) ? $matches[2] : '';
        $content = $matches[4];
        $attrText = isset($matches[3]) ? $matches[3] : '';
        $attr = $this->getAttrs(trim($attrText));

        // Wikidot's div head keeps only class, id, style, role, type and
        // data-* attributes (case-sensitive names, data-* lowercased). The
        // fossil kept only class and style and stripped hidden styles, both
        // of which live contradicts.
        $args = array();
        // REFCORR8 C-R5-P1-1: carry, outside the compared token options,
        // whether each stored key came from a non-empty authored value.
        // A value authored non-empty but normalizing to empty (e.g. a
        // whitespace-only class) is still a real attribute and renders as
        // class=""; only a literally empty authored value is unset.
        $authoredValue = array();
        foreach ($attr as $key => $value) {
            if ($key === 'id') {
                $id = $this->isolateId($value);
                if ($id !== '') {
                    $args['id'] = $id;
                }
            } elseif ($key === 'class' || $key === 'style' || $key === 'role' || $key === 'type') {
                $normalized = $this->normalizeValue($value);
                if ($key === 'class') {
                    $normalized = rtrim($normalized, " \t");
                }
                $args[$key] = $normalized;
                $authoredValue[$key] = ($value !== '');
            } elseif (strpos($key, 'data-') === 0) {
                $lkey = strtolower($key);
                // REFCORR8 C-R5-P1-2: case-variant duplicate data-*
                // keys are last-wins on live, not first-wins. The
                // lowercase key is unchanged; only the collision
                // tie-break moves to the later authored value.
                $args[$lkey] = $this->normalizeValue($value);
                // REFCORR9 C-R5B-P1-5: a later case-variant authored-empty
                // value must not clear the authored-nonempty record for the
                // same lowercased key. Live keeps the last (empty) value as
                // an attribute when an earlier variant authored a nonempty
                // value; the reference's empty-unset dropped it because the
                // flag was overwritten to false. Keep the last-wins value
                // itself and make only the authored flag monotone across
                // case-variant duplicates.
                $authoredValue[$lkey] = !empty($authoredValue[$lkey]) || ($value !== '');
            }
        }
        // REFCORR2 correction C-STAGE2-1: live emits a div's attributes
        // in a fixed order, id, class, style, role, type, followed by
        // the data-* attributes in authored order (probes
        // muse-probe-refcorr2-diva-a1 to a8, all valid, stable and
        // source-matching). The fossil's ksort sorted every key by
        // name, which puts class before id and sorts the data-*
        // attributes among themselves; the order is therefore built
        // explicitly here, where the authored data-* order is still
        // available. Record:
        // conformance-refphp/contain/CORRECTION-CSTAGE2-1.md.
        $ordered = array();
        foreach (array('id', 'class', 'style', 'role', 'type') as $key) {
            if (array_key_exists($key, $args)) {
                $ordered[$key] = $args[$key];
            }
        }
        foreach ($args as $key => $value) {
            if (strpos($key, 'data-') === 0) {
                $ordered[$key] = $value;
            }
        }
        $args = $ordered;

        foreach ($args as $key => $value) {
            if (trim($value) === '' && empty($authoredValue[$key])) {
                unset($args[$key]);
            }
        }

        // REFCORR2 correction C-STAGE2-2: an empty div whose head
        // carries no effective attribute is suppressed on live, but
        // the suppressed pair still counts as a block boundary for
        // what follows: the text after it is not paragraph-wrapped
        // and a leading newline becomes a break (probes
        // muse-probe-refcorr2-divn-s5, s10, s11 and the R2
        // empty-plain and score-empty captures). The earlier
        // reference returned only the doubled leading newline and
        // claimed no tokens, which made the following text a fresh
        // paragraph. The pair is now claimed with a 'vanished' flag
        // and the renderer suppresses the tags instead. Record:
        // conformance-refphp/contain/CORRECTION-CSTAGE2-2.md.
        $vanished = ($args === array()) && trim($content) === '';

        $startOpts = array('args' => $args, 'type' => 'start');
        $endOpts = array('type' => 'end');
        if ($vanished) {
            $startOpts['vanished'] = true;
            $endOpts['vanished'] = true;
        }

        $start = $this->wiki->addToken($this->rule, $startOpts);
        $end = $this->wiki->addToken($this->rule, $endOpts);

        if ($score !== '') {
            // The scored [[div_]] form strips paragraphs: blank-line runs
            // vanish, leading and trailing newlines go, and single newlines
            // remain for the Linebreak rule to turn into <br />.
            $body = trim($content, "\r\n");
            $body = preg_replace('/\n[ \t]*(?:\n[ \t]*)+/', '', $body);
            return $matches[1] . $start . $body . $end;
        }

        return $matches[1] . $matches[1] . $start . "\n\n" . $content . "\n\n" . $end;

    }

    function parse() {
        $oldSource = $this->wiki->source;
        $this->wiki->source = preg_replace_callback($this->regex, array(
            &$this, 'process'), $this->wiki->source);
        if ($oldSource != $this->wiki->source) {
            $this->parse();
        }
    }

}
