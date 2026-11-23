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

	    // REFCORR11 — the live C0-control filter is UNCONDITIONAL, not
	    // branch-local. PHP trim's default charlist excludes form feed (12),
	    // so the old REFCORR10 fallback branch left an FF in the stored body
	    // before a double-LF run or with no authored LF (C-R5D-R3-1 / R3D-F2).
	    // Drop the class once, before the break decision and the visible
	    // projection, so both branches store an already-pure body. Empty-Raw
	    // placeholders (0xFF<id>0xFF) and TAB/LF/CR are untouched, so the
	    // single-authored-break witness R3D-F3 still emits its <br />.
	    // REFCORR12 — narrow the class to the live-discarded set D = the C0
	    // bytes below 0x20 except TAB (9), LF (10), CR (13) and ESC (27):
	    // [\x00-\x08\x0B\x0C\x0E-\x1A\x1C-\x1F]. Live keeps ESC verbatim in a
	    // footnote body (C-R5E-P4-1 / C-R5E-S1-2), so the REFCORR11 upper range
	    // 0x0E-0x1F was too wide by one byte; the Tighten residual class already
	    // uses this exact narrower set. VT, FF and the other discarded bytes
	    // are still dropped on every branch.
	    $content = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1A\x1C-\x1F]/', '', $content);

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
	    $visible = $stripEmptyRaw($content);
	    // After the unconditional REFCORR11 control drop, the break test now
	    // decides ONLY placeholder retention: keep the placeholder-bearing
	    // control-pure body for a single authored LF (a LF with a non-LF byte
	    // on each side) so Newline emits <br />. Double-LF runs, bare/edge LFs
	    // and no-LF bodies have no live <br /> and take the trimmed visible
	    // path. The control filter above is common to both branches.
	    if (!preg_match('/[^\n]\n(?!\n)/', $content)) {
	        $content = trim($visible);
	    }

	    $this->wiki->vars['footnotes'][$id-1] = $content;
        $options = array('id'=>$id);
       
        return $this->wiki->addToken($this->rule, $options);
    }
}
