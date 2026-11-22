<?php

/**
* 
* Parses for definition lists.
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
* Parses for definition lists.
* 
* This class implements a Text_Wiki_Parse to find source text marked as a
* definition list.  In short, if a line starts with ':' then it is a
* definition list item; another ':' on the same line indicates the end
* of the definition term and the beginning of the definition narrative.
* The list items must be on sequential lines (no blank lines between
* them) -- a blank line indicates the beginning of a new list.
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

class Text_Wiki_Parse_Deflist extends Text_Wiki_Parse {

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
    
    public $regex = '/\n((: ).*\n)(?!(: |\n))/Us';

    /**
    * 
    * Generates a replacement for the matched text.  Token options are:
    * 
    * 'type' =>
    *     'list_start'    : the start of a definition list
    *     'list_end'      : the end of a definition list
    *     'term_start'    : the start of a definition term
    *     'term_end'      : the end of a definition term
    *     'narr_start'    : the start of definition narrative
    *     'narr_end'      : the end of definition narrative
    *     'unknown'       : unknown type of definition portion
    *
    * @access public
    *
    * @param array &$matches The array of matches from parse().
    *
    * @return A series of text and delimited tokens marking the different
    * list text and list elements.
    *
    */
    
    function process($matches)
    {
        // create an array called $list that contains a new set of
        // matches for the various definition-list elements.
        $list = array();
        preg_match_all(
            '/^(: )(.*)?( : )(.*)?$/Ums',
            $matches[1],
            $list,
            PREG_SET_ORDER
        );

        // Live drops a colon-led run that never formed a definition
        // (a missing separator or an empty value with no trailing
        // space) rather than emitting an empty <dl>. Keep one line
        // break so surrounding text keeps its original separation.
        if (count($list) === 0) {
            return "\n";
        }

        // the replacement text we will return to parse()
        $return = '';

        // start the deflist
        $options = array('type' => 'list_start');
        $return .= $this->wiki->addToken($this->rule, $options);

        // add each term and narrative
        foreach ($list as $key => $val) {
            $term = trim($val[2]);
            if (! $this->termRendersEmpty($term)) {
                // Live and ftml omit the <dt> tag when the term renders
                // empty; the fossil emitted an empty <dt></dt> pair.
                $return .= $this->wiki->addToken($this->rule, array('type' => 'term_start')) .
                    $term .
                    $this->wiki->addToken($this->rule, array('type' => 'term_end'));
            }
            $return .= $this->wiki->addToken($this->rule, array('type' => 'narr_start')) .
                trim($val[4]) .
                $this->wiki->addToken($this->rule, array('type' => 'narr_end'));
        }

        // end the deflist
        $options = array('type' => 'list_end');
        $return .= $this->wiki->addToken($this->rule, $options);

        // done!
        return "\n" . $return . "\n\n";
    }

    function termRendersEmpty($term)
    {
        // Inline rules that render to nothing (notably Comment) have
        // already become delimiter-wrapped token placeholders at this
        // point in the pipeline, so strip those before testing emptiness.
        return trim(preg_replace('/\xFF\d+\xFF/', '', $term)) === '';
    }
}
