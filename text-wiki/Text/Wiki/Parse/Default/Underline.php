<?php

/**
 * 
 * Parses for underlined text.
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
 * Parses for underlined text.
 *
 * This class implements a Text_Wiki_Rule to find source text marked for
 * underline as defined by text surrounded by a pair of double underscores.
 * On parsing, the text itself is left in place, but the starting and ending
 * double underscores are replaced with tokens. An empty pair (two adjacent
 * __ markers) is discarded entirely, matching live Wikidot and ftml's
 * symmetric-marker first-fit; an odd leftover marker stays literal.
 *
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Paul M. Jones <pmjones@php.net>
 * @author Michal Frackowiak
 * 
 */

class Text_Wiki_Parse_Underline extends Text_Wiki_Parse {
    
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
    
    // R2-INLINE2 correction C1: the first alternative removes adjacent empty
    // __ pairs (live Wikidot and ftml discard them); the original pair regex
    // is kept unchanged as the second alternative so padded bodies and
    // first-fit ungreedy pairing still behave exactly as before.
    public $regex = "/____|__([^\s](?:.*[^\s])?)__/U";

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
    
    function process($matches) {
        // Empty adjacent __ pairs carry no capture group and render to nothing.
        if (!isset($matches[1]) || $matches[1] === '') {
            return '';
        }
        $start = $this->wiki->addToken($this->rule, array(
            'type' => 'start'));
        $end = $this->wiki->addToken($this->rule, array(
            'type' => 'end'));
        return $start . $matches[1] . $end;
    }
}
