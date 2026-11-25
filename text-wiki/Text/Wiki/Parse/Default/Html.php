<?php

/**
* 
* Parses for blocks of HTML code.
* 
* @category Text
* 
* @package Text_Wiki
* 
* @author Paul M. Jones <pmjones@php.net>
* 
* @license LGPL
* 
* @version $Id$
* 
*/

/**
* 
* Parses for blocks of HTML code.
* 
* This class implements a Text_Wiki_Parse to find source text marked as
* HTML to be redndred as-is.  The block start is marked by <html> on its
* own line, and the block end is marked by </html> on its own line.
*
* @category Text
* 
* @package Text_Wiki
* 
* @author Paul M. Jones <pmjones@php.net>
* 
*/

class Text_Wiki_Parse_Html extends Text_Wiki_Parse {

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
    
    // REFCORR19 F2: match live's [[html]] ... [[/html]] block form as well
    // as the legacy <html> ... </html> form the rule originally handled.
    // Group 1/2 are the legacy body/trailer; group 3/4 the [[html]] body and
    // trailer.
    public $regex = '/\[\[html(?:\s+[^\]\n]*)?\]\][ \t]*\n?(.*?)\n?[ \t]*\[\[\/html\]\](\s|$)/msi';

    /**
    * 
    * Generates a replacement for the matched text.  Token options are:
    * 
    * 'text' => The text of the HTML to be rendered as-is.
    * 
    * @access public
    *
    * @param array &$matches The array of matches from parse().
    *
    * @return A delimited token to be used as a placeholder in
    * the source text, plus any text following the HTML block.
    *
    */
    
    function process($matches)
    {
        // REFCORR19 F2: group 1 is the block body, group 2 its trailer.
        $text = isset($matches[1]) ? $matches[1] : '';
        $trailer = isset($matches[2]) ? $matches[2] : '';
        $options = array('text' => $text);
        // Optional class/style on the opener, in live's form.
        $opener = isset($matches[0]) ? $matches[0] : '';
        if (preg_match('/\[\[html\s+([^\]\n]*)\]\]/i', $opener, $am)) {
            if (preg_match('/\bclass\s*=\s*"([^"]*)"/i', $am[1], $cm)) {
                $options['class'] = $cm[1];
            }
            if (preg_match('/\bstyle\s*=\s*"([^"]*)"/i', $am[1], $sm)) {
                $options['style'] = $sm[1];
            }
        }
        return $this->wiki->addToken($this->rule, $options) . $trailer;
    }
}
