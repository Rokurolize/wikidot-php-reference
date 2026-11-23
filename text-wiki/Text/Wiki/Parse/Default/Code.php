<?php

/**
 * 
 * Parses for text marked as a code example block.
 * 
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Paul M. Jones <pmjones@php.net>
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
 * Parses for text marked as a code example block.
 * 
 * This class implements a Text_Wiki_Parse to find sections marked as code
 * examples.  Blocks are marked as the string [[code]] on a line by itself,
 * followed by the inline code example, and terminated with the string
 * [[/code]] on a line by itself.
 *
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Paul M. Jones <pmjones@php.net>
 * 
 * @author Michal Frackowiak
 * 
 */

class Text_Wiki_Parse_Code extends Text_Wiki_Parse {

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
    
    public $regex = ';^\[\[code(\s[^\]]*)?\]\]((?:(?R)|.)*?)\[\[/code\]\](\s|$);msi';

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
        // are there additional attribute arguments?
        $args = trim($matches[1]);
        
        if ($args == '') {
            $options = array('text' => $matches[2], 
                'attr' => array(
                    'type' => ''));
        } else {
            // get the attributes...
            $attr = $this->getAttrs($args);
            
            // ... and make sure we have a 'type'
            if (!isset($attr['type'])) {
                $attr['type'] = '';
            }
            
            // retain the options
            $options = array(
                'text' => $matches[2], 
                'attr' => $attr);
        }
        
        // REFCORR6: the trailing whitespace group is returned outside
        // the token; the claimed span is the rest of the whole match,
        // i.e. the authored [[code ...]] ... [[/code]] form.
        $claimed = substr($matches[0], 0, strlen($matches[0]) - strlen($matches[3]));
        return "\n\n" . $this->wiki->addToken($this->rule, $options, false, $claimed) . $matches[3];
    }

    /**
     * REFCORR16: linear-time scan replacing the whole-document recursive (?R) preg_replace_callback, whose PCRE JIT stack exhaustion silently wiped large documents (measured on real pages in the package 2.1 holdout). The public $regex remains the definitional pattern; the scanner reproduces the pattern's pairing semantics exactly, including PCRE's preference order at each body position (closer first, then a complete nested block, then one character) and its demotion backtrack: a nested block that leaves the enclosing block unclosable is demoted to literal text so the enclosing block can close at the nested block's closer.
     */
    function parse() {
        $this->wiki->source = $this->_scanCode($this->wiki->source);
    }

    private function _scanCode($src) {
        $n = strlen($src);
        $out = '';
        $last = 0;
        $pos = 0;
        $memo = array();
        while ($pos < $n) {
            $cand = stripos($src, '[[code', $pos);
            if ($cand === false) {
                break;
            }
            if ($cand > 0 && $src[$cand - 1] !== "\n") {
                $pos = $cand + 1;
                continue;
            }
            $m = $this->_codeBlock($src, $cand, $memo);
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

    private function _codeBlock($src, $p, &$memo) {
        $bk = 'b' . $p;
        if (array_key_exists($bk, $memo)) {
            return $memo[$bk];
        }
        if (!preg_match('/\G\[\[code(\s[^\]]*)?\]\]/i', $src, $om, 0, $p)) {
            return $memo[$bk] = false;
        }
        $bodyStart = $p + strlen($om[0]);
        if (stripos($src, '[[/code]]', $bodyStart) === false) {
            return $memo[$bk] = false;
        }
        $c = $this->_codeBody($src, $bodyStart, $memo);
        if ($c === false) {
            return $memo[$bk] = false;
        }
        $matches = array(substr($src, $p, $c[1] - $p), isset($om[1]) ? $om[1] : '', substr($src, $bodyStart, $c[0] - $bodyStart), $c[2]);
        return $memo[$bk] = array($c[1], $matches);
    }

    private function _codeBody($src, $pos, &$memo) {
        $sk = 's' . $pos;
        if (array_key_exists($sk, $memo)) {
            return $memo[$sk];
        }
        if (preg_match('/\G\[\[\/code\]\](\s|$)/msi', $src, $cm, 0, $pos)) {
            return $memo[$sk] = array($pos, $pos + strlen($cm[0]), $cm[1]);
        }
        if ($pos === 0 || $src[$pos - 1] === "\n") {
            $sub = $this->_codeBlock($src, $pos, $memo);
            if ($sub !== false) {
                $rest = $this->_codeBody($src, $sub[0], $memo);
                if ($rest !== false) {
                    return $memo[$sk] = $rest;
                }
            }
        }
        $next = strpos($src, '[[', $pos + 1);
        if ($next === false) {
            return $memo[$sk] = false;
        }
        return $memo[$sk] = $this->_codeBody($src, $next, $memo);
    }
}
