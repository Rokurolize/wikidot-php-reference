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
        // A blank-line run immediately inside a Span or Size opener is
        // inline content before it is paragraph layout. Live serves those
        // line breaks in the leading empty fragment that Stage 2 repair
        // leaves before a following block boundary; treating the run as a
        // paragraph separator here loses the fragment.
        $newlineRun = '/\n{2,}/';
        $leadOut = '';
        $cursor = 0;
        $search = 0;
        while (preg_match($newlineRun, $src, $m, PREG_OFFSET_CAPTURE, $search)) {
            $fullPos = $m[0][1];
            $fullLen = strlen($m[0][0]);
            $leadOut .= substr($src, $cursor, $fullPos - $cursor);
            $replacement = $m[0][0];
            $prefix = substr($src, 0, $fullPos);
            $placeholder = '/' . preg_quote($this->wiki->delim, '/') . '(\d+)'
                . preg_quote($this->wiki->delim, '/') . '/';
            $inlineDepth = 0;
            $inlineStack = array();
            $allPrefixMatches = array();
            $horizPrefixIndexes = array();
            if (preg_match_all($placeholder, $prefix, $pm, PREG_OFFSET_CAPTURE)) {
                $allPrefixMatches = $pm;
                foreach ($pm[1] as $pi => $tidm) {
                    $tid = $tidm[0];
                    $tok = isset($this->wiki->tokens[(int)$tid])
                        ? $this->wiki->tokens[(int)$tid] : null;
                    if ($tok !== null && $tok[0] === 'Horiz') {
                        $horizPrefixIndexes[] = $pi;
                    }
                    if ($tok === null || !in_array($tok[0], array('Span', 'Size', 'Anchor'), true)
                        || !isset($tok[1]['type'])) {
                        continue;
                    }
                    if ($tok[1]['type'] === 'start') {
                        $inlineDepth++;
                        $inlineStack[] = $pi;
                    } elseif ($tok[1]['type'] === 'end' && $inlineDepth > 0) {
                        $inlineDepth--;
                        array_pop($inlineStack);
                    }
                }
            }
            $scopeAfterBlockEnd = false;
            $scopePrevBlockRule = null;
            if (!empty($inlineStack)) {
                $scopePi = end($inlineStack);
                if ($scopePi > 0) {
                    $scopeStartPos = $allPrefixMatches[0][$scopePi][1];
                    $prevEndPos = $allPrefixMatches[0][$scopePi - 1][1]
                        + strlen($allPrefixMatches[0][$scopePi - 1][0]);
                    $scopeBetween = substr($prefix, $prevEndPos, $scopeStartPos - $prevEndPos);
                    $scopePrevTok = isset($this->wiki->tokens[(int)$allPrefixMatches[1][$scopePi - 1][0]])
                        ? $this->wiki->tokens[(int)$allPrefixMatches[1][$scopePi - 1][0]] : null;
                    $scopeAfterBlockEnd = $scopePrevTok !== null
                        && preg_match('/\A\n[ \t]*\z/', $scopeBetween) === 1
                        && isset($scopePrevTok[1]['type']) && $scopePrevTok[1]['type'] === 'end'
                        && in_array($scopePrevTok[0], array('Div', 'Divalign', 'Center', 'Horiz', 'Table', 'Tableadv'), true);
                    if ($scopeAfterBlockEnd) {
                        $scopePrevBlockRule = $scopePrevTok[0];
                    }
                }
            }
            $directInlineLead = false;
            if (preg_match($placeholder, $prefix, $endm, PREG_OFFSET_CAPTURE) && preg_match_all($placeholder, $prefix, $allEnds, PREG_OFFSET_CAPTURE)) {
                $lastIndex = count($allEnds[0]) - 1;
                if ($allEnds[0][$lastIndex][1] + strlen($allEnds[0][$lastIndex][0]) === $fullPos) {
                    $edgeTok = isset($this->wiki->tokens[(int)$allEnds[1][$lastIndex][0]])
                        ? $this->wiki->tokens[(int)$allEnds[1][$lastIndex][0]] : null;
                    $directInlineLead = $edgeTok !== null
                        && in_array($edgeTok[0], array('Span', 'Size'), true)
                        && isset($edgeTok[1]['type']) && $edgeTok[1]['type'] === 'start';
                    if ($directInlineLead) {
                        $directInlineLead = false;
                        if ($lastIndex > 0) {
                            $inlineStartPos = $allEnds[0][$lastIndex][1];
                            $prevEndPos = $allEnds[0][$lastIndex - 1][1]
                                + strlen($allEnds[0][$lastIndex - 1][0]);
                            $between = substr($prefix, $prevEndPos, $inlineStartPos - $prevEndPos);
                            $prevTok = isset($this->wiki->tokens[(int)$allEnds[1][$lastIndex - 1][0]])
                                ? $this->wiki->tokens[(int)$allEnds[1][$lastIndex - 1][0]] : null;
                            if ($prevTok !== null
                                && preg_match('/\A\n[ \t]*\z/', $between) === 1
                                && isset($prevTok[1]['type']) && $prevTok[1]['type'] === 'end'
                                && in_array($prevTok[0], array('Div', 'Divalign', 'Center', 'Horiz', 'Table', 'Tableadv'), true)) {
                                $directInlineLead = true;
                            }
                            if ($directInlineLead) {
                                $openerEnd = $allEnds[0][$lastIndex][1] + strlen($allEnds[0][$lastIndex][0]);
                                if (preg_match('/\A\s*' . preg_quote($this->wiki->delim, '/') . '(\d+)'
                                    . preg_quote($this->wiki->delim, '/') . '/', substr($src, $openerEnd, 200), $bm)) {
                                    $bodyTok = isset($this->wiki->tokens[(int)$bm[1]])
                                        ? $this->wiki->tokens[(int)$bm[1]] : null;
                                    if ($bodyTok !== null && $bodyTok[0] === 'Blockquote') {
                                        $directInlineLead = false;
                                    }
                                }
                            }
                        }
                    }
                }
            }
            $afterPos = $fullPos + $fullLen;
            $after = substr($src, $afterPos, 300);
            $beforeHoriz = false;
            if (preg_match('/^\s*' . preg_quote($this->wiki->delim, '/') . '(\d+)'
                . preg_quote($this->wiki->delim, '/') . '/', $after, $hm)) {
                $horizTok = isset($this->wiki->tokens[(int)$hm[1]])
                    ? $this->wiki->tokens[(int)$hm[1]] : null;
                $beforeHoriz = $horizTok !== null && $horizTok[0] === 'Horiz';
            }
            $scopeHasPriorHoriz = false;
            $scopeHasContentParagraphBreak = false;
            $looseScopeContentBreaks = false;
            $looseScopeTokenId = null;
            $scopeTok = null;
            if (!empty($inlineStack)) {
                $scopePi = end($inlineStack);
                foreach ($horizPrefixIndexes as $horizPi) {
                    if ($horizPi > $scopePi) {
                        $scopeHasPriorHoriz = true;
                        break;
                    }
                }
                $looseScopeTokenId = (int)$allPrefixMatches[1][$scopePi][0];
                $scopeTok = isset($this->wiki->tokens[$looseScopeTokenId])
                    ? $this->wiki->tokens[$looseScopeTokenId] : null;
                if ($scopeTok !== null && !empty($scopeTok[1]['loose_scope_content_breaks'])) {
                    $scopeHasContentParagraphBreak = true;
                }
                if ($scopeAfterBlockEnd && !$directInlineLead) {
                    if ($scopeTok !== null && empty($scopeTok[1]['loose_scope_content_breaks'])) {
                        $scopeTokenStart = $allPrefixMatches[0][$scopePi][1];
                        $scopeTokenEnd = $scopeTokenStart + strlen($allPrefixMatches[0][$scopePi][0]);
                        $sinceOpener = substr($prefix, $scopeTokenEnd);
                        $sinceText = preg_replace($placeholder, '', $sinceOpener);
                        $hasOrdinaryInlineLine = false;
                        foreach (preg_split('/\r\n|\r|\n/', $sinceText) as $sinceLine) {
                            $lineText = trim($sinceLine);
                            if ($lineText !== '' && preg_match('/^(?:[*#=+>]|:|\|\|)/', $lineText) !== 1) {
                                $hasOrdinaryInlineLine = true;
                                break;
                            }
                        }
                        $sinceHasBlockToken = false;
                        if (preg_match_all($placeholder, $sinceOpener, $sinceTokens)) {
                            foreach ($sinceTokens[1] as $sinceTid) {
                                $sinceTok = isset($this->wiki->tokens[(int)$sinceTid])
                                    ? $this->wiki->tokens[(int)$sinceTid] : null;
                                if ($sinceTok !== null && isset($sinceTok[1]['type'])
                                    && ($sinceTok[1]['type'] === 'start' || substr($sinceTok[1]['type'], -6) === '_start')
                                    && in_array($sinceTok[0], array('Center', 'List', 'Deflist', 'Table', 'Tableadv', 'Blockquote', 'Heading', 'Div', 'Divalign', 'Collapsible'), true)) {
                                    $sinceHasBlockToken = true;
                                    break;
                                }
                            }
                        }
                        $looseScopeContentBreaks = $scopePrevBlockRule === 'Divalign'
                            && !$scopeHasPriorHoriz && $hasOrdinaryInlineLine && !$sinceHasBlockToken;
                    }
                }
            }
            $endsAfterWhitespaceOnlyLine = substr($prefix, -3) === "\xE3\x80\x80"
                || preg_match('/[ \t\r\n]$/', $prefix) === 1;
            $horizNeedsLooseScopeBreaks = $inlineDepth > 0 && !$directInlineLead
                && $beforeHoriz && $scopeAfterBlockEnd && $scopePrevBlockRule === 'Divalign'
                && $scopeTok !== null && in_array($scopeTok[0], array('Span', 'Size'), true)
                && !$scopeHasPriorHoriz
                && !$scopeHasContentParagraphBreak && !$endsAfterWhitespaceOnlyLine;
            if ($inlineDepth > 0 && ($directInlineLead || $horizNeedsLooseScopeBreaks || $looseScopeContentBreaks)) {
                $crossesEnclosingBlockEnd = false;
                $scanInlineRules = array('Span', 'Size');
                if ($looseScopeContentBreaks || ($scopeTok !== null && $scopeTok[0] === 'Anchor')) {
                    $scanInlineRules[] = 'Anchor';
                }
                $nestedBlockDepth = 0;
                if (!empty($inlineStack)) {
                    foreach ($allPrefixMatches[1] as $scanPi => $scanTidm) {
                        if ($scanPi <= $scopePi) {
                            continue;
                        }
                        $scanTok = isset($this->wiki->tokens[(int)$scanTidm[0]])
                            ? $this->wiki->tokens[(int)$scanTidm[0]] : null;
                        if ($scanTok === null || !isset($scanTok[1]['type'])
                            || !in_array($scanTok[0], array('Div', 'Divalign', 'Collapsible'), true)) {
                            continue;
                        }
                        if ($scanTok[1]['type'] === 'start') {
                            $nestedBlockDepth++;
                        } elseif ($scanTok[1]['type'] === 'end' && $nestedBlockDepth > 0) {
                            $nestedBlockDepth--;
                        }
                    }
                }
                if (preg_match_all($placeholder, substr($src, $afterPos), $restTokens, PREG_OFFSET_CAPTURE)) {
                    $scanDepth = 1;
                    foreach ($restTokens[1] as $rtid) {
                        $rtok = isset($this->wiki->tokens[(int)$rtid[0]])
                            ? $this->wiki->tokens[(int)$rtid[0]] : null;
                        if ($rtok === null || !isset($rtok[1]['type'])) {
                            continue;
                        }
                        if (in_array($rtok[0], $scanInlineRules, true)) {
                            if ($rtok[1]['type'] === 'start') {
                                $scanDepth++;
                            } elseif ($rtok[1]['type'] === 'end') {
                                $scanDepth--;
                                if ($scanDepth === 0) {
                                    break;
                                }
                            }
                        }
                        if ($scanDepth > 0
                            && in_array($rtok[0], array('Div', 'Divalign', 'Collapsible'), true)) {
                            if ($rtok[1]['type'] === 'start') {
                                $nestedBlockDepth++;
                            } elseif ($rtok[1]['type'] === 'end') {
                                if ($nestedBlockDepth > 0) {
                                    $nestedBlockDepth--;
                                } else {
                                    $crossesEnclosingBlockEnd = true;
                                    break;
                                }
                            }
                        }
                    }
                }
                $beforeCollapsible = $crossesEnclosingBlockEnd;
                $scanOffset = 0;
                while (preg_match($placeholder, $after, $nm, PREG_OFFSET_CAPTURE, $scanOffset)) {
                    if ($nm[0][1] !== $scanOffset) {
                        break;
                    }
                    $nextTok = isset($this->wiki->tokens[(int)$nm[1][0]])
                        ? $this->wiki->tokens[(int)$nm[1][0]] : null;
                    if ($nextTok !== null && in_array($nextTok[0], array('Collapsible', 'Div', 'Divalign', 'Table', 'Tableadv'), true)
                        && isset($nextTok[1]['type']) && $nextTok[1]['type'] === 'start') {
                        $beforeCollapsible = true;
                        break;
                    }
                    if ($nextTok === null || $nextTok[0] !== 'Paragraph') {
                        break;
                    }
                    $scanOffset += strlen($nm[0][0]);
                }
                if (($directInlineLead || $looseScopeContentBreaks) && $looseScopeTokenId !== null) {
                    $this->wiki->tokens[$looseScopeTokenId][1]['loose_scope_content_breaks'] = true;
                }
                if (!$beforeCollapsible) {
                    if ($horizNeedsLooseScopeBreaks) {
                        $this->wiki->tokens[(int)$hm[1]][1]['loose_scope_breaks'] = true;
                    } else {
                        $breaks = '';
                        for ($i = 0; $i < min(strlen($m[0][0]), 2); $i++) {
                            $breaks .= $this->wiki->addToken($this->rule, array(), false, "\n");
                        }
                        $replacement = $breaks . $m[0][0];
                    }
                }
            }
            $leadOut .= $replacement;
            $cursor = $fullPos + $fullLen;
            $search = $cursor;
        }
        $src = $leadOut . substr($src, $cursor);
        $this->wiki->source = $src;
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
            } elseif ($this->_afterExplicitItemBeforeBlock($src, $off, strlen($m[0][0]))) {
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

    private function _previousToken($src, $pos)
    {
        $delim = $this->wiki->delim;
        if ($pos < 0 || $pos >= strlen($src) || $src[$pos] !== $delim) {
            return null;
        }
        $start = strrpos(substr($src, 0, $pos), $delim);
        if ($start === false) {
            return null;
        }
        $id = substr($src, $start + 1, $pos - $start - 1);
        if (!preg_match('/^\d+$/', $id)) {
            return null;
        }
        return isset($this->wiki->tokens[(int)$id]) ? $this->wiki->tokens[(int)$id] : null;
    }

    private function _afterExplicitItemBeforeBlock($src, $off, $len)
    {
        $prev = $this->_previousToken($src, $off);
        if ($prev === null || strtolower($prev[0]) !== 'list'
            || !isset($prev[1]['type']) || $prev[1]['type'] !== 'explicit_item_start') {
            return false;
        }
        $next = $this->_nextBlockToken($src, $off + $len);
        return $next !== null && strtolower($next[0]) === 'div'
            && isset($next[1]['type']) && $next[1]['type'] === 'start';
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
