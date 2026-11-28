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
        // REFCORR32: horizontal whitespace at the inline scope edge is not
        // content of the size span. Live hoists a leading space before the
        // element and ejects a trailing space after it; JP corpus witnesses
        // in not-fade-away show both shapes with following text. Internal
        // line-end spaces still use the settled strip below. Keep these
        // bytes outside the token pair so the final Tighten pass can drop
        // them when the scope sits at a paragraph edge.
        $leadSpace = '';
        $trailSpace = '';
        if (preg_match('/\A[ \t]+/', $content, $edgeMatch)) {
            $leadSpace = $edgeMatch[0];
            $content = substr($content, strlen($leadSpace));
        }
        if (preg_match('/[ \t]+\z/', $content, $edgeMatch)) {
            $trailSpace = $edgeMatch[0];
            $content = substr($content, 0, -strlen($trailSpace));
        }
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
        if($content === '' || $this->_onlyEmptySizeAtoms($content)){
            // REFCORR29: live does not serve the empty element, but the
            // whitespace-only construct is still an inline atom while the
            // Newline and Paragraph rules run. JP corpus pages use such
            // size-only lines as vertical spacing; deleting the construct
            // here collapses adjacent source newlines and loses live's
            // <br /> / empty-paragraph framing. Claim it with a token whose
            // renderer emits nothing instead.
            return $this->wiki->addToken($this->rule, array('type' => 'empty'));
        }

        $split = null;
        $seenVisible = false;
        $emptyRawAfterVisible = false;
        $visibleAfterEmptyRaw = false;
        $blankRunStart = null;
        $lastVisibleLineEnd = null;
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
            if ((preg_match($emptyRawLine, $line, $rawMatch)
                && isset($this->wiki->tokens[(int)$rawMatch[1]])
                && $this->wiki->tokens[(int)$rawMatch[1]][0] === 'Raw'
                && $this->wiki->tokens[(int)$rawMatch[1]][1]['text'] === '')
                || $line === "\xEF\xBF\xBE\xEF\xBF\xBF") {
                $isEmptyRaw = true;
            }
            if ($seenVisible && $isEmptyRaw) {
                $nextStart = $lineEnd + 1;
                $nextLine = '';
                while ($nextStart < $contentLen) {
                    $nextEnd = strpos($content, "\n", $nextStart);
                    if ($nextEnd === false) {
                        $nextEnd = $contentLen;
                    }
                    $nextLine = substr($content, $nextStart, $nextEnd - $nextStart);
                    if (trim($nextLine) !== '') {
                        break;
                    }
                    $nextStart = $nextEnd + 1;
                }
                $blockAfter = $nextLine !== '' && substr($nextLine, 0, 2) === '= ';
                if (!$blockAfter && preg_match('/\A' . preg_quote($this->wiki->delim, '/')
                    . '(\d+)' . preg_quote($this->wiki->delim, '/') . '/', $nextLine, $blockMatch)) {
                    $blockToken = isset($this->wiki->tokens[(int)$blockMatch[1]])
                        ? $this->wiki->tokens[(int)$blockMatch[1]] : null;
                    $blockAfter = $blockToken !== null && ($blockToken[0] === 'Horiz'
                        || ($blockToken[0] === 'Blockquote' && isset($blockToken[1]['type'])
                            && $blockToken[1]['type'] === 'start'));
                }
                if (!$blockAfter && preg_match('/\A\[\[(?:f)?[<>=]image\s+/i', $nextLine)) {
                    $blockAfter = true;
                }
                if ($blockAfter) {
                    $split = $lineStart;
                    break;
                }
                $emptyRawAfterVisible = true;
            }
            if (!$isEmptyRaw && $emptyRawAfterVisible) {
                if (trim($line) === '' && $visibleAfterEmptyRaw && $lastVisibleLineEnd !== null) {
                    $split = $lastVisibleLineEnd;
                    break;
                }
                $lineIsBlock = substr($line, 0, 2) === '= ';
                if (!$lineIsBlock && preg_match('/\A' . preg_quote($this->wiki->delim, '/')
                    . '(\d+)' . preg_quote($this->wiki->delim, '/') . '/', $line, $lineBlockMatch)) {
                    $lineBlockToken = isset($this->wiki->tokens[(int)$lineBlockMatch[1]])
                        ? $this->wiki->tokens[(int)$lineBlockMatch[1]] : null;
                    $lineIsBlock = $lineBlockToken !== null && ($lineBlockToken[0] === 'Horiz'
                        || ($lineBlockToken[0] === 'Blockquote' && isset($lineBlockToken[1]['type'])
                            && $lineBlockToken[1]['type'] === 'start'));
                }
                if (!$lineIsBlock && preg_match('/\A\[\[(?:f)?[<>=]image\s+/i', $line)) {
                    $lineIsBlock = true;
                }
                if ($lineIsBlock) {
                    $split = $lastVisibleLineEnd !== null ? $lastVisibleLineEnd : $lineStart;
                    break;
                }
            }
            if (!$isEmptyRaw && trim($line) !== '') {
                if ($emptyRawAfterVisible) {
                    $visibleAfterEmptyRaw = true;
                }
                $seenVisible = true;
                $blankRunStart = null;
                $lastVisibleLineEnd = $lineEnd;
            } elseif (!$isEmptyRaw && $blankRunStart === null) {
                $blankRunStart = $lineStart;
            }
            $lineStart = $lineEnd + 1;
        }

        $options = array('size'=>$size, 'type'=>'start');
        if ($leadSpace !== '') {
            $options['edge_lead'] = $leadSpace;
        }
      	
        $start = $this->wiki->addToken($this->rule, $options);

        $endOptions = array('type' => 'end');
        if ($trailSpace !== '') {
            $endOptions['edge_trail'] = $trailSpace;
        }
        $end = $this->wiki->addToken(
            $this->rule, $endOptions
        );
        
        if ($split !== null) {
            return $start . substr($content, 0, $split) . $end
                . substr($content, $split)
                . $this->wiki->addToken($this->rule, array('type' => 'empty'));
        }
        return $leadSpace . $start . $content . $end . $trailSpace;

    }

    /**
     * Whether a nested Size body consists only of horizontal whitespace and
     * empty-size placeholder atoms already produced by this rule. Such a
     * body is itself invisible, but must retain one atom for line framing;
     * without this recursion the nested empty-pair suppression settled in
     * R2-contain would regress to an empty outer span.
     */
    private function _onlyEmptySizeAtoms($content) {
        $rest = preg_replace_callback(
            '/' . preg_quote($this->wiki->delim, '/') . '([0-9]+)'
                . preg_quote($this->wiki->delim, '/') . '/',
            function ($m) {
                $token = isset($this->wiki->tokens[(int)$m[1]])
                    ? $this->wiki->tokens[(int)$m[1]] : null;
                return ($token !== null && $token[0] === 'Size'
                    && isset($token[1]['type']) && $token[1]['type'] === 'empty')
                    ? '' : $m[0];
            }, $content);
        return $rest !== $content && preg_match('/^[ \t]*$/', $rest) === 1;
    }
    
    function parse(){
        do {
            $oldSource = $this->wiki->source;
            $this->wiki->source = $this->_scanSize($oldSource);
        } while ($oldSource != $this->wiki->source);
        $this->wiki->source = str_replace("\xEF\xBF\xBE\xEF\xBF\xBF", ' ', $this->wiki->source);
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
