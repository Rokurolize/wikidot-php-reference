<?php

/**
* 
* Parses for emphasized text.
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
* Parses for emphasized text.
* 
* This class implements a Text_Wiki_Parse to find source text marked for
* emphasis (italics) as defined by text surrounded by two single-quotes.
* On parsing, the text itself is left in place, but the starting and ending
* instances of two single-quotes are replaced with tokens.
*
* @category Text
* 
* @package Text_Wiki
* 
* @author Paul M. Jones <pmjones@php.net>
* @author Michal Frackowiak
* 
*/

class Text_Wiki_Parse_Emphasis extends Text_Wiki_Parse {

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
    
    // R2-INLINE2 C1 (fossil-era artifact, Stage-1 first-fit pairing):
    // the fossil pattern required a non-whitespace body, so two adjacent
    // // markers were never paired and a run like ////four//// bound its
    // first opener to its third marker, leaving a phantom body and a
    // dangling //. Live Wikidot pairs each // with the first following //
    // on the same line (the same first-fit scan ftml performs in
    // parsing/parser/inline_pairs.rs) and drops the empty pair. Use a
    // lazy body so the earliest closer wins; process() rejects a
    // whitespace-padded body (live keeps // padded // literal) and returns
    // nothing for an empty body, which is where the drop happens.
    public $regex =  "/\/\/(.*)\/\//U";

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
    * @return string A pair of delimited tokens to be used as a
    * placeholder in the source text surrounding the text to be
    * emphasized.
    *
    */
    
    function process($matches)
    {
        $body = $matches[1];
        // R2-INLINE2 C1: an empty body between two adjacent // markers is a
        // real first-fit pair on live and renders as nothing; returning ''
        // consumes both markers and emits no token pair. Verified against
        // live pages muse-probe-r2in2-em-em09, -em12 and -em14
        // (////four//// -> <p>four</p>, //// -> empty, ////em//// -> <p>em</p>).
        if ($body === '') {
            return '';
        }
        // A body that opens or closes in whitespace is not an emphasis pair
        // on live; keep the original markers literal rather than tokenizing.
        if (preg_match('/^\s|\s$/', $body)) {
            return $matches[0];
        }
        $start = $this->wiki->addToken(
            $this->rule, array('type' => 'start')
        );

        $end = $this->wiki->addToken(
            $this->rule, array('type' => 'end')
        );

        return $start . $body . $end;
    }
}
