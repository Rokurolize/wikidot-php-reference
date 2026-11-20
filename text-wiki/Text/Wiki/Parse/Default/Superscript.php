<?php

/**
* 
* Parses for superscripted text.
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
* Parses for superscripted text.
* 
* @category Text
* 
* @package Text_Wiki
* 
* @author Paul M. Jones <pmjones@php.net>
* @author Michal Frackowiak
* 
*/

class Text_Wiki_Parse_Superscript extends Text_Wiki_Parse {

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
    
    // R2-inline3 correction C1: the fossil regex required a non-whitespace
    // character at both edges of the body, so a bare `^^^^` (an empty
    // superscript pair) never paired and its four markers survived as literal
    // text. Live Wikidot consumes the markers and emits nothing: saved-page
    // probe muse-probe-r2in3-sup-p05 (source `^^^^`) renders to only the line
    // break `<p><br />\nx</p>`, p06 (`^^^^ x`) to `<p>x</p>`, and p30
    // (`a^^^^b`) to `<p>ab...`, all byte-identical to the corrected reference;
    // before correction the reference rendered `<p>^^^^</p>`, `<p>^^^^ x</p>`
    // and `<p>a^^^^b</p>`. ftml's superscript rule independently returns
    // Elements::None for an empty body (src/parsing/rule/impls/superscript.rs,
    // the `container.elements().is_empty()` branch), pinned by the same-shape
    // empty bold pair in the Strong stage. The added empty alternative lets
    // the pair match; process() emits no tokens for it, so nothing renders and
    // the surrounding line structure is untouched. Padded empty pairs such as
    // `^^ ^^` stay literal on live (probe p07) and in the reference, unchanged.
    public $regex =  "/\^\^([^\s](?:.*[^\s])?|)\^\^/U";
    
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
    
    function process($matches)
    {
        // R2-inline3 correction C1 (continued): an empty body consumes the
        // four markers but emits no start/end tokens, matching live and ftml.
        if ($matches[1] === '') {
            return '';
        }
        $start = $this->wiki->addToken(
            $this->rule, array('type' => 'start')
        );
        
        $end = $this->wiki->addToken(
            $this->rule, array('type' => 'end')
        );
        
        return $start . $matches[1] . $end;
    }
}
