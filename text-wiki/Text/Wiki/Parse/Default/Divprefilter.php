<?php

/**
* 
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
* Parses for text marked as a div block.
* 
* This removes spaces between to subseqent div blocks.
*
* @category Text
* 
* @package Text_Wiki
* 
* @author Michal Frackowiak
* 
*/

class Text_Wiki_Parse_Divprefilter extends Text_Wiki_Parse {

    /**
    * 
    * The regular expression used to find source text matching this
    * rule.
    * 
    * @access public
    * 
    * @var string
    * 
    */

	public $regex = '/\[\[\/div\]\](\s*?)\[\[div/msi'; 
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
    
    function parse()
    {
        parent::parse();
        $sentinel = "\xEF\xBF\xBE\xEF\xBF\xBF";
        foreach ($this->wiki->tokens as $id => $token) {
            if (!isset($token[1]) || !is_array($token[1])) {
                continue;
            }
            foreach ($token[1] as $key => $value) {
                if (is_string($value) && strpos($value, $sentinel) !== false) {
                    $this->wiki->tokens[$id][1][$key] = str_replace($sentinel, ' ', $value);
                }
            }
        }
    }

    function process($matches)
    {     
        return '[[/div]][[div';

    }
}
