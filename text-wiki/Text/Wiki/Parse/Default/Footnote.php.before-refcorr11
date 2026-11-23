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
	    $visible = $stripEmptyRaw($content);
	    // Preserve the placeholder-bearing body exactly when it carries a
	    // single authored line break: a LF with a non-LF byte on each side.
	    // Double-LF runs and bare/edge LFs have no live <br /> and take the
	    // trimmed visible path. C0 controls other than TAB/LF/CR are dropped,
	    // matching live purifyHtml (notably form feed).
	    if (preg_match('/[^\n]\n(?!\n)/', $content)) {
	        $content = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F]/', '', $content);
	    } else {
	        $content = trim($visible);
	    }

	    $this->wiki->vars['footnotes'][$id-1] = $content;
        $options = array('id'=>$id);
       
        return $this->wiki->addToken($this->rule, $options);
    }
}
