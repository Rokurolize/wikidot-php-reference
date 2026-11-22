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
            } elseif (strpos($key, 'data-') === 0) {
                $lkey = strtolower($key);
                if (!array_key_exists($lkey, $args)) {
                    $args[$lkey] = $this->normalizeValue($value);
                }
            }
        }
        ksort($args);

        // An empty div whose head carries no effective attribute vanishes
        // on live and in ftml; the surrounding blank line remains.
        $effective = false;
        foreach ($args as $value) {
            if (trim($value) !== '') {
                $effective = true;
                break;
            }
        }
        if (!$effective && trim($content) === '') {
            return $matches[1] . $matches[1];
        }
        foreach ($args as $key => $value) {
            if (trim($value) === '') {
                unset($args[$key]);
            }
        }

        $start = $this->wiki->addToken($this->rule, array(
            'args' => $args, 'type' => 'start'));
        $end = $this->wiki->addToken($this->rule, array('type' => 'end'));

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
