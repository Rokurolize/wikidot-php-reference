<?php
// vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
/**
 * Anchor rule end renderer for Xhtml
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
 * This class renders an anchor target or anchor element in XHTML.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Anchor extends Text_Wiki_Render {

    public $conf = array(
        'css' => null
    );

    function token($options)
    {
        if (isset($options['type'])) {
            if ($options['type'] === 'start') {
                $attrs = isset($options['attrs']) && is_array($options['attrs'])
                    ? $options['attrs']
                    : array('href' => '');
                $out = '<a';
                foreach ($attrs as $k => $v) {
                    $escaped = htmlspecialchars($v, ENT_COMPAT, 'UTF-8');
                    $out .= ' ' . $k . '="' . $escaped . '"';
                }
                $out .= '>';
                return $out;
            }
            if ($options['type'] === 'end') {
                return '</a>';
            }
            if ($options['type'] === 'invalid_named') {
                $lead = isset($options['lead']) ? $options['lead'] : '';
                $text = isset($options['text']) ? htmlspecialchars($options['text'], ENT_COMPAT, 'UTF-8') : '';
                $trail = isset($options['trail']) ? $options['trail'] : '';
                return '[' . $lead . '<a href="javascript:;">' . $text . '</a>' . $trail . ']';
            }
            if ($options['type'] === 'literal') {
                return isset($options['text']) ? htmlspecialchars($options['text'], ENT_COMPAT, 'UTF-8') : '';
            }
        }

        $name = isset($options['name']) ? $options['name'] : '';
        $format = "<a name=\"%s\"></a>";
        return sprintf($format, htmlentities($name));
    }
}
?>
