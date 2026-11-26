<?php

/**
 * 
 * Parses for colorized text.
 * 
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Paul M. Jones <pmjones@php.net>
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
 * Parses for colorized text.
 * 
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Paul M. Jones <pmjones@php.net>
 * 
 * @author Michal Frackowiak
 * 
 */

class Text_Wiki_Parse_Colortext extends Text_Wiki_Parse {
    
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
    
    // REFCORR5 Batch 2: validate the color spec at parse time, matching
    // live's normalizeColor admission set. An invalid spec leaves the whole
    // construct literal so earlier tokens in it render normally, HTML
    // metacharacters are escaped by pre(), and Tighten cannot hoist its
    // spaces; a rejected opener also lets the lazy scan reach a later valid
    // span on the same line.
    public $regex = '/##([A-Za-z0-9#(),\- \t]+)\|(.+?)##/';

    /**
     * REFCORR34: Span and Size edge whitespace has two stage-specific owners.
     * While the block-layout rules run it must sit outside the inline scope
     * (the REFCORR32 placement); once Newline/Paragraph/List have finished,
     * the same bytes must again be inside the scope so the paired-marker
     * grammar sees live's inline edges. In particular a trailing space keeps
     * `[[size 0%]]__ [[/size]]` from becoming half of a cross-item __ pair,
     * while a leading space no longer sits between `**` and a Span token in
     * `**[[span]] text[[/span]]**`. Tighten performs the final outward move.
     */
    function parse()
    {
        foreach ($this->wiki->tokens as $tid => $tok) {
            if (! is_array($tok) || ($tok[0] !== 'Span' && $tok[0] !== 'Size')) {
                continue;
            }
            $literal = $this->wiki->delim . $tid . $this->wiki->delim;
            $type = isset($tok[1]['type']) ? $tok[1]['type'] : '';
            if ($type === 'start' && isset($tok[1]['edge_lead']) && $tok[1]['edge_lead'] !== '') {
                $edge = $tok[1]['edge_lead'];
                $this->wiki->source = str_replace(
                    $edge . $literal,
                    $literal . $edge,
                    $this->wiki->source
                );
            } elseif ($type === 'end' && isset($tok[1]['edge_trail']) && $tok[1]['edge_trail'] !== '') {
                $edge = $tok[1]['edge_trail'];
                $this->wiki->source = str_replace(
                    $literal . $edge,
                    $edge . $literal,
                    $this->wiki->source
                );
            }
        }
        parent::parse();
    }

    /**
     * 
     * Generates a replacement for the matched text.  Token options are:
     * 
     * 'type' => ['start'|'end'] The starting or ending point of the
     * emphasized text.  The text itself is left in the source.
     * 
     * 'color' => the color indicator
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
    
    
    function process($matches) {
        $start = $this->wiki->addToken($this->rule, array(
            'type' => 'start', 
            'color' => $matches[1]));
        
        $end = $this->wiki->addToken($this->rule, array(
            'type' => 'end', 'color' => $matches[1]));
        
        return $start . $matches[2] . $end;
    }
}
