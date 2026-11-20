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
 * Module.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Module extends Text_Wiki_Render {
    
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
        $moduleName = $options['moduleName'];
        $siteName = $GLOBALS['site']->getUnixName();
        // check if the site is allowed to use this module
        $mm = ModuleManager::instance();
        if ($mm->canWikiUseModule($siteName, $moduleName) == false) {
            // R2 MODULE CORRECTION (2026-11-20): the fossil's "does not exist
            // or can not be used within this site" wording is a fossil-era
            // artifact. Live Wikidot (saved anonymous page view, probes
            // muse-probe-r2mod-module-mod-unknown, -mod-attr-on-unknown,
            // -mod-name-leading-digit, -mod-name-leading-underscore and
            // -mod-name-slash) renders the "No such module" error block with
            // a doc:modules link and no rel attribute, byte-for-byte as
            // below; ftml's wikidot_unknown_module_error matches it.
            $message = sprintf(_('[[module <em>%s</em>]] No such module, please <a href="https://www.wikidot.com/doc:modules" target="_blank">check available modules</a> and fix this page.'), $moduleName);
            return $this->renderError($message);
        }
        
        $attr = $options['attr'];
        if ($options['module_body']) {
            $attr .= ' module_body="' . urlencode($options['module_body']) . '"';
        }
        $templateName = $mm->resolveWikiModuleName($moduleName);
        $d = utf8_encode("\xFE");
        $out = $d . "module \"" . $templateName . "\"";
        if ($attr !== null && $attr !== '') {
            $out .= " " . urlencode($attr) . " ";
        }
        $out .= $d;
        
        return $out;
    }
}
