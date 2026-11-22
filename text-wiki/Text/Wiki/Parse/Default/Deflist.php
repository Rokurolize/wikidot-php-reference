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
        // REFCORR3 C-SUSPECT-LISTTABLE-1: of the inline rules that have
        // already become delimiter-wrapped placeholders at this point, only
        // Comment renders to nothing on live. Anchor, User and Bibcite
        // placeholders keep a visible <dt>. REFCORR5 Batch 6 adds the
        // composite's empty Raw token, which also renders to nothing, so a
        // term made only of that placeholder must omit its <dt> just as a
        // Comment-only term does.
        $wiki = $this->wiki;
        $stripped = preg_replace_callback('/\xFF(\d+)\xFF/',
            function ($m) use ($wiki) {
                $id = (int) $m[1];
                if (! isset($wiki->tokens[$id])) {
                    return $m[0];
                }
                if ($wiki->tokens[$id][0] === 'Comment') {
                    return '';
                }
                if ($wiki->tokens[$id][0] === 'Raw' && $wiki->tokens[$id][1]['text'] === '') {
                    return '';
                }
                return $m[0];
            }, $term);
        return trim($stripped) === '';
    }
}
