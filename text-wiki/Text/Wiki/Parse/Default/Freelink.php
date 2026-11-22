<?php

/**
* 
* Parses for wiki freelink text.
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
* Parses for freelinked page links.
* 
* This class implements a Text_Wiki_Parse to find source text marked as a
* wiki freelink, and automatically create a link to that page.
* 
* A freelink is any page name not conforming to the standard
* StudlyCapsStyle for a wiki page name.  For example, a page normally
* named MyHomePage can be renamed and referred to as ((My Home Page)) --
* note the spaces in the page name.  You can also make a "nice-looking"
* link without renaming the target page; e.g., ((MyHomePage|My Home
* Page)).  Finally, you can use named anchors on the target page:
* ((MyHomePage|My Home Page#Section1)).
*
* @category Text
* 
* @package Text_Wiki
* 
* @author Paul M. Jones <pmjones@php.net>
* @author Michal Frackowiak
* 
*/

class Text_Wiki_Parse_Freelink extends Text_Wiki_Parse {

    /**
    * 
    * Constructor.  We override the Text_Wiki_Parse constructor so we can
    * explicitly comment each part of the $regex property.
    * 
    * @access public
    * 
    * @param object &$obj The calling "parent" Text_Wiki object.
    * 
    */
    
    function __construct(&$obj)
    {
    
        parent::__construct($obj);
        
//        $this->regex =
//            '/' .                                                   // START regex
//            "\\[\\[\\[" .                                               // double open-parens
//            "(" .                                                   // START freelink page patter
//            "[^\\]\\|\\[\#]+" . // 1 or more of just about any character
//            ")" .                                                   // END  freelink page pattern
//            "(" .                                                   // START display-name
//            "\|" .                                                   // a pipe to start the display name
//            "[^\\]\\|\\[\#]*" . // 1 or more of just about any character
//            ")?" .                                                   // END display-name pattern 0 or 1
//            "(" .                                                   // START pattern for named anchors
//            "\#" .                                                   // a hash mark
//            "[A-Za-z]" .                                           // 1 alpha
//            "[-A-Za-z0-9_:.]*" .                                   // 0 or more alpha, digit, underscore
//            ")?" .                                                   // END named anchors pattern 0 or 1
//            "()\\]\\]\\]" .                                           // double close-parens
//            '/';                                                   // END regex

		              $this->regex =
            '/'.                                        // START regex
            "\\[\\[\\[".                            // triple open
            "([^\\]\\[]+?)".                          // target (no brackets, non-greedy)
            "(\\|[^\\]\\[]*)?".                    // optional pipe label (pipes allowed)
            "\\]\\]\\]".                            // triple close
            '/';                                        // END regex
    }


