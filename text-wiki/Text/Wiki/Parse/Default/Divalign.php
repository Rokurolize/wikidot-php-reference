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
 * Parses alignmnent blocks.
 *
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Michal Frackowiak
 * 
 */

class Text_Wiki_Parse_Divalign extends Text_Wiki_Parse {
    
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
    
    public $regex = '/^\[\[(=|<|>|==)\]\]\n((?:(?R)|.)*?)\[\[\/\\1\]\]$/msi';

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
    
    function process($matches) {
        $align = $matches[1];
        $content = $matches[2];
        
        $options = array('type' => 'start');
        
        $aligns = array('=' => 'center', '<' => 'left', 
            '>' => 'right', '==' => 'justify');
        
        $align = $aligns[$align];
        
        if (!$align) {
            return;
        }
        
        $options['align'] = $align;
        
        $start = $this->wiki->addToken($this->rule, $options);
        
        $end = $this->wiki->addToken($this->rule, array(
            'type' => 'end'));
        
        return $start . "\n\n" . $content . "\n\n" . $end;
    
    }

    function parse() {
        do {
            $oldSource = $this->wiki->source;
            $this->wiki->source = $this->_scanDivalign($oldSource);
        } while ($oldSource != $this->wiki->source);
    }

    /**
     * REFCORR16: linear-time scan replacing the whole-document recursive (?R) preg_replace_callback, whose PCRE JIT stack exhaustion silently wiped large documents (measured on real pages in the package 2.1 holdout). The public $regex remains the definitional pattern; the scanner reproduces the pattern's pairing semantics exactly, including PCRE's preference order at each body position (closer first, then a complete nested block, then one character) and its demotion backtrack: a nested block that leaves the enclosing block unclosable is demoted to literal text so the enclosing block can close at the nested block's closer.
     */
    private function _scanDivalign($src) {
        $n = strlen($src);
        $out = '';
        $last = 0;
        $pos = 0;
        $memo = array();
        while ($pos < $n) {
            $cand = stripos($src, '[[', $pos);
            if ($cand === false) {
                break;
            }
            if ($cand > 0 && $src[$cand - 1] !== "\n") {
                $pos = $cand + 1;
                continue;
            }
            $m = $this->_divalignBlock($src, $cand, $memo);
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

    private function _divalignBlock($src, $p, &$memo) {
        $bk = 'b' . $p;
        if (array_key_exists($bk, $memo)) {
            return $memo[$bk];
        }
        if (!preg_match('/\G\[\[(=|<|>|==)\]\]\n/', $src, $om, 0, $p)) {
            return $memo[$bk] = false;
        }
        $marker = $om[1];
        $bodyStart = $p + strlen($om[0]);
        if (strpos($src, '[[/' . $marker . ']]', $bodyStart) === false) {
            return $memo[$bk] = false;
        }
        $c = $this->_divalignBody($src, $bodyStart, $marker, $memo);
        if ($c === false) {
            return $memo[$bk] = false;
        }
        $matches = array(
            substr($src, $p, $c[1] - $p),
            $marker,
            substr($src, $bodyStart, $c[0] - $bodyStart));
        return $memo[$bk] = array($c[1], $matches);
    }

    private function _divalignBody($src, $pos, $marker, &$memo) {
        $sk = 's' . $pos . '|' . $marker;
        if (array_key_exists($sk, $memo)) {
            return $memo[$sk];
        }
        $closer = '[[/' . $marker . ']]';
        $clen = strlen($closer);
        if ($pos + $clen <= strlen($src)
            && substr_compare($src, $closer, $pos, $clen) === 0) {
            $after = $pos + $clen;
            if ($after === strlen($src) || $src[$after] === "\n") {
                return $memo[$sk] = array($pos, $after);
            }
        }
        if ($pos === 0 || $src[$pos - 1] === "\n") {
            $sub = $this->_divalignBlock($src, $pos, $memo);
            if ($sub !== false) {
                $rest = $this->_divalignBody($src, $sub[0], $marker, $memo);
                if ($rest !== false) {
                    return $memo[$sk] = $rest;
                }
            }
        }
        $next = strpos($src, '[[', $pos + 1);
        if ($next === false) {
            return $memo[$sk] = false;
        }
        return $memo[$sk] = $this->_divalignBody($src, $next, $marker, $memo);
    }

}
