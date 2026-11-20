<?php
// vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
/**
 * Include rule end renderer for Xhtml
 *
 * PHP versions 4 and 5
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    $Id$
 * @link       http://pear.php.net/package/Text_Wiki
 */

class Text_Wiki_Render_Xhtml_Include extends Text_Wiki_Render {

    public $conf = array();

    /**
     * Renders an Include token when present (missing-page error block fallback).
     */
    function token($options)
    {
        if (isset($options['type']) && $options['type'] === 'missing') {
            $pageName = isset($options['page']) ? $options['page'] : '';
            $siteName = isset($options['site']) ? $options['site'] : null;
            $href = ($siteName !== null && $siteName !== '')
                ? 'https://' . $siteName . '.wikidot.com/' . $pageName . '/edit/true'
                : '/' . $pageName . '/edit/true';
            return '<div class="error-block">' . "\n"
                . '<p>Included page &quot;' . htmlspecialchars($pageName, ENT_COMPAT, 'UTF-8')
                . '&quot; does not exist (<a href="' . htmlspecialchars($href, ENT_COMPAT, 'UTF-8')
                . '">create it now</a>)</p>' . "\n"
                . '</div>';
        }
        return '';
    }
}
?>
