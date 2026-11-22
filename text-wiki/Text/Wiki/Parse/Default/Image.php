<?php

/**
 *
 * Parses for image placement.
 *
 * @category Text
 *
 * @package Text_Wiki
 *
 * @author Paul M. Jones <pmjones@php.net>
 * @author Michal Frackowiak
 *
 * @license LGPL
 *
 * @version $Id$
 *
 */

/**
 *
 * Parses for image placement.
 *
 * @category Text
 *
 * @package Text_Wiki
 *
 * @author Paul M. Jones <pmjones@php.net>
 * @author Michal Frackowiak
 *
 */

class Text_Wiki_Parse_Image extends Text_Wiki_Parse {
    
    /**
     * URL schemes recognized by this rule.
     *
     * @access public
     * @var array
     */
    public $conf = array('schemes' => 'http|https|ftp|gopher|news', 
        'host_regexp' => '(?:[^.\s/"\'<\\\#delim#\ca-\cz]+\.)*[a-z](?:[-a-z0-9]*[a-z0-9])?\.?', 
        'path_regexp' => '(?:/[^\s"<\\\#delim#\ca-\cz]*)?');
    
    /**
     *
     * The regular expression used to find source text matching this
     * rule.
     *
     * @access public
     *
     * @var string
     *
     */
    
    // R2-PARA correction C2: the fossil consumed an optional `[[/image]]`
    // closer and captured its body as a "caption" that the renderer never
    // used. Live (probes p01 and p02) and the pinned ftml behaviour leave the
    // body and the unmatched `[[/image]]` as ordinary text after the image,
    // and corpus pin image/basic shows no caption wrapper. C4: an empty head
    // (`[[image ]]`) is a real live image with an empty filename (probe p07
    // and pin image/empty-head), so the source group is `.*?` rather than
    // `.+?`. The alignment/name prefix group is unchanged.
    public $regex = '/(\[\[((?:f)?[<>=])?image\s+)(.*?)\]\]/is';

    /**
     * The regular expressions used to check ecternal urls
     *
     * @access public
     * @var string
     * @see parse()
     */
    public $url = '';

    /**
     * Constructor.
     * We override the constructor to build up the url regex from config
     *
     * @param object &$obj the base conversion handler
     * @return The parser object
     * @access public
     */
    function __construct(&$obj) {
        $default = $this->conf;
        parent::__construct($obj);
        
        // convert the list of recognized schemes to a regex OR,
        $schemes = $this->getConf('schemes', $default['schemes']);
        // REFCORR3 C-SUSPECT-SERVING-3: anchor the scheme at the head of the
        // link value. The old unanchored pattern claimed a value whose only
        // valid scheme appears embedded later (link="://x http://example.com/y")
        // and rendered a malformed clickable image; live leaves the whole
        // opener literal. The accepted controls (http, gopher) are unchanged.
        $this->url = str_replace('#delim#', $this->wiki->delim, '#^(?:' . (is_array($schemes) ? implode('|', $schemes) : $schemes) . ')://' . $this->getConf('host_regexp', $default['host_regexp']) . $this->getConf('path_regexp', $default['path_regexp']) . '#');
    }

    /**
     *
     * Generates a token entry for the matched text.  Token options are:
     *
     * 'src' => The image source, typically a relative path name.
     *
     * 'opts' => Any macro options following the source.
     *
     * @access public
     *
     * @param array &$matches The array of matches from parse().
     *
     * @return A delimited token number to be used as a placeholder in
     * the source text.
     *
     */
    
    function process($matches) {
        // R2-PARA correction C7: a complete raw inline construct (`@@...@@`)
        // in the opener head makes live reject the whole image block and
        // leave the opener literal, with the raw token rendered in place
        // (pin image/raw-head-literal, battery i37-67). By the time this rule
        // runs the Raw rule has replaced that construct with a delimited
        // token, so detect the delimiter and bail out with the original
        // matched text; the token then resolves normally in the source.
        if (strpos($matches[0], $this->wiki->delim) !== false) {
            return $matches[0];
        }

        $pos = strpos($matches[3], ' ');
        
        if ($pos === false) {
            $options = array('src' => $matches[3], 
                'attr' => array());
        } else {
            // everything after the space is attribute arguments

            // from the list of arguments leave ONLY:
            // class, link and style
            $attr = $this->getAttrs(substr($matches[3], $pos + 1));
            $attr2 = array();
            // R2-PARA correction C1: live emits a `title` attribute (probes
            // p09 and p17 and pin image/basic) and it precedes style, class,
            // alt, height and width in live's fixed attribute order. The
            // fossil whitelist omitted it entirely. Putting it first in the
            // option array makes the renderer's existing attribute loop emit
            // it in that position without disturbing the other attributes.
            if (isset($attr['title'])) {
                $attr2['title'] = $attr['title'];
            }
            if (isset($attr['link'])) {
                $attr2['link'] = $attr['link'];
            }
            if (isset($attr['style'])) {
                $attr2['style'] = $attr['style'];
            }
            if (isset($attr['class'])) {
                $attr2['class'] = $attr['class'];
            }
            if (isset($attr['alt'])) {
                $attr2['alt'] = $attr['alt'];
            }
            if (isset($attr['height'])) {
                $attr2['height'] = $attr['height'];
            }
            if (isset($attr['width'])) {
                $attr2['width'] = $attr['width'];
            }
            if (isset($attr['size'])) {
                $attr2['size'] = strtolower($attr['size']);
            }
            $options = array(
                'src' => substr($matches[3], 0, $pos), 
                'attr' => $attr2);

            // fix the target="_blank"

            $link = isset($options['attr']['link']) ? $options['attr']['link'] : null;
            if ($link && $link[0] == '*') {
                $link = substr($link, 1);
                $options['target'] = '_blank';
                $options['attr']['link'] = $link;
            }

            // R2-PARA correction C3: a link value that starts with whitespace,
            // either directly or after the new-tab `*`, is not accepted by
            // live; the whole opener stays literal (probes p03 and p04, pin
            // image/basic's `link=" https://..."` row). The fossil accepted
            // it and emitted a broken href with a leading space.
            if (isset($options['attr']['link']) && $options['attr']['link'] !== ''
                && ctype_space($options['attr']['link'][0])) {
                return $matches[0];
            }

            // check the scheme case of external link
            if (array_key_exists('link', $options['attr'])) {
                // external url ?
                if (($pos = strpos($options['attr']['link'], '://')) !== false) {
                    if (!preg_match($this->url, $options['attr']['link'])) {
                        return $matches[0];
                    }
                } elseif (in_array('Wikilink', $this->wiki->disable)) {    //         return $matches[0]; // Wikilink disabled
                }
            }
        }
        
        $align = $matches[2];
        
        if ($align != null && $align !== '') {
            $options['align'] = $align;
        }
        
        // R2-PARA correction C2: the caption option sourced from the removed
        // [[/image]] group is gone; live keeps any text after the image as
        // ordinary source text (probes p01 and p02).

        // fix the target="_blank"

        $src = $options['src'];
        if ($src && $src[0] == '*') {
            $src = substr($src, 1);
            $options['target'] = '_blank';
            $options['src'] = $src;
        }
        
        // REFCORR6: the alignment newlines are returned outside the
        // token; the claimed source span is the whole [[image ...]].
        return ($align ? "\n\n" : '') . $this->wiki->addToken($this->rule, $options, false, $matches[0]) . ($align ? "\n\n" : '');
    }
}
