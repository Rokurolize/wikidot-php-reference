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
* This class implements a Text_Wiki_Parse to find math invocation code, 
* i.e. [[footnote]] text [[/footnote]]
*
* @category Text
* 
* @package Text_Wiki
* 
* @author Michal Frackowiak
* 
*/

class Text_Wiki_Parse_Footnote extends Text_Wiki_Parse {

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

    public $regex = ';\s*\[\[footnote\]\](.*?)\[\[/footnote\]\];s';

    function process($matches)
    {
    		if($this->wiki->vars['footnotes'] == null){
    			$this->wiki->vars['footnotes'] = array();
    		}
    	 	$id = count($this->wiki->vars['footnotes'])+1;
   	 	//echo "dup[a]"
   	 	
	    	$content = trim($matches[1]);

	    // REFCORR10 — one general token-aware live rule for the footnote body.
	    // The stored body is re-parsed as wiki source by Footnoteblock::process,
	    // so empty-Raw placeholders must be kept wherever an authored LF needs
	    // an inline witness byte for the Newline rule to emit <br />. Emptiness
	    // and the separator space are decided from the visible projection: the
	    // same body with empty-Raw placeholders removed (Footnoteitem::token).
	    $delim = preg_quote($this->wiki->delim, '/');
	    $stripEmptyRaw = function ($text) use ($delim) {
	        return preg_replace_callback(
	            '/' . $delim . '(\d+)' . $delim . '/',
	            function ($m) {
	                $tok = $this->wiki->tokens[(int) $m[1]] ?? null;
	                if ($tok !== null && $tok[0] === 'Raw'
	                    && isset($tok[1]['text']) && $tok[1]['text'] === '') {
	                    return '';
	                }
	                return $m[0];
	            },
	            $text);
	    };
	    // REFCORR13 C-R5F-R3-3: the authored-break predicate runs on the
	    // control-BEARING trimmed body, before the live-discarded C0 class is
	    // dropped. Live stores the raw trimmed body; Stage 2 purifyHtml drops
	    // discarded C0 bytes only from the emitted text, so a bare FF (or VT,
	    // or any other live-discarded byte) immediately before a single LF is
	    // a real inline witness for the Newline rule and yields a rule-level
	    // <br />. REFCORR11/12 dropped the class BEFORE this test, erasing the
	    // sole non-LF witness and losing the <br /> (C-R5F-R3-3, R3F-16).
	    // The predicate still decides ONLY placeholder retention; keep the
	    // placeholder- and control-bearing body for a single authored LF.
	    if (!preg_match('/[^\n]\n(?!\n)/', $content)) {
	        // Double-LF runs, bare/edge LFs and no-LF bodies have no live
	        // <br /> and take the trimmed visible path. REFCORR12's class D is
	        // the live-discarded C0 set below 0x20 except TAB (9), LF (10),
	        // CR (13) and ESC (27):
	        // [\x00-\x08\x0B\x0C\x0E-\x1A\x1C-\x1F]. Dropping it here (not
	        // before the predicate) keeps every cached REFCORR11/12 shape
	        // byte-identical: ESC is retained verbatim, VT/FF and the rest are
	        // removed on this fallback branch exactly as before.
	        $content = trim($stripEmptyRaw(
	            preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1A\x1C-\x1F]/', '', $content)));
	    }

	    $this->wiki->vars['footnotes'][$id-1] = $content;
        $options = array('id'=>$id);
       
        return $this->wiki->addToken($this->rule, $options);
    }
}
