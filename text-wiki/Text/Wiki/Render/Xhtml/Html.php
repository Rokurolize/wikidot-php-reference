<?php
// vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
/**
 * Html rule end renderer for Xhtml
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
 * This class renders preformated html in XHTML.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Html extends Text_Wiki_Render {

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

    public $conf = array(
        // Live submits the block body to a snippet service and embeds the
        // returned URL. The census/FTML handle returns this fixed stand-in;
        // production overrides the conf with the real snippet URL.
        'src' => 'https://example.com/',
        'class' => 'html-block-iframe'
    );

    function token($options)
    {
        // REFCORR19 F2: live (and FTML) render [[html]] as an iframe with the
        // html-block-iframe class, not as literal source text.
        $src = $this->getConf('src');
        $class = $this->getConf('class');
        if (!empty($options['class'])) {
            $class = trim($options['class'] . ' ' . $class);
        }
        $parts = array(
            'src="' . htmlspecialchars($src, ENT_COMPAT, 'UTF-8') . '"',
            'allowtransparency="true"',
            'frameborder="0"'
        );
        if (!empty($options['style'])) {
            $parts[] = 'style="' . htmlspecialchars($options['style'], ENT_COMPAT, 'UTF-8') . '"';
        }
        $parts[] = 'class="' . htmlspecialchars($class, ENT_COMPAT, 'UTF-8') . '"';
        return '<iframe ' . implode(' ', $parts) . '></iframe>';
    }
}
