<?php
// vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
/**
 * Blockquote rule end renderer for Xhtml
 *
 * PHP versions 4 and 5
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    $Id$
 * @link       http://pear.php.net/package/Text_Wiki
 */

/**
 * This class renders a blockquote in XHTML.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Blockquote extends Text_Wiki_Render {

    public $conf = array(
        'css' => null
    );

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
        $type = $options['type'];
        $level = $options['level'];

        // R2-BLOCK C1: the fossil pretty-printed nested blockquotes with four
        // spaces per level. Live (saved-page probes and ftml's corpus pins)
        // emits no such padding, and the level is not part of the observable
        // blockquote shape, so the padding is removed. $level stays in the
        // token options for downstream compatibility.

        // pick the css type
        $css = $this->formatConf(' class="%s"', 'css');

        // starting
        if ($type == 'start') {
            return "<blockquote$css>";
        }

        // ending
        if ($type == 'end') {
            return "</blockquote>\n";
        }
    }
}
