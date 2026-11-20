<?php
// vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
/**
  * List rule end renderer for Xhtml
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
  * This class renders bullet and ordered lists in XHTML.
  *
  * A nested list opens on a new line inside its parent item and closes with
  * a newline before the parent item closes. A depth skip is carried by an
  * inline list-item wrapper whose close has no trailing newline. These are
  * the shapes observed on live saved pages and in the ftml list pins; they
  * replace the fossil's pretty-printing tabs and inline nested tags.
  *
  * @category   Text
  * @package    Text_Wiki
  * @author     Paul M. Jones <pmjones@php.net>
  * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
  * @version    Release: @package_version@
  * @link       http://pear.php.net/package/Text_Wiki
  */
class Text_Wiki_Render_Xhtml_List extends Text_Wiki_Render {

    public $conf = array(
        'css_ol' => null,
        'css_ol_li' => null,
        'css_ul' => null,
        'css_ul_li' => null
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
        // make nice variables (type, level, count)
        extract($options);

        $bullet = (strpos($type, 'bullet_') === 0);
        $tag = $bullet ? 'ul' : 'ol';
        $inSublist = ! empty($in_sublist);
        $tailSublist = (isset($tail) && $tail === 'sublist');

        switch ($type) {

        case 'bullet_list_start':
        case 'number_list_start':
            $css = $this->formatConf(
                ' class="%s"', $bullet ? 'css_ul' : 'css_ol'
            );
            $typeAttr = '';
            if (! $bullet && isset($format) && $format !== '') {
                $typeAttr = ' type="' . $format . '"';
            }
            $html = "<{$tag}{$typeAttr}{$css}>\n";
            if ($level > 0 && ! $inSublist) {
                $html = "\n" . $html;
            }
            return $html;
            break;

        case 'bullet_list_end':
        case 'number_list_end':
            if ($tailSublist) {
                $html = "</{$tag}>";
            } else {
                $html = "</li>\n</{$tag}>";
            }
            if (($level > 0 && ! $inSublist)
                || ($level === 0 && $tailSublist)) {
                $html .= "\n";
            }
            return $html;
            break;

        case 'sublist_start':
            return '<li style="list-style: none; display: inline">';
            break;

        case 'sublist_end':
            return '</li>';
            break;

        case 'bullet_item_start':
        case 'number_item_start':
            $css = $this->formatConf(
                ' class="%s"', $bullet ? 'css_ul_li' : 'css_ol_li'
            );
            $html = "<li{$css}>";
            if ($count > 0) {
                $html = "</li>\n" . $html;
            }
            return $html;
            break;

        case 'bullet_item_end':
        case 'number_item_end':
        default:
            // item endings are emitted by the next item start or the list end
            return '';
            break;
        }
    }
}
