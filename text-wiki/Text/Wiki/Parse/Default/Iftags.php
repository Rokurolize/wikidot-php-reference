<?php
/**
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
 * Creates a conditional, tag-based block.
 *
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Michal Frackowiak
 * 
 */
class Text_Wiki_Parse_Iftags extends Text_Wiki_Parse {


	public $regex = ';\[\[iftags(\s[^\]]*)?\]\]((?:(?R)|.)*?)\[\[/iftags\]\];msi';

	
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
    	$page = $this->wiki->vars['page'];
    	if(!$page){
    		$pageName = $this->wiki->vars['pageName'];
	    	$site = $GLOBALS['site'];
	    	$page = DB_PagePeer::instance()->selectByName($site->getSiteId(), $pageName);
    	}
    	if(!$page) {
    		return;
    	}
    	
    	$tags = $page->getTagsAsArray();
    	$hasTag = function($needle) use ($tags) { foreach($tags as $tag) { if (strcasecmp($tag, $needle) === 0) { return true; } } return false; };	

    	
    	$tags0 = preg_split(';[, ]+;', trim($matches[1]));
    	
    	$allTags = array();
    	$noTags = array();
    	$anyTags = array();
    	
    	foreach($tags0 as $t){
    		if (substr($t, 0, 1) == '+') {
               $allTags[] = substr($t, 1);
            } elseif (substr($t, 0, 1) == '-') {
               $noTags[] = substr($t, 1);
            } else {
            	$anyTags[] = $t;
            }
    	}
    	
    	if(count($allTags) > 0){
    		foreach($allTags as $t){
    			/* If any of the required tags is not present, return ''. */
    			if(!$hasTag($t)){
    				return '';
    			}
    		}
    	}
   		if(count($noTags) > 0){
    		foreach($noTags as $t){
    			/* If any of the forbidden tags is present, return ''. */
    			if($hasTag($t)){
    				return '';
    			}
    		}
    	}
    	
    	if(count($anyTags) > 0){
    		foreach($anyTags as $t){
    			/* If any of the "any" tags is present, return the content. */
    			if($hasTag($t)){
    				return $matches[2];
    			}
    		}
    		/* If not, return ''. */
    		return '';
    	}
    	
    	/* If we are here, the content should be returned. */
    	return $matches[2];
    }

}
