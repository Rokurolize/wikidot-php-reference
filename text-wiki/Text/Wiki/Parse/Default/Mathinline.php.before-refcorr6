<?php

/**
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
* Parses for text marked as inline math.
* 
* This class implements a Text_Wiki_Parse to find math invocation code, 
* i.e. [[$ equation $]]
*
* @category Text
* 
* @package Text_Wiki
* 
* @author Michal Frackowiak
* 
*/

class Text_Wiki_Parse_Mathinline extends Text_Wiki_Parse {

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

     public $regex = '/\[\[\$(.*?)\$\]\]/';
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
    	$content = trim($matches[1]);

        // Earlier rules have already replaced their own spans with
        // \xFF<token-id>\xFF placeholders by the time this late rule runs.
        // ftml's legacy math collector and live Wikidot both suppress the
        // whole LaTeX body when a line break or a raw region occurs inside
        // [[$ ... $]], rendering an empty formula ("$$"). Comments are
        // elided by their own rule and leave no placeholder, so they do not
        // suppress. Resolve each placeholder through the token table rather
        // than guessing from the bytes.
        if (strpos($content, $this->wiki->delim) !== false
            && preg_match_all('/\xFF(\d+)\xFF/', $content, $ph)) {
            foreach ($ph[0] as $i => $whole) {
                $tid = $ph[1][$i];
                if (!isset($this->wiki->tokens[$tid])) {
                    continue;
                }
                $token = $this->wiki->tokens[$tid];
                $name = isset($token[0]) ? $token[0] : '';
                $options = isset($token[1]) && is_array($token[1]) ? $token[1] : array();
                // A line break or a raw region anywhere in the body makes
                // live suppress the whole formula to "$$".
                if (in_array($name, array('Newline', 'Raw'), true)) {
                    $content = '';
                    break;
                }
                // Other earlier-rule spans (notably a bare URL) contribute
                // their literal text to the LaTeX source, which live renders.
                if (isset($options['text']) && is_string($options['text'])) {
                    $replacement = $options['text'];
                } elseif (isset($options['href']) && is_string($options['href'])) {
                    $replacement = $options['href'];
                } else {
                    $replacement = '';
                }
                $content = str_replace($whole, $replacement, $content);
            }
        }

        $options = array('content'=>$content);

        return $this->wiki->addToken($this->rule, $options);
    }
}
