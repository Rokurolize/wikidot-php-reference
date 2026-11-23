<?php
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
 * Text span.
 *
 * Live Wikidot emits a bare <span> when the attribute set is empty. The
 * fossil template prefixed every attribute with a space on top of the space
 * already present after "<span", producing "<span  ...>", and it rendered
 * even an empty attribute set; live probes muse-probe-r2contain-span-p01
 * through p34 settle the corrected form. Attribute values are escaped as
 * live escapes them (p32 and p34).
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Span extends Text_Wiki_Render {

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
        if ($options['type'] == 'start') {
            $args = $options['args'];
            $argstr = '';
            foreach ($args as $key => $value) {
                $argstr .= ' ' . $key . '="'
                    . htmlspecialchars($value, ENT_COMPAT, 'UTF-8') . '"';
            }
            return '<span' . $argstr . '>';
        }

        if ($options['type'] == 'end') {
            return "</span>";
        }

    }
}
