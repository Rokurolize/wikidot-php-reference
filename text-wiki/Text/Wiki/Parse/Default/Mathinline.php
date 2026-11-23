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
* Parses for text marked as inline math.
* 
* This class implements a Text_Wiki_Parse to find math invocation code, 
* i.e. [[$ equation $]]
*
* @category Text
* 
* @package Text_Wiki
* 
* @author Michal Frackowiak
* 
*/

class Text_Wiki_Parse_Mathinline extends Text_Wiki_Parse {

    /**
    * REFCORR6 C-SUSPECT3-1: the four rules the M1 battery proves make
    * live suppress the whole formula wherever they occur in the body,
    * including inside a described email's or URL's claimed source.
    */
    // REFCORR8 C-R5-P2-4: a Date token suppresses the whole formula on
    // live (`[[$x [[date 0]] y$]]` -> `<span class="math-inline">$$</span>`),
    // just like the REFCORR6 four. The check in expandSource is recursive,
    // so a Date at any depth suppresses; the four-rule set is otherwise
    // unchanged, as is the recursive source-span expansion itself.
    public static $suppressRules = array('Freelink', 'Raw', 'Newline', 'Image', 'Date');

    /**
    * REFCORR6: the one-level option-value replacement retained as a
    * fallback for a token whose addToken call did not carry a source
    * span. It is the pre-correction behavior and keeps every rule the
    * battery does not exercise byte-identical.
    */
    function optionReplacement($token)
    {
        $options = isset($token[1]) && is_array($token[1]) ? $token[1] : array();
        if (isset($options['text']) && is_string($options['text'])) {
            return $options['text'];
        }
        if (isset($options['href']) && is_string($options['href'])) {
            return $options['href'];
        }
        return '';
    }

    /**
    * REFCORR6: expand every placeholder in $bytes back to its token's
    * original authored source text, recursively. Returns
    * array($suppressed, $expandedBytes); a suppressed result means the
    * whole formula is to be rendered as "$$". $seen bounds recursion on
    * a cyclic placeholder chain, and $depth bounds accidental deep
    * nesting; unknown tokens stay as literal placeholder bytes.
    */
    function expandSource($bytes, $seen, $depth)
    {
        if ($depth > 64 || strpos($bytes, $this->wiki->delim) === false
            || !preg_match_all('/\xFF(\d+)\xFF/', $bytes, $ph, PREG_OFFSET_CAPTURE)) {
            return array(false, $bytes);
        }
        $out = '';
        $pos = 0;
        foreach ($ph[0] as $i => $hit) {
            $whole = $hit[0];
            $start = $hit[1];
            if ($start > $pos) {
                $out .= substr($bytes, $pos, $start - $pos);
            }
            $tid = $ph[1][$i][0];
            $token = isset($this->wiki->tokens[$tid]) ? $this->wiki->tokens[$tid] : null;
            $name = ($token !== null && isset($token[0])) ? $token[0] : '';
            if (in_array($name, self::$suppressRules, true)) {
                return array(true, '');
            }
            if ($token === null || isset($seen[$tid])) {
                $out .= $whole;
            } elseif (isset($this->wiki->tokenSource[$tid])) {
                $next = $seen;
                $next[$tid] = true;
                list($suppressed, $replacement) = $this->expandSource(
                    $this->wiki->tokenSource[$tid], $next, $depth + 1);
                if ($suppressed) {
                    return array(true, '');
                }
                $out .= $replacement;
            } else {
                $out .= $this->optionReplacement($token);
            }
            $pos = $start + strlen($whole);
        }
        $out .= substr($bytes, $pos);
        return array(false, $out);
    }

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

     public $regex = '/\[\[\$(.*?)\$\]\]/';
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
    	$content = trim($matches[1]);

        // Earlier rules have already replaced their own spans with
        // \xFF<token-id>\xFF placeholders by the time this late rule runs.
        // REFCORR6 C-SUSPECT3-1: live preserves the trimmed authored body
        // and expands each placeholder back to that token's original
        // source text, recursively, suppressing the whole formula to
        // "$$" for a Freelink, Raw, Newline or Image token at any depth.
        // Comments are elided by their own rule and leave no placeholder,
        // so they do not suppress.
        list($suppressed, $content) = $this->expandSource($content, array(), 0);
        if ($suppressed) {
            $content = '';
        }

        $options = array('content'=>$content);

        // REFCORR6: the whole [[$ ... $]] match is this token's source.
        return $this->wiki->addToken($this->rule, $options, false, $matches[0]);
    }
}
