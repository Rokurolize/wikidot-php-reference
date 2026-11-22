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
 * Advanced table renderer, corrected against live Wikidot behavior.
 *
 * The advanced table form carries no automatic css class; only authored
 * attributes are emitted, sorted by name. Tag bodies are laid out with the
 * newlines live uses, and a header cell close is determined by the token's
 * header flag set from the authored closer name.
 */
class Text_Wiki_Render_Xhtml_Tableadv extends Text_Wiki_Render {

    public $conf = array();

    function token($options) {
        $type = isset($options['type']) ? $options['type'] : '';
        $attrs = isset($options['attrs']) && is_array($options['attrs'])
            ? $options['attrs'] : array();
        $rendered = '';
        foreach ($attrs as $key => $value) {
            $rendered .= ' ' . $key . '="'
                . htmlspecialchars((string)$value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')
                . '"';
        }
        $header = !empty($options['header']);
        $tag = $header ? 'th' : 'td';

        if ($type === 'start') {
            return '<table' . $rendered . ">\n";
        }
        if ($type === 'rowStart') {
            return '<tr' . $rendered . ">\n";
        }
        if ($type === 'cellStart') {
            return '<' . $tag . $rendered . '>';
        }
        if ($type === 'cellEnd') {
            return '</' . $tag . ">\n";
        }
        if ($type === 'rowEnd') {
            return "</tr>\n";
        }
        if ($type === 'end') {
            return '</table>';
        }
        return '';
    }
}
