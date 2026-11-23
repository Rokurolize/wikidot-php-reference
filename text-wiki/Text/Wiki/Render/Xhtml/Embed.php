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
 * Renders embedded code.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Embed extends Text_Wiki_Render {
    
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
    
    public $patterns = array();

    public function __construct($obj) {
        parent::__construct($obj);
        
        $patternDir = WIKIDOT_ROOT . '/conf/wikiparser/embed';
        $files = glob($patternDir . '/*.php');
        foreach ($files as $f) {
            require $f;
            $this->_patterns = array_merge($this->patterns, $patterns);
        }
    
    }

    function token($options) {
        
        $content = trim($options['content']);
        
        foreach ($this->_patterns as $pattern) {
            if (preg_match($pattern, $content)) {
                $content = preg_replace('/language="JavaScript[^"]*"/i', '', $content);
                // C-SUSPECT-CODEEMBED-6: an event handler is rejected even
                // when glued to the preceding attribute with no whitespace.
                // C-SUSPECT-CODEEMBED-2: the event check precedes the src
                // check, so content with both fires the error block.
                $eventpattern = 'on[a-z]+';
                // REFCORR13 D01: the event name must start at a word
                // boundary. Live accepts longdesc, content and
                // 1onclick (their `on` is glued to a preceding word
                // byte) while still rejecting an `onclick` glued to a
                // closing quote. PHP `\b` at the leading `o` is exactly
                // the negative lookbehind (?<![A-Za-z0-9_]).
                $eventpattern = ';<[^>]*\b' . $eventpattern . '\s*=[^>]+>;si';
                if (preg_match($eventpattern, $content)) {
                    break;
                }
                // C-SUSPECT-CODEEMBED-3/4: src accepts either quote style,
                // and a word boundary that excludes '-' keeps data-src out;
                // a real script-scheme src still renders empty (se02/se06).
                if (preg_match("/(?<![a-zA-Z0-9_-])src\s*=\s*([\"'])([^\"']*)\\1/i", $content, $sm)) {
                    $srcScheme = strtolower(trim($sm[2]));
                    if (strpos($srcScheme, 'javascript:') === 0 || strpos($srcScheme, 'vbscript:') === 0) {
                        return '';
                    }
                }
                // C-SUSPECT-CODEEMBED-5: the generic contains test applies
                // to other attributes only; src is prefix-tested above.
                $badScheme = false;
                if (preg_match_all('/(?<![a-zA-Z0-9_-])([a-zA-Z0-9_-]+)\s*=\s*"([^"]*)"/i', $content, $am, PREG_SET_ORDER)) {
                    foreach ($am as $attr) {
                        if (strtolower($attr[1]) === 'src') {
                            continue;
                        }
                        $lv = strtolower($attr[2]);
                        if (strpos($lv, 'javascript:') !== false || strpos($lv, 'vbscript:') !== false) {
                            $badScheme = true;
                            break;
                        }
                    }
                }
                if ($badScheme) {
                    break;
                }
                return $content;
            }
        }
        
        //no match...
        return '<div class="error-block">Sorry, no match for the embedded content.</div>';
    
    }
}
