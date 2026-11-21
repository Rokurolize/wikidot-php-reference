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
 * Bibliography block.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Bibliography extends Text_Wiki_Render {
    
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
        // The parse rule lays out opaque newline tokens around residual
        // bibliography lines. They keep later line-anchored rules from
        // forming in the joined body while still rendering as line breaks.
        if ($options['type'] == 'nl') {
            return "\n";
        }
        //if(count($bibitems) == 0){return '';} // render nothing if no footnotes.
        if ($options['type'] == 'start') {
            $title = $options['title'];
            if ($title === null) {
                $title = _('Bibliography');
            }
            $out = '<div class="bibitems">';
            if ($title !== "") {
                // R4-corr correction (PHP-version artifact): live Wikidot
                // emits an apostrophe in the block title as a raw "'", while
                // PHP 8.1+ changed htmlspecialchars()'s default flags from
                // ENT_COMPAT to ENT_QUOTES|ENT_SUBSTITUTE, which would turn
                // it into &#039;. ENT_COMPAT restores the live shape (probe
                // muse-probe-r4c1-bib-title-apos), the same correction the
                // R2-notes stage made in Footnoteblock (probe
                // muse-probe-r2notes-fnb-title-apostrophe); &, <, > and "
                // stay escaped.
                $out .= '<div class="title">' . htmlspecialchars($title, ENT_COMPAT) . '</div>';
            }
            return $out;
        }
        if ($options['type'] == 'end') {
            return '</div>';
        }
    
    }
}
