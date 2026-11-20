<?php

/**
 * 
 * Parses for a comment block.
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
 * Parses for a comment block.
 *
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Michal Frackowiak
 * 
 *  */
class Text_Wiki_Parse_Comment extends Text_Wiki_Parse {

    /**
     * 
     * The regular expression used to find source text matching this
     * rule. A leading newline belongs to the comment; the body is
     * dot-all and the delimiters are case-insensitive, as in the fossil.
     * 
     * @access public
     * 
     * @var string
     * 
     */
     
    public $regex = '/(\n)?\[!\-\-(.*?)\-\-\]/si';

    /**
     * Remove comment spans. The regex and the missing token are the fossil
     * behavior and live confirms both, including the `[[!-- ... --]]` form
     * where live leaves the enclosing `[]` exactly as this rule does. The one
     * live-driven change is that a comment occupying its own indented line
     * takes its leading horizontal whitespace with it: the saved probe
     * muse-probe-r2next-comment-nl-indented-spaces renders an empty line
     * where the fossil left the two spaces as text. Prefilter has already
     * converted tabs to spaces and normalized line endings by this point.
     */
    function parse()
    {
        $source = $this->wiki->source;
        if (strpos($source, '[!--') === false) {
            return;
        }
        preg_match_all($this->regex, $source, $matches, PREG_OFFSET_CAPTURE);
        $out = '';
        $cursor = 0;
        foreach ($matches[0] as $i => $match) {
            $full = $match[0];
            $start = $match[1];
            $removeFrom = $start;
            $indentedOnlyLine = false;
            $lineBreak = strrpos(substr($source, 0, $start), "\n");
            $lineStart = $lineBreak === false ? 0 : $lineBreak + 1;
            $prefix = substr($source, $lineStart, $start - $lineStart);
            if ($prefix !== '' && preg_match('/^[ \t]+$/', $prefix)) {
                $lineEnd = strpos($source, "\n", $start + strlen($full));
                $tail = substr($source, $start + strlen($full),
                    ($lineEnd === false ? strlen($source) : $lineEnd)
                        - ($start + strlen($full)));
                if ($tail === '' || preg_match('/^[ \t]*$/', $tail)) {
                    $removeFrom = $lineStart;
                    $indentedOnlyLine = true;
                }
            }
            // A token that renders to the empty string keeps the line in
            // place for the paragraph rule while contributing no visible
            // text, matching live's empty line between two line breaks.
            $replacement = $indentedOnlyLine
                ? $this->wiki->addToken('Comment', array('text' => $full))
                : '';
            $out .= substr($source, $cursor, $removeFrom - $cursor) . $replacement;
            $cursor = $start + strlen($full);
        }
        $out .= substr($source, $cursor);
        $this->wiki->source = $out;
    }

    /**
     * 
     * Generates a token entry for the matched text.  Token options are:
     * 
     * 'text' => The full matched text, not including the <code></code> tags.
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
        
        return '';
    
    }
}
