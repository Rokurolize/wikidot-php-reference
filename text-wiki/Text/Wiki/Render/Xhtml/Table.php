<?php
// vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
/**
 * Table rule end renderer for Xhtml
 *
 * PHP versions 4 and 5
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    $Id$
 * @link       http://pear.php.net/package/Text_Wiki
 */

/**
 * This class renders tables in XHTML.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Table extends Text_Wiki_Render {

    public $conf = array(
        'css_table' => null,
        'css_caption' => null,
        'css_tr' => null,
        'css_th' => null,
        'css_td' => null
    );

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

    function token($options)
    {
        // make nice variable names (type, attr, span)
        $span = $rowspan = 1;
        extract($options);

        // Free format is an optional caller-supplied attribute fragment; when
        // absent it contributes nothing. R2-Table correction C1: the fossil
        // wrote a bare space before '>' on every cell tag and pretty-printed
        // tables with four/eight-space indents and blank lines around the
        // whole table. Live Wikidot and the pinned wikidot.html corpus emit
        // no indent, no surrounding blank lines, and no stray attribute
        // space, so those fossil-era artifacts are removed here. The newline
        // after cell_end is live truth and is kept.

        $format = isset($format) ? ' '. $format : '';

        switch ($type) {

        case 'table_start':
            $css = $this->formatConf(' class="%s"', 'css_table');
            return "<table$css$format>\n";
            break;

        case 'table_end':
            return "</table>";
            break;

        case 'caption_start':
            $css = $this->formatConf(' class="%s"', 'css_caption');
            return "<caption$css$format>\n";
            break;

        case 'caption_end':
            return "</caption>\n";
            break;

        case 'row_start':
            $css = $this->formatConf(' class="%s"', 'css_tr');
            return "<tr$css$format>\n";
            break;

        case 'row_end':
            return "</tr>\n";
            break;

        case 'cell_start':

            // base html
            $html = '';

            // is this a TH or TD cell?
            if ($attr == 'header') {
                // start a header cell
                $css = $this->formatConf(' class="%s"', 'css_th');
                $html .= "<th$css";
            } else {
                // start a normal cell
                $css = $this->formatConf(' class="%s"', 'css_td');
                $html .= "<td$css";
            }

            // add the column span
            if ($span > 1) {
                $html .= " colspan=\"$span\"";
            }

            // add the row span
            if ($rowspan > 1) {
                $html .= " rowspan=\"$rowspan\"";
            }

            // add alignment
            if ($attr != 'header' && $attr != '') {
                $html .= " style=\"text-align: $attr;\"";
            }

            // done!
            $html .= "$format>";
            return $html;
            break;

        case 'cell_end':
            if ($attr == 'header') {
                return "</th>\n";
            } else {
                return "</td>\n";
            }
            break;

        default:
            return '';

        }
    }
}
