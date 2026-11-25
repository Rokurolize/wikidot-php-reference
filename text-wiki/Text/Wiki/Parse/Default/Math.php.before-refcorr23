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

    /**
     * REFCORR16: linear-time scan replacing the whole-document recursive
     * (?R) preg_replace_callback, whose PCRE JIT stack exhaustion
     * silently wiped large documents (demonstrable for this rule on an
     * unclosed opener with a long tail; the class was measured on real
     * pages for Divalign, Tableadv and Code in the package 2.1 holdout).
     * The public $regex remains the definitional pattern; the scanner
     * reproduces its pairing semantics, including PCRE's preference
     * order at each body position (closer first, then a complete nested
     * block, then one character), its demotion backtrack (a nested
     * block that leaves the enclosing block unclosable is demoted to
     * literal text), and the (?R) negative guard: a nested block
     * immediately followed by optional whitespace and a [[/math]]
     * closer is not consumed as a unit, and progressively longer nested
     * matches that swallow an earlier closer as body text are tried in
     * the pattern's own order before the opener is demoted.
     */
    function parse() {
        $this->wiki->source = $this->_scanMath($this->wiki->source);
    }

    private function _scanMath($src) {
        $n = strlen($src);
        $out = '';
        $last = 0;
        $pos = 0;
        $memo = array();
        while ($pos < $n) {
            $cand = stripos($src, '[[math', $pos);
            if ($cand === false) {
                break;
            }
            if ($cand > 0 && $src[$cand - 1] !== "\n") {
                $pos = $cand + 1;
                continue;
            }
            $m = $this->_mathBlockSkip($src, $cand, 0, $memo);
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

    private function _mathBlockSkip($src, $p, $skip, &$memo) {
        $bk = 'b' . $p . '|' . $skip;
        if (array_key_exists($bk, $memo)) {
            return $memo[$bk];
        }
        if (!preg_match('/\G\[\[math(\s+[a-z0-9_]*?)?((?:\s+[a-z0-9]+="[^"]*"))*\s*\]\]/i', $src, $om, 0, $p)) {
            return $memo[$bk] = false;
        }
        $bodyStart = $p + strlen($om[0]);
        if (stripos($src, '[[/math]]', $bodyStart) === false) {
            return $memo[$bk] = false;
        }
        $c = $this->_mathBody($src, $bodyStart, $skip, $memo);
        if ($c === false) {
            return $memo[$bk] = false;
        }
        $matches = array(
            substr($src, $p, $c[1] - $p),
            isset($om[1]) ? $om[1] : '',
            isset($om[2]) ? $om[2] : '',
            substr($src, $bodyStart, $c[0] - $bodyStart),
            $c[2]);
        return $memo[$bk] = array($c[1], $matches);
    }

    private function _mathBody($src, $pos, $skip, &$memo) {
        $sk = 's' . $pos . '|' . $skip;
        if (array_key_exists($sk, $memo)) {
            return $memo[$sk];
        }
        if (preg_match('/\G\n\[\[\/math\]\](\s|$)/msi', $src, $cm, 0, $pos)) {
            if ($skip > 0) {
                // The closer is consumed as body text, character by
                // character as the pattern's '.' atom would: its
                // trailing (\s|$) group is not part of the closer text,
                // so a following closer keeps its leading newline.
                return $memo[$sk] = $this->_mathBody(
                    $src, $pos + strlen($cm[0]) - strlen($cm[1]),
                    $skip - 1, $memo);
            }
            return $memo[$sk] = array($pos, $pos + strlen($cm[0]), $cm[1]);
        }
        if ($pos > 0 && $src[$pos - 1] === "\n"
            && stripos($src, '[[math', $pos) === $pos) {
            for ($k = 0; ; $k++) {
                $cand = $this->_mathBlockSkip($src, $pos, $k, $memo);
                if ($cand === false) {
                    break;
                }
                if (preg_match('/\G\s*\[\[\/math\]\]/', $src, $gm, 0, $cand[0])) {
                    continue;
                }
                $rest = $this->_mathBody($src, $cand[0], $skip, $memo);
                if ($rest !== false) {
                    return $memo[$sk] = $rest;
                }
            }
        }
        $nextOpen = strpos($src, '[[', $pos + 1);
        $nextClose = stripos($src, "\n[[/math]]", $pos + 1);
        if ($nextOpen === false && $nextClose === false) {
            return $memo[$sk] = false;
        }
        if ($nextOpen === false) {
            $next = $nextClose;
        } elseif ($nextClose === false) {
            $next = $nextOpen;
        } else {
            $next = min($nextOpen, $nextClose);
        }
        return $memo[$sk] = $this->_mathBody($src, $next, $skip, $memo);
    }
}