    /**
     * Live-shaped freelink processing. The fossil regex captured a page, an
     * optional alpha-initial anchor and a pipe-free label; live Wikidot treats
     * the whole bracket interior as a target with any number of pipes in the
     * label, allows digit-initial anchors, transliterates non-ASCII page names,
     * strips a leading _default: category, recognizes /#/ hash routes, and
     * links bare URLs externally. The corrections are numbered C1-C6 in
     * conformance-refphp/link/freelink/SECTION.md; every shape changed here was
     * settled by the frozen live captures in this directory.
     */
    function process($matches)
    {
        // C-SUSPECT-XRULE-1: an earlier rule's placeholder inside the target
        // (or label) means the bracket form is not a link on live. Bail out
        // with the whole match literal, following the Image rule's guard,
        // so the inner token resolves normally in the source.
        if (strpos($matches[0], $this->wiki->delim) !== false) {
            return $matches[0];
        }

        $raw = isset($matches[1]) ? $matches[1] : '';
        $labelRaw = isset($matches[2]) ? $matches[2] : '';

        // Live leaves a genuinely empty target and an anchor-only target with
        // no leading space literal ([[[|Label]]], [[[#a|L]]], [[[#a]]]).
        if ($raw === '' || $raw[0] === '|') {
            return $matches[0];
        }
        if (preg_match('/^#[^ \t]/', $raw)) {
            return $matches[0];
        }

        // C1/C2: malformed multi-hash targets stay literal, matching live and
        // the ftml corpus pins (home###, a##b, a#b#c). A /#/ hash route is the
        // one exception and is handled below.
        if (strpos($raw, '##') !== false && strpos($raw, '/#/') === false) {
            return $matches[0];
        }
        if (substr_count($raw, '#') > 1 && strpos($raw, '/#/') === false) {
            return $matches[0];
        }

        // C1: peel an anchor or a hash-route suffix off the target. A leading
        // space before a hash is part of the target, so '[[[ #a | L ]]]'
        // yields an empty page with anchor #a, which live renders as /#a.
        $anchor = '';
        $extra = '';
        if (strpos($raw, '/#/') !== false) {
            list($base, $rest) = explode('/#/', $raw, 2);
            $raw = $base;
            $extra = '#/' . $rest;
        } elseif (($hashPos = strpos($raw, '#')) !== false) {
            $anchor = rtrim(substr($raw, $hashPos));
            $raw = substr($raw, 0, $hashPos);
        }

        $leadingSpace = (bool) preg_match('/^[ \t]/', $raw);
        $trimmed = trim($raw);

        // REFCORR3 C-SUSPECT-SERVING-2: a leading star is live's new-tab
        // marker on an external URL triple link, not part of the target. The
        // old test passed the starred target to freelink_is_url, so it was
        // slugified into a local newpage link. Only the starred URL branch
        // changes; plain URLs and local star-prefixed page names stay as-is.
        $starUrl = false;
        if (! $leadingSpace && isset($trimmed[0]) && $trimmed[0] === '*') {
            $starUrl = true;
            $trimmed = substr($trimmed, 1);
        }

        // C5: a bare, non-leading-space URL is an external link. The label is
        // the URL itself when no pipe label was authored.
        $url = null;
        if (! $leadingSpace && freelink_is_url($trimmed)) {
            $url = $trimmed;
            if ($labelRaw === '') {
                $text = $url;
            } else {
                $text = substr($labelRaw, 1);
            }
            $options = array(
                'site' => null,
                'page' => '',
                'text' => $text,
                'anchor' => '',
                'extra' => '',
                'url' => $url,
                'textFromTitle' => null,
            );
            // Only a starred URL adds the target option, so the pinned
            // plain-URL token shape is byte-unchanged.
            if ($starUrl) {
                $options['target'] = '_blank';
            }
            // REFCORR6: the whole triple-bracket form is the claimed span.
            return $this->wiki->addToken($this->rule, $options, false, $matches[0]);
        }

        // C6: non-ASCII page names go through ftml's explicit transliteration
        // table; unmapped characters act as separators, as on live.
        $slugSource = $raw;
        // C4: strip a leading _default: BEFORE transliteration (REFCORR5
        // Batch 5). Running the table first corrupts _default: into _: and
        // the prefix no longer strips. REFCORR7: live tolerates leading
        // space/tab before the category, so the anchored match consumes that
        // run as part of the prefix and drops the matched byte count; a
        // non-leading prefix and a generic colon prefix still do not match,
        // and the bare form still strips exactly nine bytes as before.
        if (preg_match('/^[ \t]*_default:/i', $slugSource, $defPrefix)) {
            $slugSource = substr($slugSource, strlen($defPrefix[0]));
        }
        if (preg_match('/[^\x00-\x7F]/u', $slugSource)) {
            $slugSource = freelink_transliterate($slugSource);
        }
        $page = WDStringUtils::toUnixName($slugSource);

        if ($labelRaw === '') {
            // No pipe label: live strips a category prefix from the display
            // text but keeps the rest of the authored target.
            $text = $raw;
            // A leading : or / is part of the authored display text on live
            // (e.g. [[[:scp-wiki : system : Recent Changes]]]), so only a
            // category prefix after a real page name is stripped here.
            if ($text[0] !== ':' && $text[0] !== '/' && strpos($text, ':') !== false) {
                $text = substr($text, strpos($text, ':') + 1);
            }
            $text = trim($text);
        } elseif (trim($labelRaw) === '|') {
            // Empty pipe label: the renderer fills the text from the page
            // title when the page exists, otherwise from the slug.
            $text = '|';
        } else {
            $text = substr($labelRaw, 1);
        }

        $options = array(
            'site' => null,
            'page' => $page,
            'text' => $text,
            'anchor' => $anchor,
            'extra' => $extra,
            'url' => null,
            'textFromTitle' => (trim($labelRaw) === '|') ? true : null,
        );
        // REFCORR6: the whole triple-bracket form is the claimed span.
        return $this->wiki->addToken($this->rule, $options, false, $matches[0]);
    }
}

