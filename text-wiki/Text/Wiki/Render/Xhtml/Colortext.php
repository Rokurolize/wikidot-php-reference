<?php
// vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
/**
 * Colortext rule end renderer for Xhtml
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
 * This class renders colored text in XHTML.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Colortext extends Text_Wiki_Render {

    public $colors = array(
        'aqua',
        'black',
        'blue',
        'fuchsia',
        'gray',
        'green',
        'lime',
        'maroon',
        'navy',
        'olive',
        'purple',
        'red',
        'silver',
        'teal',
        'white',
        'yellow'
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
        $raw = $options['color'];
        $color = $this->normalizeColor($raw);

        // Live Wikidot (and ftml in its Wikidot layout) only form a color
        // span for a spec whose bytes are alphanumerics or one of #(),- and
        // space. A spec outside that class stays literal source text: the
        // opener restores "##color|" and the closer restores "##", with the
        // body (carried untouched between the two tokens) in between.
        if ($color === null) {
            return $type == 'start' ? '##' . $raw . '|' : '##';
        }

        if ($type == 'start') {
            // A whitespace-only color field collapses to the empty spec, which
            // live renders as style="color:" with no space after the colon.
            if ($color === '') {
                return '<span style="color:">';
            }
            // The Wikidot style string carries no trailing semicolon; the
            // fossil inherited one from the non-Wikidot Text_Wiki styling
            // tradition. Live's saved pages and ftml's legacy render omit it.
            return "<span style=\"color: $color\">";
        }

        if ($type == 'end') {
            return '</span>';
        }
    }

    /**
     * Normalize a color spec the way live Wikidot (and ftml's Wikidot layout)
     * normalize_wikidot_color does: collapse runs of spaces and tabs, lowercase,
     * fold a 3- or 6-digit hex spec to a #-prefixed lowercase form, and admit
     * only specs built from alphanumerics and #(),- and space. A whitespace-only
     * field collapses to the empty string, which live admits. Returns null for
     * a spec outside that class, in which case the color pair does not form.
     */
    function normalizeColor($color)
    {
        $parts = preg_split('/[ \t]+/', $color, -1, PREG_SPLIT_NO_EMPTY);
        $collapsed = strtolower(implode(' ', $parts));
        $hex = substr($collapsed, 0, 1) === '#' ? substr($collapsed, 1) : $collapsed;
        if ((strlen($hex) === 3 || strlen($hex) === 6) && ctype_xdigit($hex)) {
            return '#' . $hex;
        }
        if (preg_match('/^[A-Za-z0-9#(),\- ]*$/D', $collapsed)) {
            return $collapsed;
        }
        return null;
    }
}
