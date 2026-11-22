<?php
// vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
/**
 * Url rule end renderer for Xhtml
 *
 * PHP versions 4 and 5
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    $Id: Url.php,v 1.5 2008/08/28 11:34:22 redbeard Exp $
 * @link       http://pear.php.net/package/Text_Wiki
 */

/**
 * This class renders URL links in XHTML.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Url extends Text_Wiki_Render {

    public $conf = array(
        //'target' => '_blank',
        'images' => true,
        'img_ext' => array('jpg', 'jpeg', 'gif', 'png'),
        'css_inline' => null,
        'css_footnote' => null,
        'css_descr' => null,
        'css_img' => null
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
        // create local variables from the options array (text,
        // href, type)
        extract($options);

        // find the rightmost dot and determine the filename
        // extension.
        $pos = strrpos($href, '.');
        $ext = strtolower(substr($href, $pos + 1));
        $href0 = $href;
        // F-R2-68 correction (coordinator, 2026-11-20): live percent-encodes
        // non-ASCII bytes in the emitted href (relay probe
        // muse-probe-req-nbsp-url: the NBSP in an autolink href renders as
        // %C2%A0, exactly as ftml has it; the reference kept the raw byte).
        // Same bytewise encoding as the Image renderer's encodeNonAscii.
        $href = preg_replace_callback('/[^\x00-\x7F]/', function ($m) {
            $bytes = unpack('C*', $m[0]);
            $out = '';
            foreach ($bytes as $byte) {
                $out .= '%' . strtoupper(str_pad(dechex($byte), 2, '0', STR_PAD_LEFT));
            }
            return $out;
        }, $href);
        $href = htmlspecialchars($href, ENT_COMPAT, 'UTF-8');
        if($href=="#"){
        	$href="javascript:;";
        }

        // does the filename extension indicate an image file?
        if ($this->getConf('images') &&
            in_array($ext, $this->getConf('img_ext', array()))) {

            // create alt text for the image
            if (! isset($text) || $text == '') {
                $text = basename($href);
                $text = htmlspecialchars($text, ENT_COMPAT, 'UTF-8');
            }

            // generate an image tag
            $css = $this->formatConf(' class="%s"', 'css_img');
            $output = "<img$css src=\"$href\" alt=\"$text\" />";

        } else {

            // R2-inline1 C3: live's Wikidot renderer spells the new-tab clause
            // as target="_blank" (corpus pin
            // test/link/star-killed-autolink-fallback/wikidot.html); the fossil
            // emitted an onclick window.open fragment.
            // REFCORR3 C-SUSPECT-INLINE-1/2: the fossil's extra suppression of
            // the authored target on on-page anchors and mailto: links is NOT
            // live behavior. Fresh probes muse-probe-suspect-inline-url-anchor-star,
            // -url-anchor-star2, -url-mailto-lower and -url-mailto-star2 show live
            // keeping target="_blank" on all four, while the reference dropped it;
            // the unstarred controls keep no target on both sides. The suppression
            // block is therefore removed. The "#" -> "javascript:;" substitution
            // above is unaffected. The HTMLCHARS ENT_COMPAT escapes are kept.
            $target = isset($options['target']) ? $options['target'] : $this->getConf('target');

            // generate a regular link (not an image)
            $text = htmlspecialchars($text, ENT_COMPAT, 'UTF-8');
            $css = $this->formatConf(' class="%s"', "css_$type");
            $output = "<a$css href=\"$href\"";

            if ($target) {
                $target = htmlspecialchars($target, ENT_COMPAT, 'UTF-8');
                $output .= " target=\"$target\"";
            }

            // finish up output
            $output .= ">$text</a>";

            // make numbered references look like footnotes when no
            // CSS class specified, make them superscript by default
            if ($type == 'footnote' && ! $css) {
                $output = '<sup>' . $output . '</sup>';
            }
        }

        /* Add to array of external links. */
        $wiki = $this->wiki;
		if($wiki->vars['externalLinks'] == null){
			$wiki->vars['externalLinks'] = array();	
		}
		if(preg_match(';^https?://;', $href0)){
			$href0 = substr($href0,0,2000);
			$wiki->vars['externalLinks'][$href0]=$href0;
		}

           
        return $output;
    }
}
