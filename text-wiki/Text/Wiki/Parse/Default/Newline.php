<?php

/**
* 
* Parses for implied line breaks indicated by newlines.
* 
* @category Text
* 
* @package Text_Wiki
* 
* @author Paul M. Jones <pmjones@php.net>
* @author Michal Frackowiak
* 
* @license LGPL
* 
* @version $Id$
* 
*/

/**
* 
* Parses for implied line breaks indicated by newlines.
* 
* This class implements a Text_Wiki_Parse to mark implied line breaks in the
* source text, usually a single carriage return in the middle of a paragraph
* or block-quoted text.
*
* @category Text
* 
* @package Text_Wiki
* 
* @author Paul M. Jones <pmjones@php.net>
* @author Michal Frackowiak
* 
*/

class Text_Wiki_Parse_Newline extends Text_Wiki_Parse {

    /**
    * 
    * The regular expression used to parse the source text and find
    * matches conforming to this rule.  Used by the parse() method.
    * 
    * @access public
    * 
    * @var string
    * 
    * @see parse()
    * 
    */
    public $regex = '/([^\n])\n(?!\n)/m';
    
    /**
    * 
    * Generates a replacement token for the matched text.
    * 
    * @access public
    *
    * @param array &$matches The array of matches from parse().
    *
    * @return string A delimited token to be used as a placeholder in
    * the source text.
    *
    */
    
    /**
     * REFCORR16: a line break before an advanced-table block that
     * directly follows a block-level token is layout, not a break:
     * live emits no <br /> at the table-after-table and
     * div-end-to-table junctions of the package 2.1 holdout, while a
     * break before a line table or a div block is served. The block
     * set for the preceding token is the Paragraph rule's skip list.
     * Every other single newline keeps the fossil behavior.
     */
    function parse()
    {
        $src = $this->wiki->source;
        if (!preg_match_all($this->regex, $src, $ms, PREG_SET_ORDER | PREG_OFFSET_CAPTURE)) {
            return;
        }
        $out = '';
        $last = 0;
        foreach ($ms as $m) {
            $off = $m[0][1];
            $out .= substr($src, $last, $off - $last);
            $end = $off + strlen($m[0][0]);
            // REFCORR19 F4(b): a scored-div ([[div_]]) component body is
            // re-inserted into the source stream by the Div parse rule, so
            // the newlines that merely indent its block closers reach this
            // rule and are served as breaks. Live closes those divs with no
            // <br> at all (fragment:scp-7943-1 top-box, firsthand raw HTML).
            // An authored line break between two text lines (foo\nbar) is
            // still served, so only a newline whose next non-whitespace
            // item is a block-closing token is absorbed.
            if ($this->_beforeBlockClose($src, $end)) {
                // Consume the LF as indentation, not as a break: leaving it
                // in the stream makes the later Paragraph rule wrap the
                // following div closer in a spurious <p>.
                $out .= $m[1][0];
            } elseif ($this->_betweenBlocks($src, $off, strlen($m[0][0]))) {
                $out .= $m[0][0];
            } else {
                $out .= $this->process(array($m[0][0], $m[1][0]));
            }
            $last = $off + strlen($m[0][0]);
        }
        $this->wiki->source = $out . substr($src, $last);
    }

    private function _blockSkipList()
    {
        static $skip = null;
        if ($skip === null) {
            $this->wiki->loadParseObj('Paragraph');
            $skip = array();
            if (isset($this->wiki->parseObj['Paragraph'])
                && is_object($this->wiki->parseObj['Paragraph'])) {
                $skip = $this->wiki->parseObj['Paragraph']->getConf('skip', array());
            }
        }
        return $skip;
    }

    private function _tokenRuleAt($src, $pos, $forward)
    {
        $delim = $this->wiki->delim;
        if ($forward) {
            if ($pos >= strlen($src) || $src[$pos] !== $delim) {
                return null;
            }
            $end = strpos($src, $delim, $pos + 1);
            if ($end === false) {
                return null;
            }
            $id = substr($src, $pos + 1, $end - $pos - 1);
        } else {
            if ($pos < 0 || $src[$pos] !== $delim) {
                return null;
            }
            $start = strrpos(substr($src, 0, $pos), $delim);
            if ($start === false) {
                return null;
            }
            $id = substr($src, $start + 1, $pos - $start - 1);
        }
        if (!preg_match('/^\d+$/', $id)) {
            return null;
        }
        $tok = isset($this->wiki->tokens[(int)$id]) ? $this->wiki->tokens[(int)$id] : null;
        return $tok === null ? null : strtolower($tok[0]);
    }

    /**
     * REFCORR19 F4(b): return the full token whose delimiter begins at or
     * after $pos (skipping only horizontal whitespace), or null. Unlike
     * _tokenRuleAt() this does not require the character immediately before
     * the newline to be a delimiter: in a scored-div body the preceding
     * character is authored text ("7943"), which is exactly the leaking
     * shape.
     */
    private function _nextBlockToken($src, $pos)
    {
        $delim = $this->wiki->delim;
        $n = strlen($src);
        while ($pos < $n && ($src[$pos] === ' ' || $src[$pos] === "\t" || $src[$pos] === "\r")) {
            $pos++;
        }
        if ($pos >= $n || $src[$pos] !== $delim) {
            return null;
        }
        $end = strpos($src, $delim, $pos + 1);
        if ($end === false) {
            return null;
        }
        $id = substr($src, $pos + 1, $end - $pos - 1);
        if (!preg_match('/^\d+$/', $id)) {
            return null;
        }
        return isset($this->wiki->tokens[(int)$id]) ? $this->wiki->tokens[(int)$id] : null;
    }

    /**
     * REFCORR19 F4(b): true when the newline is immediately followed (after
     * indentation only) by a div closer. Live emits no break before a div
     * close in a scored-div component body; an authored break between two
     * text runs is not followed by a token and is left served.
     */
    private function _beforeBlockClose($src, $pos)
    {
        $tok = $this->_nextBlockToken($src, $pos);
        if ($tok === null || strtolower($tok[0]) !== 'div') {
            return false;
        }
        $opts = isset($tok[1]) && is_array($tok[1]) ? $tok[1] : array();
        return isset($opts['type']) && $opts['type'] === 'end';
    }

    private function _betweenBlocks($src, $off, $len)
    {
        $delim = $this->wiki->delim;
        if ($off < 1 || $src[$off] !== $delim) {
            return false;
        }
        // The measured suppression is specific to a following advanced
        // table: a break before a [[table]] block is absorbed, while a
        // break before a line table or a div block is served as <br />
        // (S_local 2014-survey-results; diag d32; holdout h094). The
        // preceding side is any block-level token (div end in h078,
        // table end in h045).
        $next = $this->_tokenRuleAt($src, $off + $len, true);
        if ($next !== 'tableadv') {
            return false;
        }
        $skip = $this->_blockSkipList();
        $prev = $this->_tokenRuleAt($src, $off, false);
        return $prev !== null && in_array($prev, $skip, true);
    }

    function process($matches)
    {    
        // REFCORR6: the token claims only the LF; $matches[1] is the
        // preceding character and is returned outside the token.
        return $matches[1] .
            $this->wiki->addToken($this->rule, array(), false, "\n")
           ;// . $matches[2];
    }
}
