<?php

/**
 * 
 * Parses for paragraph blocks.
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
 * Parses for paragraph blocks.
 * 
 * This class implements a Text_Wiki rule to find sections of the source
 * text that are paragraphs.  A para is any line not starting with a token
 * delimiter, followed by two newlines.
 *
 * Live Wikidot's scored alias openers (`[[span_]]` and its `[[a_]]` sibling)
 * are owned at the paragraph layer: ftml's `parsing/paragraph` module joins
 * the line-break runs on both sides of a paired scored opener and removes the
 * paragraph wrapper when the joined run is only that span (see its
 * `wikidot_scored_alias_open_joins_previous_line`,
 * `wikidot_scored_close_joins_late_line` and
 * `wikidot_current_ends_with_scored_alias` helpers), and live probe
 * muse-probe-r2contain-span-p20 plus this stage's p08/p11/p17 settle the same
 * shape. The fossil had no handling for the scored form at all. The paragraph
 * rule now builds the Span token pair by reusing the existing Span rule's
 * `process()` (so the attribute grammar is not duplicated here), removes the
 * adjacent break runs, and suppresses its wrapper for a run that is only a
 * scored span. The whitespace-run collapse inside text is deliberately NOT
 * done here: live collapses a tab to one space even inside a scored span with
 * no `<p>` wrapper (probe p02), so that surface belongs to Stage 2
 * purifyHtml, not to paragraph formation.
 *
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Paul M. Jones <pmjones@php.net>
 * @author Michal Frackowiak
 * 
 */

class Text_Wiki_Parse_Paragraph extends Text_Wiki_Parse {
     
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
     
    public $regex = "/^.*?\n\s*?\n/m";
    
    public $conf = array(
        'skip' => array('blockquote', // are we sure about this one?
 'code', 'clearfloat', 
            'heading', 'horiz', 'separator', 'deflist', 'table', 
            'tableadv', 'list', 'toc', 'center', 
            'tabview', 'div', 'divalign', 'divalignleft', 
            'divalignright', 'divaligncenter', 
            'divalignjustify', 'collapsible', 'note', 
            'math', 'module', 'module654', 
            'footnoteblock', 'footnoteitem', 
            'bibliography', 'bibitem', 'gallery', 
            'image')//,
 //'embed'
        

        , 'clear' => array('div'));

    /**
     * Replacement strings of scored-span token pairs, keyed by the id of
     * their start token. Populated at parse time and read by process() so a
     * run consisting only of a scored span keeps its bare-element shape.
     */
    protected $scoredSpans = array();

    /**
     * Prepare scored spans, then apply the ordinary paragraph regex. The
     * scored form must be handled before the regex runs because its line
     * joins change which source runs exist at all.
     */
    function parse() {
        $this->tokenizeScoredSpans();
        parent::parse();
    }

    /**
     * Replace paired scored span openers with Span tokens and remove the
     * line-break runs adjacent to them. Horizontal spaces on the same line
     * are kept, so `lead [[span_]]X[[/span]] tail` stays one paragraph with
     * its surrounding spaces. An unpaired opener is left literal, exactly as
     * ftml leaves it. The existing Span rule constructs the tokens, so this
     * rule owns only the paragraph-side behavior.
     */
    protected function tokenizeScoredSpans() {
        $delim = preg_quote($this->wiki->delim, '/');
        $unit = '(?:[ \t\r\n]|' . $delim . '[0-9]+' . $delim . ')';
        $pattern = '/(' . $unit . '*)\[\[span_([^\]]*)\]\](.*?)\[\[\/span\]\]('
            . $unit . '*)/is';
        $this->wiki->source = preg_replace_callback(
            $pattern, array(&$this, 'replaceScoredSpan'), $this->wiki->source);
    }

    /**
     * Whether an adjacent run contains a line boundary, literal or already
     * tokenized by the Newline rule (which runs just before Paragraph).
     */
    protected function runHasBreak($run) {
        if (strpos($run, "\n") !== false || strpos($run, "\r") !== false) {
            return true;
        }
        $delim = $this->wiki->delim;
        if (preg_match_all('/' . preg_quote($delim, '/')
            . '([0-9]+)' . preg_quote($delim, '/') . '/', $run, $ms)) {
            foreach ($ms[1] as $id) {
                if (isset($this->wiki->tokens[$id])
                    && $this->wiki->tokens[$id][0] === 'Newline') {
                    return true;
                }
            }
        }
        return false;
    }

    /**
     * Keep the non-break tokens of an adjacent run. A run that also holds a
     * block or inline token (for example a `[[div]]` opener immediately
     * above a scored span) must keep that token: only the whitespace and the
     * Newline rule's break tokens are dropped.
     */
    protected function filterBreakRun($run) {
        $delim = preg_quote($this->wiki->delim, '/');
        if (! preg_match_all('/(' . $delim . '([0-9]+)' . $delim . ')/',
            $run, $ms, PREG_SET_ORDER)) {
            return '';
        }
        $kept = '';
        foreach ($ms as $m) {
            $type = isset($this->wiki->tokens[$m[2]])
                ? $this->wiki->tokens[$m[2]][0] : '';
            if ($type !== 'Newline') {
                $kept .= $m[1];
            }
        }
        return $kept;
    }

