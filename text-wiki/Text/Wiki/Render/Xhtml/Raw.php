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
 *
 * REFCORR-NEXT (m2 FIX 1): angle-raw (@<...>@) tokens carry 'angle' => true.
 * Their bodies were entity-decoded at parse time; a decoded U+00A0 is
 * serialized as &nbsp; (live canon-hub/art:vasilisa-blud), while the plain
 * @@...@@ form keeps the unchanged escape table.
 */
class Text_Wiki_Render_Xhtml_Raw extends Text_Wiki_Render {

    function token($options)
    {
        // REFCORR5 Batch 6: the composite empty Raw token renders as nothing.
        if ($options['text'] === '') return '';
        return '<span style="white-space: pre-wrap;">'
            . wikidotEscapeRaw($options['text'], !empty($options['angle']))
            . '</span>';
    }
}

if (!function_exists('wikidotEscapeRaw')) {
    function wikidotEscapeRaw($s, $angle = false) {
        $table = array(
            ' ' => '&#32;',
            "\0" => ' ',
            '>' => '&gt;',
            '<' => '&lt;',
            '&' => '&amp;',
            "'" => "'",
            '"' => '&quot;',
        );
        // REFCORR-NEXT: only the entity-decoded angle-raw form serializes
        // U+00A0 as the &nbsp; entity, as live does. The @@ form is left on
        // the original table so a literal NBSP byte stays literal there.
        if ($angle) $table["\u{00A0}"] = '&nbsp;';
        return strtr($s, $table);
    }
}
