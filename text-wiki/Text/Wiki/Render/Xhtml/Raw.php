<?php
// vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
/**
 * Raw rule end renderer for Xhtml
 *
 * R2 Form/Raw/Rawold correction: the live Wikidot @@...@@ renderer wraps the
 * literal body in <span style="white-space: pre-wrap;"> and applies Wikidot's
 * raw-escape table: spaces become &#32;, NUL becomes a regular space, the five
 * HTML-significant ASCII characters are entity-escaped, and apostrophes stay
 * literal (ftml's escape_wikidot_raw in render/html/escape.rs; live probe
 * muse-probe-r2formraw-raw-entities). The fossil's bare htmlspecialchars()
 * emitted neither the wrapper nor the space escaping and escaped apostrophes
 * under PHP 8's ENT_QUOTES default.
 */
class Text_Wiki_Render_Xhtml_Raw extends Text_Wiki_Render {

    function token($options)
    {
        // REFCORR5 Batch 6: the composite empty Raw token renders as nothing.
        if ($options['text'] === '') return '';
        return '<span style="white-space: pre-wrap;">'
            . wikidotEscapeRaw($options['text'])
            . '</span>';
    }
}

if (!function_exists('wikidotEscapeRaw')) {
    function wikidotEscapeRaw($s) {
        return strtr($s, array(
            ' ' => '&#32;',
            "\0" => ' ',
            '>' => '&gt;',
            '<' => '&lt;',
            '&' => '&amp;',
            "'" => "'",
            '"' => '&quot;',
        ));
    }
}
