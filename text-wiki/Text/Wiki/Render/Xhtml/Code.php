<?php
require_once(WIKIDOT_ROOT."/lib/Text_Highlighter/Text/Highlighter.php");
ini_set('include_path',ini_get('include_path').':'.WIKIDOT_ROOT.'/lib/Text_Highlighter/');

/**
 * Code rule end renderer for Xhtml
 *
 * PHP versions 4 and 5
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @author Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    $Id$
 * @link       http://pear.php.net/package/Text_Wiki
 */

/**
 * This class renders code blocks in XHTML.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @author Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Code extends Text_Wiki_Render {

    public $conf = array(
        'css'      => null, // class for <pre>
        'css_code' => null, // class for generic <code>
        'css_php'  => null, // class for PHP <code>
        'css_html' => null, // class for HTML <code>
        'css_filename' => null // class for optional filename <div>
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
        $text = $options['text'];
        $attr = $options['attr'];
        $type = strtolower($attr['type']);

        $css      = $this->formatConf(' class="%s"', 'css');
        $css_code = $this->formatConf(' class="%s"', 'css_code');
        $css_php  = $this->formatConf(' class="%s"', 'css_php');
        $css_html = $this->formatConf(' class="%s"', 'css_html');
        $css_filename = $this->formatConf(' class="%s"', 'css_filename');

        // R2 Code: live trims code bodies by dropping whole leading blank
        // lines and stripping trailing whitespace, but it KEEPS indentation
        // on the first content line (ftml corpus code/edge-whitespace pins:
        // "\n  x  \n" renders as "  x"). PHP's trim() stripped that indent,
        // so it is replaced by the same line-wise rule ftml uses. NBSP is
        // served as a regular space on live (same corpus pin); ideographic
        // space is preserved.
        $text = $this->wikidotTrimCodeBody($text);

        // R2 Code: the fossil called Text_Highlighter::factory() statically,
        // which is a fatal error on PHP 8 ("Non-static method ... cannot be
        // called statically"). Instantiate the factory object and call it on
        // that instance; factory() returns by reference, so bind with '&'.
        $langs = array('php', 'cpp', 'css', 'html', 'xhtml', 'diff', 'dtd',
            'java', 'javascript', 'sql', 'perl', 'python', 'ruby', 'xml');
        $hl = null;
        if (in_array($type, $langs, true)) {
            $factory = new Text_Highlighter();
            $lang = ($type == 'xhtml') ? 'html' : $type;
            $hl =& $factory->factory($lang);
        }

        if ($hl !== null && !PEAR::isError($hl)) {
            $text = $hl->highlight($text);
            // The vendored ~2006 highlighter emits empty <span> tokens that
            // live's current highlighter does not (e.g. after a CSS value).
            // Strip them so the token stream matches the live-adjudicated
            // ftml corpus pins (code/highlight-* wikidot.html).
            $text = preg_replace('/<span class="hl-[a-z]+"><\/span>/', '', $text);
            // R2 Code FRAME item: live puts a newline after the wrapper's
            // opening <div> and around the hl-main child. The vendor output
            // already carries the hl-main div, so insert the newlines inside
            // it rather than adding a second wrapper.
            $text = str_replace(
                array('<div class="hl-main">', '</pre></div>'),
                array("<div class=\"hl-main\">\n", "</pre></div>\n"),
                $text
            );
            $text = "<div class=\"code\">\n" . $text . "</div>";
        } elseif (trim($text) === '') {
            // Empty (or all-whitespace) bodies render as a bare wrapper on
            // live: <div class="code"></div> (probe muse-probe-r2code-empty-body
            // and ftml corpus code/basic EMPTY pin).
            $text = '<div class="code"></div>';
        } else {
            // generic code example: keep entity handling at PHP 4/5's
            // ENT_COMPAT default (double quotes escaped, single quotes
            // literal); PHP 8's default ENT_QUOTES would emit &#039; where
            // live emits a bare apostrophe (probe r2code entities-body).
            $text = str_replace("\t", "    ", $text);
            $text = htmlspecialchars($text, ENT_COMPAT);
            $text = "<div class=\"code\">\n<pre$css><code$css_code>$text</code></pre></div>";
        }

        if ($css_filename && isset($attr['filename'])) {
            $text = "<div$css_filename>" .
                $attr['filename'] . '</div>' . $text;
        }

        return "\n$text\n\n";
    }

    /**
     * Live code-body trim: drop whole leading blank lines, strip trailing
     * ASCII whitespace, keep leading indentation on the first content line.
     */
    function wikidotTrimCodeBody($body)
    {
        $body = str_replace("\r\n", "\n", $body);
        while (true) {
            $withoutIndent = ltrim($body, " \t");
            if (substr($withoutIndent, 0, 1) === "\n") {
                $body = substr($withoutIndent, 1);
                continue;
            }
            break;
        }
        $body = rtrim($body, " \t\n");
        return str_replace("\u{a0}", ' ', $body);
    }
}
