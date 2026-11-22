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
 * Render emails.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Email extends Text_Wiki_Render {

    function token($options) {
        $email = $options['email'];
        $text = $options['text'];
        
        $out = '<span class="wiki-email">';
        // REFCORR5 Batch 3 (C-SUSPECT-EMAIL-1/-2): live escapes the reversed
        // and joined string with ENT_NOQUOTES and substitutes invalid bytes
        // (including raw token delimiter bytes) with U+FFFD. Quotes stay raw.
        $out .= htmlspecialchars(
            str_replace('@', '|', strrev($email) . '#' . strrev($text)),
            ENT_NOQUOTES | ENT_SUBSTITUTE, 'UTF-8');
        $out .= '</span>';
        
        return $out;
    }
}
