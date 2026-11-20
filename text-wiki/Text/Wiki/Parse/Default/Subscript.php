<?php

/**
 * 
 * Parses for subscripted text.
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
 * Parses for subscripted text.
 * 
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Paul M. Jones <pmjones@php.net>
 * @author Michal Frackowiak
 * 
 */

class Text_Wiki_Parse_Subscript extends Text_Wiki_Parse {
    
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
    
    // R2-INLINE3 C1 (fossil-era artifact, Stage-1 empty-pair drop):
    // the fossil pattern requires a non-whitespace body, so an adjacent
    // pair of markers (,,,,) never matched and was left as literal text.
    // Live Wikidot pairs adjacent markers first-fit and drops the empty
    // pair: the frozen pin test/subscript/basic renders ",,,," as
    // <p>Then empty subscript:</p>, and live probe
    // muse-probe-r2in3-sub-sub13 renders ",,,,four,,,," as <p>four</p>,
    // so a four-comma run is consumed as an empty pair before a longer
    // body can claim its markers. The empty-pair branch is therefore
    // placed FIRST; the original non-empty branch is otherwise verbatim,
    // preserving the comma-run collision forms live already agrees on
    // (,,,a,,, -> <sub>,a</sub>, and ,,a ,, b,, -> <sub>a ,, b</sub>,
    // confirmed by probes sub12 and sub11).
    public $regex = "/,,,,|,,([^\s](?:.*[^\s])?),,/U";

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
        // R2-INLINE3 C1: the ,,,, alternation has no body group; returning ''
        // consumes both markers and emits no token pair, which is the
        // empty-pair drop live performs. A non-empty body keeps the fossil
        // token pair unchanged.
        $body = isset($matches[1]) ? $matches[1] : '';
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
