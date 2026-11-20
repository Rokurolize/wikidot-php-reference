<?php
/**
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    $Id$
 * @link       http://pear.php.net/package/Text_Wiki
 */

/**
 * Inline math.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Mathinline extends Text_Wiki_Render {
     
    public $conf = array();

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
     
    function token($options) {
        // Live Wikidot's saved-page shape for [[$ ... $]] is a span holding
        // the trimmed source between literal dollar signs; the observable
        // HTML contains no generated image. The fossil's md5-named PNG path
        // and its no-PNG error span are an obsolete serving mechanism, so
        // both are replaced here. Escape as the legacy HtmlRender does:
        // ampersand, both angle brackets, double quote and apostrophe; all
        // other characters (including non-ASCII) pass through verbatim.
        $escaped = strtr($options['content'], array(
            '&' => '&amp;',
            '<' => '&lt;',
            '>' => '&gt;',
            '"' => '&quot;',
            "'" => '&#39;',
            "\0" => ' ',
        ));
        return '<span class="math-inline">$' . $escaped . '$</span>';
    }
}