// Helpers live at file scope; the class above is closed before them.
function freelink_is_url($s)
{
    $schemes = array('http://', 'https://', 'ftp://', 'file://', 'feed:',
        'git://', 'gopher://', 'irc://', 'irc6://', 'ircs://', 'sftp://',
        'ssh://', 'telnet://', 'rtmp://', 'resource://', 'chrome://',
        'chrome-extension://', 'content://', 'cvs://', 'blob:', 'dns:',
        'mailto:', 'mms:', 'news:', 'nntp:', 'tel:', 'sms:', 'skype:', 'xmpp:');
    foreach ($schemes as $scheme) {
        if (stripos($s, $scheme) === 0) {
            return true;
        }
    }
    return false;
}

function freelink_transliterate($s)
{
    static $map = array(
        'À' => 'a',
        'Á' => 'a',
        'Â' => 'a',
        'Ã' => 'a',
        'Ä' => 'ae',
        'Å' => 'a',
        'Æ' => 'ae',
        'È' => 'e',
        'É' => 'e',
        'Ê' => 'e',
        'Ë' => 'e',
        'Ì' => 'i',
        'Í' => 'i',
        'Î' => 'i',
        'Ï' => 'i',
        'Ð' => 'd',
        'Ñ' => 'n',
        'Ò' => 'o',
        'Ó' => 'o',
        'Ô' => 'o',
        'Õ' => 'o',
        'Ö' => 'oe',
        'Ø' => 'o',
        'Ù' => 'u',
        'Ú' => 'u',
        'Û' => 'u',
        'Ü' => 'ue',
        'Ý' => 'y',
        'Þ' => 't',
        'ß' => 'ss',
        'à' => 'a',
        'á' => 'a',
        'â' => 'a',
        'ã' => 'a',
        'ä' => 'ae',
        'å' => 'a',
        'æ' => 'ae',
        'ç' => 'c',
        'è' => 'e',
        'é' => 'e',
        'ê' => 'e',
        'ë' => 'e',
        'ì' => 'i',
        'í' => 'i',
        'î' => 'i',
        'ï' => 'i',
        'ð' => 'd',
        'ñ' => 'n',
        'ò' => 'o',
        'ó' => 'o',
        'ô' => 'o',
        'õ' => 'o',
        'ö' => 'oe',
        'ø' => 'o',
        'ù' => 'u',
        'ú' => 'u',
        'û' => 'u',
        'ü' => 'ue',
        'ý' => 'y',
        'þ' => 't',
        'ÿ' => 'y',
        'Ā' => 'a',
        'ā' => 'a',
        'Ă' => 'a',
        'ă' => 'a',
        'Ą' => 'a',
        'ą' => 'a',
        'Ć' => 'c',
        'ć' => 'c',
        'Ĉ' => 'c',
        'ĉ' => 'c',
        'Ċ' => 'c',
        'ċ' => 'c',
        'Č' => 'c',
        'č' => 'c',
        'Ď' => 'd',
        'ď' => 'd',
        'Đ' => 'd',
        'đ' => 'd',
        'Ē' => 'e',
        'ē' => 'e',
        'Ĕ' => 'e',
        'ĕ' => 'e',
        'Ė' => 'e',
        'ė' => 'e',
        'Ę' => 'e',
        'ę' => 'e',
        'Ě' => 'e',
        'ě' => 'e',
        'Ĝ' => 'g',
        'ĝ' => 'g',
        'Ğ' => 'g',
        'ğ' => 'g',
        'Ġ' => 'g',
        'ġ' => 'g',
        'Ģ' => 'g',
        'ģ' => 'g',
        'Ĥ' => 'h',
        'ĥ' => 'h',
        'Ħ' => 'h',
        'ħ' => 'h',
        'Ĩ' => 'i',
        'ĩ' => 'i',
        'Ī' => 'i',
        'ī' => 'i',
        'Ĭ' => 'i',
        'ĭ' => 'i',
        'Į' => 'i',
        'į' => 'i',
        'İ' => 'i',
        'ı' => 'i',
        'Ĳ' => 'ij',
        'ĳ' => 'ij',
        'Ĵ' => 'j',
        'ĵ' => 'j',
        'Ķ' => 'k',
        'ķ' => 'k',
        'ĸ' => 'k',
        'Ĺ' => 'l',
        'ĺ' => 'l',
        'Ļ' => 'l',
        'ļ' => 'l',
        'Ľ' => 'l',
        'ľ' => 'l',
        'Ŀ' => 'l',
        'ŀ' => 'l',
        'Ł' => 'l',
        'ł' => 'l',
        'Ń' => 'n',
        'ń' => 'n',
        'Ņ' => 'n',
        'ņ' => 'n',
        'Ň' => 'n',
        'ň' => 'n',
        'ŉ' => 'n',
        'Ŋ' => 'n',
        'ŋ' => 'n',
        'Ō' => 'o',
        'ō' => 'o',
        'Ŏ' => 'o',
        'ŏ' => 'o',
        'Ő' => 'o',
        'ő' => 'o',
        'Œ' => 'oe',
        'œ' => 'oe',
        'Ŕ' => 'r',
        'ŕ' => 'r',
        'Ŗ' => 'r',
        'ŗ' => 'r',
        'Ř' => 'r',
        'ř' => 'r',
        'Ś' => 's',
        'ś' => 's',
        'Ŝ' => 's',
        'ŝ' => 's',
        'Ş' => 's',
        'ş' => 's',
        'Š' => 's',
        'š' => 's',
        'Ţ' => 't',
        'ţ' => 't',
        'Ť' => 't',
        'ť' => 't',
        'Ŧ' => 't',
        'ŧ' => 't',
        'Ũ' => 'u',
        'ũ' => 'u',
        'Ū' => 'u',
        'ū' => 'u',
        'Ŭ' => 'u',
        'ŭ' => 'u',
        'Ů' => 'u',
        'ů' => 'u',
        'Ű' => 'u',
        'ű' => 'u',
        'Ų' => 'u',
        'ų' => 'u',
        'Ŵ' => 'w',
        'ŵ' => 'w',
        'Ŷ' => 'y',
        'ŷ' => 'y',
        'Ÿ' => 'y',
        'Ź' => 'z',
        'ź' => 'z',
        'Ż' => 'z',
        'ż' => 'z',
        'Ž' => 'z',
        'ž' => 'z',
        'ſ' => 'ss',
        'Ƒ' => 'f',
        'ƒ' => 'f',
        'Ș' => 's',
        'ș' => 's',
        'Ț' => 't',
        'ț' => 't',
        'Ά' => 'a',
        'Έ' => 'e',
        'Ή' => 'i',
        'Ί' => 'i',
        'Ό' => 'o',
        'Ύ' => 'y',
        'Ώ' => 'o',
        'ΐ' => 'i',
        'Α' => 'a',
        'Β' => 'v',
        'Γ' => 'g',
        'Δ' => 'd',
        'Ε' => 'e',
        'Ζ' => 'z',
        'Η' => 'i',
        'Θ' => 'th',
        'Ι' => 'i',
        'Κ' => 'k',
        'Λ' => 'l',
        'Μ' => 'm',
        'Ν' => 'n',
        'Ξ' => 'x',
        'Ο' => 'o',
        'Π' => 'p',
        'Ρ' => 'r',
        'Σ' => 's',
        'Τ' => 't',
        'Υ' => 'y',
        'Φ' => 'f',
        'Χ' => 'ch',
        'Ψ' => 'ps',
        'Ω' => 'o',
        'Ϊ' => 'i',
        'Ϋ' => 'y',
        'ά' => 'a',
        'έ' => 'e',
        'ή' => 'i',
        'ί' => 'i',
        'ΰ' => 'y',
        'α' => 'a',
        'β' => 'v',
        'γ' => 'g',
        'δ' => 'd',
        'ε' => 'e',
        'ζ' => 'z',
        'η' => 'i',
        'θ' => 'th',
        'ι' => 'i',
        'κ' => 'k',
        'λ' => 'l',
        'μ' => 'm',
        'ν' => 'n',
        'ξ' => 'x',
        'ο' => 'o',
        'π' => 'p',
        'ρ' => 'r',
        'ς' => 's',
        'σ' => 's',
        'τ' => 't',
        'υ' => 'y',
        'φ' => 'f',
        'χ' => 'ch',
        'ψ' => 'ps',
        'ω' => 'o',
        'ϊ' => 'i',
        'ϋ' => 'y',
        'ό' => 'o',
        'ύ' => 'y',
        'ώ' => 'o',
        'ϴ' => 'th',
        'Ё' => 'e',
        'Ђ' => 'd',
        'Ѓ' => 'g',
        'Є' => 'e',
        'Ѕ' => 'z',
        'І' => 'i',
        'Ї' => 'i',
        'Ј' => 'j',
        'Љ' => 'l',
        'Њ' => 'n',
        'Ћ' => 'c',
        'Ќ' => 'k',
        'Ў' => 'u',
        'Џ' => 'd',
        'А' => 'a',
        'Б' => 'b',
        'В' => 'v',
        'Г' => 'g',
        'Д' => 'd',
        'Е' => 'e',
        'Ж' => 'z',
        'З' => 'z',
        'И' => 'i',
        'Й' => 'j',
        'К' => 'k',
        'Л' => 'l',
        'М' => 'm',
        'Н' => 'n',
        'О' => 'o',
        'П' => 'p',
        'Р' => 'r',
        'С' => 's',
        'Т' => 't',
        'У' => 'u',
        'Ф' => 'f',
        'Х' => 'h',
        'Ц' => 'c',
        'Ч' => 'c',
        'Ш' => 's',
        'Щ' => 's',
        'Ы' => 'y',
        'Э' => 'e',
        'Ю' => 'u',
        'Я' => 'a',
        'а' => 'a',
        'б' => 'b',
        'в' => 'v',
        'г' => 'g',
        'д' => 'd',
        'е' => 'e',
        'ж' => 'z',
        'з' => 'z',
        'и' => 'i',
        'й' => 'j',
        'к' => 'k',
        'л' => 'l',
        'м' => 'm',
        'н' => 'n',
        'о' => 'o',
        'п' => 'p',
        'р' => 'r',
        'с' => 's',
        'т' => 't',
        'у' => 'u',
        'ф' => 'f',
        'х' => 'h',
        'ц' => 'c',
        'ч' => 'c',
        'ш' => 's',
        'щ' => 's',
        'ы' => 'y',
        'э' => 'e',
        'ю' => 'u',
        'я' => 'a',
        'ё' => 'e',
        'ђ' => 'd',
        'ѓ' => 'g',
        'є' => 'e',
        'ѕ' => 'z',
        'і' => 'i',
        'ї' => 'i',
        'ј' => 'j',
        'љ' => 'l',
        'њ' => 'n',
        'ћ' => 'c',
        'ќ' => 'k',
        'ў' => 'u',
        'џ' => 'd',
        'Ѣ' => 'e',
        'ѣ' => 'e',
        'Ѫ' => 'a',
        'ѫ' => 'a',
        'Ѳ' => 'f',
        'ѳ' => 'f',
        'Ѵ' => 'y',
        'ѵ' => 'y',
        'Ґ' => 'g',
        'ґ' => 'g',
        'Ғ' => 'g',
        'ғ' => 'g',
        'Ҕ' => 'g',
        'ҕ' => 'g',
        'Җ' => 'z',
        'җ' => 'z',
        'Қ' => 'k',
        'қ' => 'k',
        'Ҝ' => 'k',
        'ҝ' => 'k',
        'Ҟ' => 'k',
        'ҟ' => 'k',
        'Ҡ' => 'k',
        'ҡ' => 'k',
        'Ң' => 'n',
        'ң' => 'n',
        'Ҥ' => 'n',
        'ҥ' => 'n',
        'Ҧ' => 'p',
        'ҧ' => 'p',
        'Ҩ' => 'o',
        'ҩ' => 'o',
        'Ҫ' => 's',
        'ҫ' => 's',
        'Ҭ' => 't',
        'ҭ' => 't',
        'Ү' => 'u',
        'ү' => 'u',
        'Ұ' => 'u',
        'ұ' => 'u',
        'Ҳ' => 'h',
        'ҳ' => 'h',
        'Ҵ' => 'c',
        'ҵ' => 'c',
        'Ҷ' => 'c',
        'ҷ' => 'c',
        'Ҹ' => 'c',
        'ҹ' => 'c',
        'Һ' => 'h',
        'һ' => 'h',
        'Ҽ' => 'c',
        'ҽ' => 'c',
        'Ҿ' => 'c',
        'ҿ' => 'c',
        'Ӂ' => 'z',
        'ӂ' => 'z',
        'Ӄ' => 'k',
        'ӄ' => 'k',
        'Ӆ' => 'l',
        'ӆ' => 'l',
        'Ӈ' => 'n',
        'ӈ' => 'n',
        'Ӊ' => 'n',
        'ӊ' => 'n',
        'Ӌ' => 'c',
        'ӌ' => 'c',
        'Ӑ' => 'a',
        'ӑ' => 'a',
        'Ӓ' => 'a',
        'ӓ' => 'a',
        'Ӕ' => 'ae',
        'ӕ' => 'ae',
        'Ӗ' => 'e',
        'ӗ' => 'e',
        'Ә' => 'a',
        'ә' => 'a',
        'Ӛ' => 'a',
        'ӛ' => 'a',
        'Ӝ' => 'z',
        'ӝ' => 'z',
        'Ӟ' => 'z',
        'ӟ' => 'z',
        'Ӡ' => 'z',
        'ӡ' => 'z',
        'Ӣ' => 'i',
        'ӣ' => 'i',
        'Ӥ' => 'i',
        'ӥ' => 'i',
        'Ӧ' => 'o',
        'ӧ' => 'o',
        'Ө' => 'o',
        'ө' => 'o',
        'Ӫ' => 'o',
        'ӫ' => 'o',
        'Ӯ' => 'u',
        'ӯ' => 'u',
        'Ӱ' => 'u',
        'ӱ' => 'u',
        'Ӳ' => 'u',
        'ӳ' => 'u',
        'Ӵ' => 'c',
        'ӵ' => 'c',
        'Ӹ' => 'y',
        'ӹ' => 'y',
        'Ԋ' => 'n',
        'ԋ' => 'n',
        'Ԏ' => 't',
        'ԏ' => 't',
        'Ԛ' => 'q',
        'ԛ' => 'q',
        'Ԝ' => 'w',
        'ԝ' => 'w',
        'ẞ' => 'ss',
        'Å' => 'a',
        'K' => 'k',
    );
    $out = '';
    $chars = preg_split('//u', $s, -1, PREG_SPLIT_NO_EMPTY);
    foreach ($chars as $ch) {
        // REFCORR5 Batch 5: ASCII alphanumerics pass through untouched; the
        // table and the separator fallback are for non-ASCII only.
        if (preg_match('/^[A-Za-z0-9]$/D', $ch) ||
            $ch === '#' || $ch === ':' || $ch === '/' || $ch === ' ' || $ch === '_' || $ch === '-') {
            $out .= $ch;
            continue;
        }
        if (isset($map[$ch])) {
            $out .= $map[$ch];
        } else {
            $out .= ' ';
        }
    }
    return $out;
}
