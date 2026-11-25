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
        $stripped = '';
        $offset = 0;
        $contentLen = strlen($content);
        while ($offset < $contentLen) {
            $lineEnd = strpos($content, "\n", $offset);
            $hasNewline = $lineEnd !== false;
            if (!$hasNewline) {
                $lineEnd = $contentLen;
            }
            $line = substr($content, $offset, $lineEnd - $offset);
            if (preg_match('/^[ \t]+$/', $line) && $hasNewline) {
                $line = ' ';
            } else {
                $line = preg_replace('/[ \t]+$/', '', $line);
            }
            $stripped .= $line . ($hasNewline ? "\n" : '');
            $offset = $lineEnd + 1;
        }
        $content = $stripped;
        if($content === ''){
            return '';
        }

        $split = null;
        $seenVisible = false;
        $lineStart = 0;
        $contentLen = strlen($content);
        $emptyRawLine = '/^' . preg_quote($this->wiki->delim, '/')
            . '(\d+)' . preg_quote($this->wiki->delim, '/') . '$/';
        while ($lineStart < $contentLen) {
            $lineEnd = strpos($content, "\n", $lineStart);
            if ($lineEnd === false) {
                $lineEnd = $contentLen;
            }
            $line = substr($content, $lineStart, $lineEnd - $lineStart);
            $isEmptyRaw = false;
            if (preg_match($emptyRawLine, $line, $rawMatch)
                && isset($this->wiki->tokens[(int)$rawMatch[1]])
                && $this->wiki->tokens[(int)$rawMatch[1]][0] === 'Raw'
                && $this->wiki->tokens[(int)$rawMatch[1]][1]['text'] === '') {
                $isEmptyRaw = true;
            }
            if ($seenVisible && $isEmptyRaw) {
                $nextStart = $lineEnd + 1;
                if ($nextStart < $contentLen
                    && substr($content, $nextStart, 2) === '= ') {
                    $split = $lineStart;
                    break;
                }
            }
            if (!$isEmptyRaw && trim($line) !== '') {
                $seenVisible = true;
            }
            $lineStart = $lineEnd + 1;
        }

        $options = array('size'=>$size, 'type'=>'start');
      	
        $start = $this->wiki->addToken($this->rule, $options);

        $end = $this->wiki->addToken(
            $this->rule, array('type' => 'end')
        );
        
        if ($split !== null) {
            return $start . substr($content, 0, $split) . $end
                . substr($content, $split)
                . $this->wiki->addToken($this->rule, array('type' => 'end'));
        }
        return $start . $content  .$end;

    }
    
    function parse(){
        do {
            $oldSource = $this->wiki->source;
            $this->wiki->source = $this->_scanSize($oldSource);
        } while ($oldSource != $this->wiki->source);
    }

    /**
     * REFCORR16: linear-time scan replacing the whole-document recursive (?R) preg_replace_callback, whose PCRE JIT stack exhaustion silently wiped large documents (measured on real pages in the package 2.1 holdout). The public $regex remains the definitional pattern; the scanner reproduces the pattern's pairing semantics exactly, including PCRE's preference order at each body position (closer first, then a complete nested block, then one character) and its demotion backtrack: a nested block that leaves the enclosing block unclosable is demoted to literal text so the enclosing block can close at the nested block's closer.
     */
    private function _scanSize($src) {
        $n = strlen($src);
        $out = '';
        $last = 0;
        $pos = 0;
        $memo = array();
        while ($pos < $n) {
            $cand = stripos($src, '[[size', $pos);
            if ($cand === false) {
                break;
            }
            $m = $this->_sizeBlock($src, $cand, $memo);
            if ($m === false) {
                $pos = $cand + 1;
                continue;
            }
            $out .= substr($src, $last, $cand - $last);
            $out .= $this->process($m[1]);
            $last = $m[0];
            $pos = $m[0];
        }
        return $out . substr($src, $last);
    }

    private function _sizeBlock($src, $p, &$memo) {
        $bk = 'b' . $p;
        if (array_key_exists($bk, $memo)) {
            return $memo[$bk];
        }
        if (!preg_match('/\G\[\[size\s([^\]]+)\]\]/i', $src, $om, 0, $p)) {
            return $memo[$bk] = false;
        }
        $bodyStart = $p + strlen($om[0]);
        if (stripos($src, '[[/size]]', $bodyStart) === false) {
            return $memo[$bk] = false;
        }
        $c = $this->_sizeBody($src, $bodyStart, $memo);
        if ($c === false) {
            return $memo[$bk] = false;
        }
        $matches = array(substr($src, $p, $c[1] - $p), $om[1], substr($src, $bodyStart, $c[0] - $bodyStart));
        return $memo[$bk] = array($c[1], $matches);
    }

    private function _sizeBody($src, $pos, &$memo) {
        $sk = 's' . $pos;
        if (array_key_exists($sk, $memo)) {
            return $memo[$sk];
        }
        if (preg_match('/\G\[\[\/size\]\]/i', $src, $cm, 0, $pos)) {
            return $memo[$sk] = array($pos, $pos + strlen($cm[0]));
        }
        if (stripos($src, '[[size', $pos) === $pos) {
            $sub = $this->_sizeBlock($src, $pos, $memo);
            if ($sub !== false) {
                $rest = $this->_sizeBody($src, $sub[0], $memo);
                if ($rest !== false) {
                    return $memo[$sk] = $rest;
                }
            }
        }
        $next = strpos($src, '[[', $pos + 1);
        if ($next === false) {
            return $memo[$sk] = false;
        }
        return $memo[$sk] = $this->_sizeBody($src, $next, $memo);
    }
    
}
