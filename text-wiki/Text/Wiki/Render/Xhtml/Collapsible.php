<?php
// vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
/**
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    $Id$
 * @link       http://pear.php.net/package/Text_Wiki
 */

/**
 * Renders collapsible block.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Collapsible extends Text_Wiki_Render {

    public $conf = array();

    /**
     * Render a Wikidot collapsible link label. Live renders the label text into
     * the anchor with spaces turned into &nbsp;, tabs into four &nbsp; entities,
     * line breaks into a plain space, and control characters dropped; the
     * default show label is "+ show block" and the default hide label uses an
     * en dash ("– hide block"). See conformance-refphp/contain/collapsible/
     * SECTION.md and the cached muse-probe-r2contain-coll- probes.
     */
    function wikidotLabel($text, $show)
    {
        if (!isset($text) || $text === '' || $text === '0') {
            $text = $show ? '+ show block' : "\xE2\x80\x93 hide block";
        }
        // SUSPECT-INTERACT C1: live leaves a single quote raw in a label
        // (probe muse-probe-suspect-interact-c1-coll-apostrophe: live
        // "it's"/"don't" versus the former ENT_QUOTES "it&#039;s"/
        // "don&#039;t"). ENT_COMPAT keeps the other escapes and the
        // ordered replacement passes below unchanged.
        $text = htmlspecialchars($text, ENT_COMPAT, 'UTF-8');
        $text = str_replace(
            array(' ', "\t", "\n", "\r"),
            array('&nbsp;', '&nbsp;&nbsp;&nbsp;&nbsp;', ' ', ''),
            $text
        );
        return preg_replace('/[\x00-\x1F\x7F]/', '', $text);
    }

    /**
    *
    * Renders a token into text matching the requested format.
    *
    * @access public
    *
    * @param array $options The "options" portion of the token (second
    * element).
    *
    * @return string The text rendered from the token options.
    *
    */

    function token($options)
    {
        $args = isset($options['args']) && is_array($options['args'])
            ? $options['args'] : array();

        $folded = true;
        if (isset($args['folded']) &&
            ($args['folded'] === 'no' || $args['folded'] === 'false')) {
            $folded = false;
        }

        $show = $this->wikidotLabel(isset($args['show']) ? $args['show'] : null, true);
        $hide = $this->wikidotLabel(isset($args['hide']) ? $args['hide'] : null, false);

        $hideLocation = 'top';
        if (isset($args['hideLocation'])) {
            if ($args['hideLocation'] === 'bottom') {
                $hideLocation = 'bottom';
            } elseif ($args['hideLocation'] === 'both') {
                $hideLocation = 'both';
            }
        }

        $hideB = '<div class="collapsible-block-unfolded-link">'
            . '<a class="collapsible-block-link" href="javascript:;">' . $hide . '</a>'
            . '</div>';

        if (isset($options['type']) && $options['type'] === 'start') {
            $out = '<div class="collapsible-block">';
            $out .= '<div class="collapsible-block-folded"'
                . ($folded ? '' : ' style="display:none"') . '>'
                . '<a class="collapsible-block-link" href="javascript:;">' . $show . '</a>'
                . '</div>';
            $out .= '<div class="collapsible-block-unfolded"'
                . ($folded ? ' style="display:none"' : '') . '>';
            if ($hideLocation === 'top' || $hideLocation === 'both') {
                $out .= $hideB;
            }
            $out .= '<div class="collapsible-block-content">';
            return $out;
        }

        if (isset($options['type']) && $options['type'] === 'end') {
            $out = '</div>';
            if ($hideLocation === 'bottom' || $hideLocation === 'both') {
                $out .= $hideB;
            }
            $out .= '</div></div>';
            return $out;
        }
    }
}
