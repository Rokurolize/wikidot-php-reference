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
    
    function parse()
    {
        $this->evalHashIf();
        parent::parse();
    }

    /**
     * REFCORR15: resolve Wikidot's [[#if cond | true | false]] parser function
     * before Comment, Div, Anchor, Url, and Paragraph rules run (while already
     * after Code/Html/Raw tokenization).
     */
    private function evalHashIf()
    {
        $src = $this->wiki->source;
        if (strpos($src, '[[#if') === false) {
            return;
        }
        for ($pass = 0; $pass < 64; $pass++) {
            $n = strlen($src);
            $out = '';
            $lastCopied = 0;
            $cursor = 0;
            $changed = false;
            while ($cursor < $n) {
                $pos = strpos($src, '[[#if', $cursor);
                if ($pos === false) {
                    break;
                }
                if ($pos + 5 >= $n || ($src[$pos + 5] !== ' ' && $src[$pos + 5] !== "\t")) {
                    $cursor = $pos + 5;
                    continue;
                }
                $bodyStart = $pos + 6;
                $closePos = strpos($src, ']]', $bodyStart);
                if ($closePos === false) {
                    break;
                }
                $interior = substr($src, $bodyStart, $closePos - $bodyStart);
                // If an inner [[#if starts before ]], jump to it so innermost resolves first.
                $innerIf = strpos($interior, '[[#if');
                if ($innerIf !== false) {
                    $cursor = $bodyStart + $innerIf;
                    continue;
                }
                // Guard against unclosed or crossing [[...]] link brackets inside the body.
                if (strpos($interior, '[[') !== false) {
                    $cursor = $pos + 5;
                    continue;
                }
                $intLen = strlen($interior);
                $firstSep = null;
                $lastSep = null;
                $sepCount = 0;
                for ($k = 1; $k < $intLen - 1; $k++) {
                    if ($interior[$k] === '|'
                        && ($interior[$k - 1] === ' ' || $interior[$k - 1] === "\t")
                        && ($interior[$k + 1] === ' ' || $interior[$k + 1] === "\t")) {
                        if ($firstSep === null) {
                            $firstSep = $k;
                        }
                        $lastSep = $k;
                        $sepCount++;
                    }
                }
                if ($sepCount === 0) {
                    $condTrim = trim($interior, " \t");
                    if ($condTrim === '' || $condTrim === '0' || $condTrim === '1'
                        || strpos($condTrim, '0|') === 0 || strpos($condTrim, '1|') === 0
                        || strpos($condTrim, '0 |') === 0 || strpos($condTrim, '1 |') === 0) {
                        $replacement = '';
                    } else {
                        $cursor = $pos + 5;
                        continue;
                    }
                } else {
                    $condition = substr($interior, 0, $firstSep);
                    $cLen = strlen($condition);
                    $authored = ($cLen > 0 && ($condition[$cLen - 1] === ' ' || $condition[$cLen - 1] === "\t"))
                        ? substr($condition, 0, -1)
                        : $condition;
                    $semantic = trim($condition, " \t");
                    $truth = ($authored !== '' && $semantic !== '0'
                        && $semantic !== 'null' && strcasecmp($semantic, 'false') !== 0);
                    $whenTrue = ($sepCount > 1)
                        ? substr($interior, $firstSep + 1, $lastSep - $firstSep - 1)
                        : substr($interior, $firstSep + 1);
                    $whenFalse = ($sepCount > 1)
                        ? substr($interior, $lastSep + 1)
                        : '';
                    $replacement = trim($truth ? $whenTrue : $whenFalse, ' ');
                }
                $out .= substr($src, $lastCopied, $pos - $lastCopied) . $replacement;
                $lastCopied = $closePos + 2;
                $cursor = $lastCopied;
                $changed = true;
            }
            if (!$changed) {
                break;
            }
            $src = $out . substr($src, $lastCopied);
        }
        $this->wiki->source = $src;
    }

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
