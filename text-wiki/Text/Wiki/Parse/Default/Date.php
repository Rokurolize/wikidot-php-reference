<?php
/**
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
 * Creates a date string.
 *
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Michal Frackowiak
 * 
 */
class Text_Wiki_Parse_Date extends Text_Wiki_Parse {
 
	
 
    // Three patterns are used: the first requires a (possibly negative) Unix timestamp; the second matches a blank value followed by whitespace or the closer, which live renders as nothing whether or not attributes follow; the third is a no-attribute blank with a single space. A non-numeric value with no leading blank stays literal, as live does.
	public $regex = array(
        ';\[\[date\s+(-?[0-9]+)(\s+.*?)?\]\];',
        ';\[\[date\s+(?=\s|\]\])\s*(.*?)\]\];',
        ';\[\[date\s+\]\];'
    );
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
     
     function process($matches)
     {
     	
     	$options = array();
     	$numeric = isset($matches[1]) && preg_match('/^-?[0-9]+$/', $matches[1]);
     	$options['timestamp'] = $numeric ? $matches[1] : '';
     	
     	$attrText = $numeric ? (isset($matches[2]) ? $matches[2] : '') : (isset($matches[1]) ? $matches[1] : '');
     	$attr = $this->getAttrs(trim($attrText));
     	foreach($attr as $key => $a){
     		$options[$key] = $attr[$key];
     	}
     	
     	$token = $this->wiki->addToken(
             $this->rule, $options
         );
         
         return $token;
     }
 
 }
