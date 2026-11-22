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
 * Renders a div element.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Div extends Text_Wiki_Render {
    
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
                $argstr .= ' ' . $key . '="' . $value . '"';
            }
            // R4-corr correction (fossil artifact): the fossil's literal
            // "<div " carried a space the argument string does not need:
            // with no arguments it emitted "<div >", and each argument
            // already carries its own leading space, so with arguments it
            // emitted "<div  k=\"v\">". Live emits "<div>" (captures
            // footnoteitem p-div-first, footnoteblock div-block and
            // x x-fn-in-div) and single-spaced attributes.
            return "<div" . $argstr . ">";
        }
        
        if ($options['type'] == 'end') {
            return "</div>";
        }
    
    }
}
