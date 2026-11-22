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
                // a dangerous scheme in the src attribute makes the
                // whole embed render empty on live Wikidot
                if (preg_match('/\bsrc\s*=\s*"([^"]*)"/i', $content, $sm)) {
                    $srcScheme = strtolower(trim($sm[1]));
                    if (strpos($srcScheme, 'javascript:') === 0 || strpos($srcScheme, 'vbscript:') === 0) {
                        return '';
                    }
                }
                // check for js events
                $eventpattern = 'on[a-z]+';
                $eventpattern = ';<[^>]*\s+' . $eventpattern . '\s*=[^>]+>;si';
                if (preg_match($eventpattern, $content)) {
                    break;
                }
                // a dangerous scheme in any other attribute value
                // falls through to the no-match error on live Wikidot
                $badScheme = false;
                if (preg_match_all('/[a-zA-Z0-9_-]+\s*=\s*"([^"]*)"/', $content, $am)) {
                    foreach ($am[1] as $attrValue) {
                        $lv = strtolower($attrValue);
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
