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
        $rawBody = isset($matches[3]) ? $matches[3] : '';
        if ($rawBody !== '' && $this->textHasTokenRule($rawBody, 'Html')) {
            $moduleName = trim($matches[1]);
            $attr = trim($matches[2]);
            $options = array('moduleName' => $moduleName, 'attr' => $attr,
                'module_body' => '');
            $closer = substr($matches[0], -11);
            return "\n\n" . $this->wiki->addToken($this->rule, $options) . "\n\n"
                . $rawBody . $closer;
        }

        // check if not containing another module!!!
        $con = $matches[0];
        
        if (preg_match_all('/^\[\[module\s([a-z0-9_\-\/]+)(\s+.*?)?\]\]/smi', $con, $dummy) > 1) {
            // REFCORR10 general nested-module rule: consumption through
            // trailing closers applies to EVERY nested module opener, not
            // only one whose own tail already ends in a newline. The
            // established F13 composition lets Module claim each line-
            // terminated inner opener and Module654 then claim the outer
            // one through the final closer. An inline inner opener has no
            // newline after its ]], so Module's opener grammar cannot claim
            // it and the outer lazy body stops at the inner closer, leaving
            // the outer closer literal (C-R5C-P3-2). Give every inline nested
            // opener the newline its grammar requires so the same composition
            // consumes one closer per opener and no residual closer survives.
            $con = preg_replace('/^(\[\[module[^\]]*\]\])(?! *\n)/mi', "$1\n", $con);
            return preg_replace('/^\[\[module/', '[[module654', $con);
        }
        
        $moduleName = trim($matches[1]);
        
        // are there additional attribute arguments?
        $attr = trim($matches[2]);
        
        $body = trim($matches[3]); // optional module "body" between tags

        $options = array('moduleName' => $moduleName, 'attr' => $attr, 
            'module_body' => $body);

        $out = "\n\n" . $this->wiki->addToken($this->rule, $options) . "\n\n";

        // C-SUSPECT-XRULE-3: when an earlier *block* rule (Code) has claimed
        // part of the body, live leaves that body and the literal closer in
        // the source after the unknown-module error (probe
        // muse-probe-suspect-xrule-x19-module-code); the error token alone is
        // not the whole claim there.
        // REFCORR7 (SUSPECT4-C S11 inc-mod / S14 inc-css): a Raw token in the
        // body is different. Include splices @@...@@ into the module body and
        // Raw claims it before Module runs; live consumes that token with the
        // closer and emits only the module result (error block for an unknown
        // module, a style element for css). The old delimiter test re-emitted
        // the raw span and the literal [[/module]] into #page-content, which
        // live never does. Re-emit only when the body holds a Code token, and
        // leave a Raw-token body to the module token.
        $reemit = false;
        foreach ($this->wiki->tokens as $tid => $tok) {
            if ($tok[0] === 'Code'
                && strpos($body, $this->wiki->delim . $tid . $this->wiki->delim) !== false) {
                $reemit = true;
                break;
            }
        }
        if ($reemit) {
            // REFCORR9 C-R5B-P3-3: the opener/closer regex is case-insensitive
            // (/ism), so the authored closer spelling must survive the Code-
            // token re-emit. The regex match ends at the closer, whose ASCII
            // byte length is fixed at 11 ([[/module]]); carry those exact
            // matched bytes instead of concatenating a hard-coded lowercase
            // literal. The Code-only gate above (REFCORR7 Raw suppression,
            // REFCORR8 narrowing) and the token wire shape are unchanged.
            $closer = substr($matches[0], -11);
            $out .= $matches[3] . $closer;
        }

        return $out;
    }
}
