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
* Parses for [[size]] tags.
*
* @category Text
* 
* @package Text_Wiki
* 
* @author Michal Frackowiak
* 
*/

class Text_Wiki_Parse_Size extends Text_Wiki_Parse {

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

	// R2-contain: the fossil used ((?:(?R)|.)*?) for the body, which pairs an
	// outer opener with a whole nested pair and tokenizes it before the inner
	// pair is seen. That leaves an empty outer <span> when the nested pair is
	// empty (live probe empty-nested renders nothing). Matching innermost pairs
	// first and letting parse() recurse gives the same nesting for non-empty
	// pairs while letting the empty-body suppression below apply inside-out.
	// REFCORR5 Batch 8 (p26): a recursive body lets a valid outer pair claim a
	// span containing an invalid inner pair, which stays literal in the body.
	public $regex = '/\[\[size\s([^\]]+)\]\]((?:(?R)|.)*?)\[\[\/size\]\]/msi'; 
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
    		
    		$content =$matches[2];
    
    		$size = trim($matches[1]);
    		
    		$allowedSizes = array(
    			'/^[0-9\.]{1,5}(em|px|%)$/',
    			'/^xx\-small$/',
			'/^x\-small$/',
			'/^small$/',
			'/^medium$/',
			'/^large$/',
			'/^x\-large$/',
			'/^xx\-large$/',
			'/^smaller$/',
			'/^larger$/'
    		);
    
    		$good = false;
    		foreach($allowedSizes as $as){
    			if(preg_match($as, $size)){
    				$good=true;
    				break;
    			}
    		}
    		
    		if($good==false){
    			return $matches[0];	
    		}
    
        // R2-contain corrections, settled by live saved-page probes and ftml's
        // Wikidot-layout pins. (1) Live discards the C0 control bytes Wikidot
        // treats as discarded controls (pin whitespace-size-body-nul: A<NUL>B
        // renders as AB); the fossil kept them in the body. (2) Live drops
        // trailing ASCII spaces and tabs at a line end, including immediately
        // before [[/size]] (probes space-before-close, multi-space-close,
        // tab-close, internal-space-newline) but keeps the line break itself
        // (newline-close) and keeps a non-breaking space (nbsp-close).
        // (3) Live drops a size construct whose body has no visible content
        // (empty-body, ws-body, empty-nested probes) where the fossil emitted
        // an empty <span>. Consuming the whole construct also lets the
        // recursive parse() collapse nested pairs that become empty.
        $content = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1A\x1C-\x1F]/', '', $content);
        $content = preg_replace('/[ \t]+(?=\n|$)/', '', $content);
        if($content === ''){
            return '';
        }

        $options = array('size'=>$size, 'type'=>'start');
      	
        $start = $this->wiki->addToken($this->rule, $options);

        $end = $this->wiki->addToken(
            $this->rule, array('type' => 'end')
        );
        
        return $start . $content  .$end;

    }
    
    function parse(){
    	$oldSource = $this->wiki->source;
        $this->wiki->source = preg_replace_callback(
           	$this->regex,
           	array(&$this, 'process'),
           	$this->wiki->source
        );
        if($oldSource != $this->wiki->source){
        	$this->parse();
        }
    }
    
}
