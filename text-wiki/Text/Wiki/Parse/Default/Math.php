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
* Parses for text marked as a math block.
* 
* This class implements a Text_Wiki_Parse to find math invocation code, 
* i.e. [[math label]] equation [[/math]]
*
* @category Text
* 
* @package Text_Wiki
* 
* @author Michal Frackowiak
* 
*/

class Text_Wiki_Parse_Math extends Text_Wiki_Parse {

    static $equationsArray = array();
    
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
    
     public $regex = ';^\[\[math(\s+[a-z0-9_]*?)?((?:\s+[a-z0-9]+="[^"]*"))*\s*\]\]((?:(?R)(?!\s*\[\[/math\]\])|.)*?)\n\[\[/math\]\](\s|$);msi';
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
    
    function process($matches){
        
        if($this->wiki->vars['math_id'] == null){
    			$this->wiki->vars['math_id'] = 1;
    	}
    	$id = $this->wiki->vars['math_id'];
    	$this->wiki->vars['math_id']++;
        
	    $label = trim($matches[1]);
	    $content = trim($matches[3]);
	    
	    if(preg_match(';include\s*\{|input\s*\{;is', $content)){
	    	throw new ProcessException("Invalid LaTeX expression(s) found.");	
	    }
	    
	    $args = $this->getAttrs($matches[2]);
	   	// REFCORR3 C-SUSPECT-SERVING-1: live preserves any arbitrary
	   	// lower-case environment name, defaults an ABSENT type to "align",
	   	// and rejects an empty or upper-case value with an error block. The
	   	// old two-name whitelist silently collapsed everything else to
	   	// "equation". The decision (and the render's validation) is by the
	   	// value's case, so the raw value is kept here for the renderer;
	   	// the equation counter above has already advanced for every block,
	   	// including rejected ones, as live's ids 3/4 show.
	   	// REFCORR8 C-R5-P2-3 / REFCORR9 R9-C: a stray positional label
	   	// (the `a` in `[[math a TYPE="align"]]`) is harmless, and an
	   	// attribute whose NAME is any case variant of `type` other than
	   	// the exact lower-case spelling (`TYPE`, `Type`, `tYpE`, ...) is
	   	// not the lower-case `type` key that live looks up. REFCORR11
	   	// C-R5D-P2-4 generalizes the fallback: every cached live Math
	   	// capture (bare `[[math]]`, variant names, labelled openers with
	   	// no type) serves the fossil \begin{equation} envelope with the
	   	// counter, so ANY missing exact lower-case `type` key now selects
	   	// `equation`, whether genuinely absent or present only as a case
	   	// variant. The REFCORR3 absent-type default `align` is retired.
	   	// Only an exact lower-case `type` key can select a non-equation
	   	// environment, and its value is still passed verbatim to the
	   	// renderer's validation. The counter and the valid/invalid value
	   	// handling are untouched.
	   	$type = array_key_exists('type', $args) ? $args['type'] : 'equation';
    	
        $options = array('label'=>$label, 'content'=>$content, 'id'=>$id, 'type' => $type);
        self::$equationsArray[$label] = $id;
        $id++;
        return "\n\n".$this->wiki->addToken($this->rule, $options)."\n\n";
    }
}
