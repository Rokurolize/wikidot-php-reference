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

        // Live drops edge spaces of the span body on the same physical line
        // (probes p35/p36); newlines are layout, not edge spaces, so only
        // horizontal whitespace is trimmed.
        $content = trim($matches[2], " \t");

        $attr = $this->getAttrs(trim($matches[1]));
        $args = array();
        // Live puts id first and then preserves source order for the rest.
        if (isset($attr['id']) && $attr['id'] !== '') {
            // REFCORR5 Batch 8 (p14): live does not double an author-supplied
            // u- prefix.
            $args['id'] = (strpos($attr['id'], 'u-') === 0)
                ? $attr['id'] : 'u-' . $attr['id'];
        }
        foreach ($attr as $key => $value) {
            if ($key === 'id' || $value === '') {
                continue;
            }
            if ($key === 'class' || $key === 'style'
                || $key === 'role' || $key === 'type') {
                $args[$key] = $value;
            } elseif (strpos($key, 'data-') === 0) {
                $args[strtolower($key)] = $value;
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

        return $start . $content . $end;

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
