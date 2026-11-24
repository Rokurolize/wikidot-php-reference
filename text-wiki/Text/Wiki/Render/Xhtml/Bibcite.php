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
 * Bibliography citation.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Bibcite extends Text_Wiki_Render {
    
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
        $label = $options['label'];
        // REFCORR19 F6: an unresolved label has no entry and keeps the
        // inline error span. Guarding the lookup here also removes the
        // undefined-array-key warnings this rule emitted when a document
        // had no bibliography at all.
        $bibitemIds = isset($this->wiki->vars['bibitemIds']) && is_array($this->wiki->vars['bibitemIds'])
            ? $this->wiki->vars['bibitemIds']
            : array();
        $id = isset($bibitemIds[$label]) ? $bibitemIds[$label] : null;
        $idPrefix = $this->wiki->getRenderConf('xhtml', 'bibitem', 'id_prefix');
        if ($id === null) {
            return '<span class="error-inline">Bibliography item <em>' . $label . '</em> not found.</span>';
        }
        // REFCORR19 F6: live (and FTML) emit a decimal, per-render suffix
        // followed by a literal "a": id="bibcite-<index>-<suffix>a".
        // The reference has no per-render RNG at this layer, so derive a
        // stable stand-in in live's 1000..99999 range from the label.
        // The FORM is the contract: the census comparator's volatile-ID
        // pattern bibcite-\d+-\d+ normalizes both this form and FTML's
        // to "bibcite-N", leaving the trailing a in both cases, while
        // the bare id passed through unnormalized and produced all 70
        // anchor-id differences.
        $suffix = 1000 + (crc32((string) $label) % 99000);
        $anchorId = 'bibcite-' . $id . '-' . $suffix . 'a';
        $out = '<a href="javascript:;" class="bibcite" id="' . $anchorId . '"' . ' onclick="WIKIDOT.page.utils.scrollToReference(\'bibitem-' . $idPrefix . $id . '\')">' . $id . '</a>';
        return $out;
    }
}
