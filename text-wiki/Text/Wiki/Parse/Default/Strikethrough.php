<?php

/**
 *
 * 
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Paul M. Jones <pmjones@php.net>
 * 
 * @license LGPL
 * 
 * @version $Id$
 * 
 */

/**
 * 
 * Parses for strikethrough text.
 * 
 *
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Michal Frackowiak
 * 
 */

class Text_Wiki_Parse_Strikethrough extends Text_Wiki_Parse {
    
    /**
     * 
     * The regular expression used to parse the source text and find
     * matches conforming to this rule.  Used by the parse() method.
     * 
     * @access public
     * 
     * @var string
     * 
     * @see parse()
     * 
     */
    
    public $regex = "/\-\-([^\s](?:.*[^\s])?)\-\-/U";

    /**
     * 
     * Generates a replacement for the matched text.  Token options are:
     * 
     * 'type' => ['start'|'end'] The starting or ending point of the
     * emphasized text.  The text itself is left in the source.
     * 
     * @access public
     *
     * @param array &$matches The array of matches from parse().
     *
     * @return A pair of delimited tokens to be used as a placeholder in
     * the source text surrounding the text to be emphasized.
     *
     */
    
    function parse() {
        $src = $this->wiki->source;
        $n = strlen($src);
        $delim = $this->wiki->delim;
        $out = '';
        $offset = 0;
        while ($offset < $n && preg_match($this->regex, $src, $m, PREG_OFFSET_CAPTURE, $offset)) {
            $matchStr = $m[0][0];
            $matchPos = $m[0][1];
            $body = $m[1][0];
            // REFCORR15 (S_diag d30): Span::parse() trims trailing spaces before
            // [[/span]], gluing a literal `--` to the Span `end` placeholder
            // (\xffN\xff). Reject an opening `--` immediately followed by a Span
            // `end` token so `--` cannot pair across [[/span]].
            $rejectSpanEnd = false;
            if ($delim !== '' && $body !== '' && $body[0] === $delim) {
                $closeDelim = strpos($body, $delim, 1);
                if ($closeDelim !== false && $closeDelim > 1) {
                    $tokId = substr($body, 1, $closeDelim - 1);
                    if (ctype_digit($tokId)) {
                        $idNum = (int) $tokId;
                        if (isset($this->wiki->tokens[$idNum])
                            && $this->wiki->tokens[$idNum][0] === 'Span'
                            && isset($this->wiki->tokens[$idNum][1]['type'])
                            && $this->wiki->tokens[$idNum][1]['type'] === 'end') {
                            $rejectSpanEnd = true;
                        }
                    }
                }
            }
            if ($rejectSpanEnd) {
                $out .= substr($src, $offset, $matchPos - $offset + 2);
                $offset = $matchPos + 2;
                continue;
            }
            $out .= substr($src, $offset, $matchPos - $offset);
            $out .= $this->process(array($matchStr, $body));
            $offset = $matchPos + strlen($matchStr);
        }
        if ($offset === 0) {
            return;
        }
        $out .= substr($src, $offset);
        $this->wiki->source = $out;
    }

    function process($matches) {
        $start = $this->wiki->addToken($this->rule, array(
            'type' => 'start'));
        $end = $this->wiki->addToken($this->rule, array(
            'type' => 'end'));
        return $start . $matches[1] . $end;
    }
}
