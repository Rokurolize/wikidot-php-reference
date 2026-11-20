<?php
/**
 * Parses [[form]] blocks (R2 Form/Raw/Rawold corrected).
 *
 * The fossil's regex is retained: a line-start-independent [[form]] opener,
 * a YAML-ish definition body, a '---' separator line, a data body, and a
 * [[/form]] closer, with /is. Live probes on sandbox-for-codex
 * (muse-probe-r2formraw-form-*) show that current live Wikidot does NOT expose
 * the interactive form widget on an anonymous page view: a matched block is
 * rendered as literal source text, one raw-style span per line, with the YAML
 * and data bodies untouched. The fossil's process() crashed here because
 * Wikidot_Form (and the YAML libraries it needs) are absent from the fossil
 * snapshot and from the reference tree; the interactive data-form behavior is
 * a serving-layer concern and is out of scope for the parse/render rules.
 * The corrected parser therefore stores one Raw-style token per source line,
 * leaving the newline bytes in place so the existing Newline rules produce the
 * live <br /> joins. An unterminated or malformed block does not match at all
 * and is processed as ordinary wikitext, exactly as live does.
 */
class Text_Wiki_Parse_Form extends Text_Wiki_Parse {

    // Live probe form-no-sep shows a block without the '---' data separator
    // is still claimed as a literal form; only an unterminated block is left
    // as ordinary wikitext. The separator is therefore optional here.
    public $regex = '/\[\[form\]\]\s*\n(.*?)(?:\n---\s*\n(.*?))?\n\[\[\/form\]\]/is';

    function process($matches) {
        $lines = explode("\n", $matches[0]);
        $out = '';
        foreach ($lines as $idx => $line) {
            if ($line !== '') {
                $out .= $this->wiki->addToken($this->rule, array('text' => $line));
            } else {
                // A blank source line inside a form still produces a <br />
                // on live but must not become a paragraph break; a token
                // placeholder keeps the line inline.
                $out .= $this->wiki->addToken($this->rule, array('blank' => 1));
            }
            if ($idx < count($lines) - 1) $out .= "\n";
        }
        return $out;
    }
}
