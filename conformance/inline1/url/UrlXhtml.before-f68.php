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
        $href = htmlspecialchars($href);
        if($href=="#"){
        	$href="javascript:;";
        }

        // does the filename extension indicate an image file?
        if ($this->getConf('images') &&
            in_array($ext, $this->getConf('img_ext', array()))) {

            // create alt text for the image
            if (! isset($text) || $text == '') {
                $text = basename($href);
                $text = htmlspecialchars($text);
            }

            // generate an image tag
            $css = $this->formatConf(' class="%s"', 'css_img');
            $output = "<img$css src=\"$href\" alt=\"$text\" />";

        } else {

            // R2-inline1 C3: live's Wikidot renderer spells the new-tab clause
            // as target="_blank" (corpus pin
            // test/link/star-killed-autolink-fallback/wikidot.html); the fossil
            // emitted an onclick window.open fragment. The authored target is
            // suppressed on on-page anchors and mailto: links, as before.
            $target = isset($options['target']) ? $options['target'] : $this->getConf('target');
            if ($href[0] == '#' ||
            	strtolower(substr($href, 0, 7)) == 'mailto:') {
                $target = '';
            }

            // generate a regular link (not an image)
            $text = htmlspecialchars($text);
            $css = $this->formatConf(' class="%s"', "css_$type");
            $output = "<a$css href=\"$href\"";

            if ($target) {
                $target = htmlspecialchars($target);
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
