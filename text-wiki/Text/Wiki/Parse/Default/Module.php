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

class Text_Wiki_Parse_Module extends Text_Wiki_Parse {

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
    
    // R2 MODULE CORRECTION (2026-11-20): the fossil's optional body group used
    // (.*?), so an empty body still consumed the [[/module]] closer. Live
    // leaves that closer as literal text for both unknown and known modules
    // (probes muse-probe-r2mod-module-mod-probe-unknown-empty-body and
    // -mod-probe-known-empty-body; ftml's own pin
    // test/module/css-empty-module-paragraph-break/wikidot.html shows the
    // same literal closer). Requiring one or more body characters makes the
    // closer survive when the body is empty; non-empty bodies and all other
    // matching behavior are unchanged.
    public $regex = "/^\[\[module\s([a-z0-9_\-\/]+)(\s+.*?)?\]\] *\n(?:(.+?)\[\[\/module\]\])?/ism";

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
    
    function parse() {
        
        do {
            $oldText = ($this->wiki->source);
            if ($this->regex) {
                $this->wiki->source = preg_replace_callback($this->regex, array(
                    &$this, 
                    'process'), $this->wiki->source);
            }
        } while ($oldText !== $this->wiki->source);
    }

    function process($matches) {
        // check if not containing another module!!!
        $con = $matches[0];
        
        if (preg_match_all('/^\[\[module\s([a-z0-9_\-\/]+)(\s+.*?)?\]\]/smi', $con, $dummy) > 1) {
            return preg_replace('/^\[\[module/', '[[module654', $con);
        }
        
        $moduleName = trim($matches[1]);
        
        // are there additional attribute arguments?
        $attr = trim($matches[2]);
        
        $body = trim($matches[3]); // optional module "body" between tags

        $options = array('moduleName' => $moduleName, 'attr' => $attr, 
            'module_body' => $body);

        $out = "\n\n" . $this->wiki->addToken($this->rule, $options) . "\n\n";

        // C-SUSPECT-XRULE-3: when an earlier rule has claimed part of the
        // body, live leaves that body and the literal closer in the source
        // after the unknown-module error; the error token alone is not the
        // whole claim.
        if (strpos($body, $this->wiki->delim) !== false) {
            $out .= $matches[3] . '[[/module]]';
        }

        return $out;
    }
}
