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
 * Iframe element.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Iframe extends Text_Wiki_Render {

    function token($options){
       
        $parts = array();
        foreach($options as $k => $o){
            $value = ($k === 'src') ? $this->percentEncodeNonAscii((string)$o) : (string)$o;
            // ENT_COMPAT restores the pre-8.1 default so a single quote stays literal, as live emits it.
            $parts[] = $k.'="'.htmlspecialchars($value, ENT_COMPAT | ENT_HTML401, 'UTF-8').'"';
        }
        return '<iframe '.implode(' ', $parts).'></iframe>';
    }

    function percentEncodeNonAscii($value){
        return preg_replace_callback('/[\x80-\xFF]/', function($m){
            return sprintf('%%%02X', ord($m[0]));
        }, $value);
    }
}
