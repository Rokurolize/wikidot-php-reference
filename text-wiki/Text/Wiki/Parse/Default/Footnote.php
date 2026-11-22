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

	    // REFCORR7: an empty-Raw placeholder is the byte string
	    // \xFF<id>\xFF naming a token ['Raw', ['text' => '']] whose render
	    // is nothing (Tighten deletes it; the Raw renderer emits no bytes).
	    // A body made only of such placeholders is empty on live (S4C
	    // fn-empty, fn-ws): strip them from the stored body so the existing
	    // `$body !== ''` emptiness test in Footnoteitem::token sees empty.
	    // The literal remainder survives (fn-six keeps "@@"), and a
	    // non-empty Raw token (fn-free's "x") is left intact. The same
	    // stripping is mirrored in LeanFtml.NotesRules.footnoteProcess,
	    // so the compared footnotes state stays byte-identical across
	    // the two sides; no token entry is added or reindexed.
	    $delim = preg_quote($this->wiki->delim, '/');
	    $content = preg_replace_callback(
	        '/' . $delim . '(\d+)' . $delim . '/',
	        function ($m) {
	            $tok = $this->wiki->tokens[(int) $m[1]] ?? null;
	            if ($tok !== null && $tok[0] === 'Raw'
	                && isset($tok[1]['text']) && $tok[1]['text'] === '') {
	                return '';
	            }
	            return $m[0];
	        },
	        $content);

	    $this->wiki->vars['footnotes'][$id-1] = $content;
        $options = array('id'=>$id);
       
        return $this->wiki->addToken($this->rule, $options);
    }
}
