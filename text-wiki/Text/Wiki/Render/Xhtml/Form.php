<?php
/**
 * Form rule end renderer for Xhtml (R2 Form/Raw/Rawold corrected).
 *
 * Live Wikidot (probe muse-probe-r2formraw-form-basic et al.) renders a
 * matched [[form]] block as literal source text, one raw-style span per line,
 * not as an interactive form. The interactive submission behavior belongs to
 * the serving layer and is out of scope here. The parse rule stores one token
 * per line, so this renderer emits the same pre-wrap span as the Raw rule.
 */
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

class Text_Wiki_Render_Xhtml_Form extends Text_Wiki_Render {

    function token($options)
    {
        if (isset($options['blank'])) {
            return '';
        }
        if (isset($options['text'])) {
            $line = wikidotEscapeRaw($options['text']);
            // Live Form's literal lines indent with a Wikidot nbsp/space
            // alternation: each leading pair of spaces is &nbsp;&#32;, with
            // a trailing single space rendered as &#32; (probes
            // muse-probe-r2formraw-form-basic, -formindent1).
            $prefix = '';
            while (substr($line, 0, 10) === '&#32;&#32;') {
                $prefix .= '&nbsp;&#32;';
                $line = substr($line, 10);
            }
            if (substr($line, 0, 5) === '&#32;') {
                $prefix .= '&#32;';
                $line = substr($line, 5);
            }
            return '<span style="white-space: pre-wrap;">'
                . $prefix . $line
                . '</span>';
        }
        // Kept for compatibility with the fossil's begin/field/end token
        // shape; live evidence gives those no observable role on a saved
        // anonymous page view.
        return '';
    }
}
