<?php

/**
 * 
 * Parses for strongly-emphasized text.
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
 * Parses for strongly-emphasized text.
 * 
 * This class implements a Text_Wiki_Parse to find source text marked for
 * strong emphasis (bold) as defined by text surrounded by three
 * single-quotes. On parsing, the text itself is left in place, but the
 * starting and ending instances of three single-quotes are replaced with
 * tokens.
 *
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Paul M. Jones <pmjones@php.net>
 * @author Michal Frackowiak
 * 
 */

class Text_Wiki_Parse_Strong extends Text_Wiki_Parse {
    
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
    
    // R2-inline2 correction C1: the fossil regex required a non-whitespace
    // character at both edges of the body, so a bare `****` (an empty bold
    // pair) never paired and its four markers survived as literal text. Live
    // Wikidot consumes the markers and emits nothing: saved-page probe
    // muse-probe-r2in2-strong-p06 (source `****`) renders to an empty page and
    // p05 (`****\nx`) keeps only the line break, while ftml's bold rule returns
    // Elements::None for the empty body (corpus pins test/bold/native and
    // test/bold/empty-pair-feeds-later-rule). The added empty alternative lets
    // the pair match; process() emits no tokens for it, so nothing renders and
    // the surrounding line structure is untouched.
    public $regex = "/\*\*\*\*|\*\*([^\s\n](?:.*[^\s\n])?)\*\*/U";

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
        $body = isset($matches[1]) ? $matches[1] : '';
        // R2-inline2 correction C1 (continued): an empty body consumes the
        // four markers but emits no start/end tokens, matching live and ftml.
        if ($body === '') {
            return '';
        }
        $start = $this->wiki->addToken($this->rule, array(
            'type' => 'start'));
        
        $end = $this->wiki->addToken($this->rule, array(
            'type' => 'end'));
        
        return $start . $body . $end;
    }
}