    /**
     * Callback for tokenizeScoredSpans(): the break-bearing lead/trail runs
     * are reduced to their non-break tokens and the Span token pair is
     * inserted in their place.
     */
    protected function replaceScoredSpan($matches) {
        if (! isset($this->wiki->parseObj['Span'])
            || ! is_object($this->wiki->parseObj['Span'])) {
            return $matches[0];
        }
        $lead = $this->runHasBreak($matches[1])
            ? $this->filterBreakRun($matches[1]) : $matches[1];
        $trail = $this->runHasBreak($matches[4])
            ? $this->filterBreakRun($matches[4]) : $matches[4];
        // Span::process expects the attribute capture with its leading
        // whitespace; the scored underscore is not part of that grammar.
        $pair = $this->wiki->parseObj['Span']->process(
            array('', ' ' . $matches[2], $matches[3]));
        $delim = preg_quote($this->wiki->delim, '/');
        if (preg_match('/^' . $delim . '([0-9]+)' . $delim . '/', $pair, $id)) {
            $this->scoredSpans[$id[1]] = $pair;
        }
        return $lead . $pair . $trail;
    }
     
    /**
     * 
     * Generates a token entry for the matched text.  Token options are:
     * 
     * 'start' => The starting point of the paragraph.
     * 
     * 'end' => The ending point of the paragraph.
     * 
     * @access public
     *
     * @param array &$matches The array of matches from parse().
     *
     * @return A delimited token number to be used as a placeholder in
     * the source text.
     *
     */
     
    /**
     * R11-CONCAT: whether a paragraph run holds a div opener token.
     * Combined with the recorded continued-div lead, this identifies the
     * one run whose preceding text must stay bare on live.
     */
    protected function runHasBlockStart($run) {
        $delim = preg_quote($this->wiki->delim, '/');
        if (! preg_match_all('/' . $delim . '([0-9]+)' . $delim . '/', $run, $ms)) {
            return false;
        }
        foreach ($ms[1] as $id) {
            $tok = isset($this->wiki->tokens[$id]) ? $this->wiki->tokens[$id] : null;
            if ($tok !== null && $tok[0] === 'Div') {
                return true;
            }
        }
        return false;
    }

    function process($matches) {
        $delim = $this->wiki->delim;

        // R11-CONCAT: a continued block boundary keeps the leading text bare
        // (no <p> wrapper). Narrowed to a run that both holds a div opener
        // and whose plain text was recorded by Concatlines, so authored
        // same-line openers keep their pinned paragraph wrapper.
        $leads = isset($this->wiki->vars['continued_div_leads'])
            ? $this->wiki->vars['continued_div_leads'] : array();
        if (! empty($leads) && $this->runHasBlockStart($matches[0])) {
            $pp = '/' . preg_quote($delim, '/') . '[0-9]+' . preg_quote($delim, '/') . '/';
            $plain = trim(preg_replace($pp, '', $matches[0]), " \t\n\r");
            if (in_array($plain, $leads, true)) {
                return $matches[0];
            }
        }

        // was anything there?
        if (trim($matches[0]) == '') {
            return '';
        }

        // Scored anchor ([[a_ ...]]...[[/a]]) paragraph-wrapper suppression (PG-F1):
        // when a run ends with a scored anchor closing token (either standalone
        // [[a_]]X[[/a]] or a line ending with a scored anchor), keep it bare.
        if (!empty($this->wiki->vars['scored_anchors']) && is_array($this->wiki->vars['scored_anchors'])) {
            $trimmedRun = trim($matches[0]);
            foreach ($this->wiki->vars['scored_anchors'] as $endTok => $startTok) {
                $endLen = strlen($endTok);
                if ($endLen > 0 && substr($trimmedRun, -$endLen) === $endTok && strpos($trimmedRun, $startTok) !== false) {
                    return $matches[0];
                }
            }
        }
        
        // does the match start with a delimiter?
        if (substr($matches[0], 0, 1) != $delim) {
            // no.
             

            $start = $this->wiki->addToken($this->rule, array(
                'type' => 'start'));
            
            $end = $this->wiki->addToken($this->rule, array(
                'type' => 'end'));
            
            return $start . trim($matches[0]) . $end . "\n\n";
        }
        
        // the line starts with a delimiter.  read in the delimited
        // token number, check the token, and see if we should
        // skip it.
        

        // loop starting at the second character (we already know
        // the first is a delimiter) until we find another
        // delimiter; the text between them is a token key number.
        $key = '';
        $len = strlen($matches[0]);
        for ($i = 1; $i < $len; $i++) {
            $char = $matches[0][$i];
            if ($char == $delim) {
                break;
            } else {
                $key .= $char;
            }
        }
        
        // A run that is exactly one scored span keeps the bare <span> that
        // live emits: the scored opener owns the root paragraph. A plain
        // span still gets its wrapper, so only the recorded scored pair is
        // excepted here.
        if (isset($this->scoredSpans[$key])
            && trim($matches[0]) === trim($this->scoredSpans[$key])) {
            return $matches[0];
        }

        // look at the token and see if it's skippable (if we skip,
        // it will not be marked as a paragraph)
        $token_type = strtolower($this->wiki->tokens[$key][0]);
        $skip = $this->getConf('skip', array());
        
        if (in_array($token_type, $skip)) {
            // this type of token should not have paragraphs applied to it.
            // return the entire matched text.
            return $matches[0];
        } else {
            
            $start = $this->wiki->addToken($this->rule, array(
                'type' => 'start'));
            
            $end = $this->wiki->addToken($this->rule, array(
                'type' => 'end'));
            
            return $start . trim($matches[0]) . $end . "\n\n";
        }
    }
}
