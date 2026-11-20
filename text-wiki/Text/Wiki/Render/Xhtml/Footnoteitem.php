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
 * Footnote item.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Footnoteitem extends Text_Wiki_Render {
    
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
        // Emitted by Footnoteblock on the lead side of the first paragraph
        // break in a note body. Tighten deletes raw newlines, so the break
        // has to be a token to survive as the newline live puts before the
        // next <p> (muse-probe-r2notes-fnb24).
        if ($options['type'] == 'parabreak') {
            return "\n";
        }
        if ($options['type'] == 'start') {

            $idPrefix = $this->wiki->getRenderConf('xhtml', 'footnote', 'id_prefix');
            $id = $options['id'];
            $out = '<div class="footnote-footer" id="footnote-' . $idPrefix . $id . '">';
            $out .= '<a href="javascript:;" ' . 'onclick="WIKIDOT.page.utils.scrollToReference(\'footnoteref-' . $idPrefix . $id . '\')">' . $id . '</a>.';
            // Live emits a separator space after the back-reference only when
            // the collected note body is non-empty. The fossil appended it
            // unconditionally, leaving a stray space before </div> on an empty
            // note; live settles this on muse-probe-r2notes-fni-p-empty and
            // -p-empty-ws (both fold a whitespace-only body to empty because
            // Footnote::process trims the collected content). Footnote::process
            // stores the trimmed body at vars['footnotes'][id - 1], so the same
            // state the block render reads is available here.
            $footnotes = $this->wiki->vars['footnotes'] ?? array();
            $body = $footnotes[$id - 1] ?? '';
            if ($body !== '') {
                $out .= ' ';
            }
            return $out;
        }
        if ($options['type'] == 'end') {
            $out = '</div>';
            return $out;
        }
    }
}
