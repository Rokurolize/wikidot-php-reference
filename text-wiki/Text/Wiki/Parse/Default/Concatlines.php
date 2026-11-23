<?php
/**
 * 
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Michal Frackowiak
 * 
 * @license LGPL
 * 
 * @version $Id$
 * 
 */

/**
 * 
 * Joins lines.
 *
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Michal Frackowiak
 * 
 */
class Text_Wiki_Parse_Concatlines extends Text_Wiki_Parse {

    /**
     * 
     * Simple parsing method.
     *
     * @access public
     * 
     */
    
    function parse() {
        // Concat lines ending in a backslash. The replacement is deliberately a single left-to-right pass, matching live Wikidot's str_replace semantics rather than ftml's repeated cascade on runs of backslashes and newlines; a second backslash exposed by a removed pair is not itself joined. One exception is settled live: a continuation whose next line is a standalone div opener drops the backslash but keeps the line break, so the opener stays at line start and renders as a block on the following line instead of being pulled into the preceding paragraph. Live's rendered output shows no visible backslash there, and ftml reaches the same observable shape after its own later backslash handling. The divider regex mirrors ftml's Wikidot continued-div-opener check and is ASCII-case-insensitive.
        $source = $this->wiki->source;
        if (strpos($source, "\\\n") === false) {
            return;
        }
        // R11-CONCAT: a continued line whose next line is a standalone div
        // opener is a continued block boundary on live. Record the plain lead
        // text of such a line in a non-compared side channel so Paragraph can
        // leave it bare (no <p> wrapper); the opener still owns its block.
        $this->wiki->vars['continued_div_leads'] = array();
        $out = '';
        $length = strlen($source);
        $index = 0;
        while ($index < $length) {
            if ($source[$index] === '\\' && $index + 1 < $length && $source[$index + 1] === "\n") {
                $lineEnd = strpos($source, "\n", $index + 2);
                $line = ($lineEnd === false)
                    ? substr($source, $index + 2)
                    : substr($source, $index + 2, $lineEnd - $index - 2);
                $marker = trim($line, " \t");
                if (preg_match('/^\[\[div_?(?:[ \t].*)?\]\]$/i', $marker)) {
                    $lineStart = strrpos($out, "\n");
                    $lead = ($lineStart === false)
                        ? $out : substr($out, $lineStart + 1);
                    $lead = trim($lead, " \t");
                    if (! in_array($lead, $this->wiki->vars['continued_div_leads'], true)) {
                        $this->wiki->vars['continued_div_leads'][] = $lead;
                    }
                    // Join the continuation with one space, as live does: the
                    // opener no longer gets a blank-line boundary from the
                    // doubled leading newline of Div::process.
                    $out .= " ";
                }
                $index += 2;
                continue;
            }
            $out .= $source[$index];
            $index++;
        }
        $this->wiki->source = $out;
    }

}
