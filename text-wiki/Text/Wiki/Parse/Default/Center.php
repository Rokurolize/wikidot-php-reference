<?php

/**
 * 
 * Parses for centered lines of text.
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
 * Parses for centered lines of text.
 * 
 * This class implements a Text_Wiki_Parse to find lines marked for centering.
 * The line must start with "= " (i.e., an equal-sign followed by a space).
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

class Text_Wiki_Parse_Center extends Text_Wiki_Parse {

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
    
    // REFVAL CORRECTION (2026-11-21): live Wikidot matches consecutive
    // `= ` lines (probes muse-probe-refval-center-p10, p11), whereas the
    // fossil `/\n\= (.*?)\n/` consumed the trailing newline and skipped
    // the second consecutive centered line. Use a line-anchored pattern
    // without consuming the bounding newlines, and trim leading/trailing
    // horizontal spaces inside the centered paragraph (p08).
    public $regex = '/^= (.*)$/m';

    /**
     * 
     * Generates a token entry for the matched text.
     * 
     * @access public
     *
     * @param array &$matches The array of matches from parse().
     *
     * @return A delimited token number to be used as a placeholder in
     * the source text.
     *
     */
    
    function parse() {
        if (empty($this->wiki->vars['prefilter_terminal_empty_center'])) {
            parent::parse();
            return;
        }
        $src = $this->wiki->source;
        if (!preg_match_all($this->regex, $src, $ms, PREG_SET_ORDER | PREG_OFFSET_CAPTURE)) {
            return;
        }
        $out = '';
        $last = 0;
        $terminalEnd = strlen($src) - 2;
        foreach ($ms as $m) {
            $off = $m[0][1];
            $out .= substr($src, $last, $off - $last);
            $plain = array($m[0][0], $m[1][0]);
            $end = $off + strlen($m[0][0]);
            if (trim($m[1][0]) === '' && $end === $terminalEnd) {
                $out .= $m[0][0];
            } else {
                $out .= $this->process($plain);
            }
            $last = $end;
        }
        $this->wiki->source = $out . substr($src, $last);
    }

    function process($matches) {
        $start = $this->wiki->addToken($this->rule, array(
            'type' => 'start'));
        
        $end = $this->wiki->addToken($this->rule, array(
            'type' => 'end'));
        
        return "\n\n" . $start . trim($matches[1]) . $end . "\n\n";
    }
}
