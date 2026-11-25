<?php

/**
 * 
 * Parses for modules.
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
 * Parses for modules.
 *
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Michal Frackowiak
 * 
 */

class Text_Wiki_Parse_Module654 extends Text_Wiki_Parse {
    
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
    
    // R2 MODULE654 CORRECTION (2026-11-20): the fossil required a newline
    // immediately after the opener. Live Wikidot also claims an opener whose
    // line has trailing horizontal whitespace before the newline (saved page
    // muse-probe-r2mod-module654-p-upper-newline-spaces, valid/stable/
    // saved_source_matches=true), exactly as the sibling Module rule already
    // does with its " *\n". Fossil-era artifact; name charset (leading digit,
    // slash), case-insensitive opener and [[/module]] closer were probed and
    // need no change.
    public $regex = "/^\[\[module654\s([a-z0-9_\-\/]+)(\s+.*?)?\]\][ \t]*\n(?:(.*?)\[\[\/module\]\])?/ims";

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
    
    function process($matches) {
        $rawBody = isset($matches[3]) ? $matches[3] : '';
        $moduleName = trim($matches[1]);
        
        // are there additional attribute arguments?
        $attr = trim($matches[2]);
        
        if ($rawBody !== '' && $this->textHasTokenRule($rawBody, 'Html')) {
            $options = array('moduleName' => $moduleName, 'attr' => $attr,
                'module_body' => '');
            $closer = substr($matches[0], -11);
            return "\n\n" . $this->wiki->addToken($this->rule, $options) . "\n\n"
                . $rawBody . $closer;
        }

        $body = trim($matches[3]); // optional module "body" between tags
        

        $options = array('moduleName' => $moduleName, 'attr' => $attr, 
            'module_body' => $body);
        
        return "\n\n" . $this->wiki->addToken($this->rule, $options) . "\n\n";
    }
}
