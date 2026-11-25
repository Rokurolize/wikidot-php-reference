<?php

/**
 * 
 * Creates a collapsible content block.
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
 * Creates a collapsible content block.
 *
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Michal Frackowiak
 * 
 */

class Text_Wiki_Parse_Collapsible extends Text_Wiki_Parse {

    static $count = 0;
    
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
    
    public $regex = '/(\xFF\d+\xFF)?(\n)?\[\[collapsible(\s.*?)?\]\](.*?)\[\[\/collapsible\]\] */msi';

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
        
        $content = $matches[4];

        // When a Size span begins immediately at the collapsible opener,
        // transfer font-size to Collapsible's fold labels and re-open any
        // visible-body or trailing part inside valid block boundaries.
        // Unrelated size spans inside a collapsible body must be left alone
        // (news-03-2017 regression guard).
        $labelSize = null;
        $delim = $this->wiki->delim;
        $q = preg_quote($delim, '/');
        $sid = null;
        $outerStart = '';
        if ($matches[1] !== ''
            && preg_match('/^' . $q . '(\d+)' . $q . '$/', $matches[1], $sm)) {
            $candidateSid = (int)$sm[1];
            $st = isset($this->wiki->tokens[$candidateSid])
                ? $this->wiki->tokens[$candidateSid] : null;
            if ($st && $st[0] === 'Size' && isset($st[1]['type'])
                && $st[1]['type'] === 'start') {
                $sid = $candidateSid;
            }
        }
        if ($sid !== null) {
            $endPos = null;
            $endId = null;
            if (preg_match_all('/' . $q . '(\d+)' . $q . '/', $content, $ms, PREG_OFFSET_CAPTURE)) {
                $sizeDepth = 1;
                foreach ($ms[1] as $mi => $candidate) {
                    $eid = (int)$candidate[0];
                    $pos = $ms[0][$mi][1];
                    $et = isset($this->wiki->tokens[$eid]) ? $this->wiki->tokens[$eid] : null;
                    if (!$et || $et[0] !== 'Size' || !isset($et[1]['type'])) {
                        continue;
                    }
                    if ($et[1]['type'] === 'start') {
                        $sizeDepth++;
                        continue;
                    }
                    if ($et[1]['type'] !== 'end') {
                        continue;
                    }
                    $sizeDepth--;
                    if ($sizeDepth === 0) {
                        $endPos = $pos;
                        $endId = $eid;
                        break;
                    }
                }
            }

            $trimmedContent = trim($content);
            $simpleBody = $trimmedContent !== ''
                && strpos($trimmedContent, "\n") === false
                && strpos($trimmedContent, "\r") === false;
            $openerOnly = false;
            $rescopeBody = false;
            if ($endPos !== null) {
                $beforeEnd = substr($content, 0, $endPos);
                if (trim($beforeEnd) === '') {
                    $openerOnly = true;
                } elseif ($simpleBody) {
                    $rescopeBody = true;
                }
            } elseif ($simpleBody) {
                $rescopeBody = true;
            }

            if ($openerOnly || $rescopeBody) {
                $labelSize = $this->wiki->tokens[$sid][1]['size'];
                $this->wiki->tokens[$sid][1]['type'] = 'suppressed';
                if ($openerOnly) {
                    $this->wiki->tokens[$endId][1]['type'] = 'suppressed';
                } elseif ($endPos !== null) {
                    $beforeEnd = substr($content, 0, $endPos);
                    if (preg_match('/\S/', $beforeEnd, $first, PREG_OFFSET_CAPTURE)) {
                        $insertAt = $first[0][1];
                        $innerStart = $this->wiki->addToken('Size', array(
                            'size' => $labelSize,
                            'type' => 'start'
                        ));
                        $content = substr($content, 0, $insertAt)
                            . $innerStart
                            . substr($content, $insertAt);
                    }
                } elseif (preg_match('/\S/', $content, $first, PREG_OFFSET_CAPTURE)) {
                    $innerStart = $this->wiki->addToken('Size', array(
                        'size' => $labelSize,
                        'type' => 'start'
                    ));
                    $innerEnd = $this->wiki->addToken('Size', array('type' => 'end'));
                    $insertStart = $first[0][1];
                    $lastPos = null;
                    if (preg_match_all('/\S/', $content, $visible, PREG_OFFSET_CAPTURE)) {
                        $lastPos = $visible[0][count($visible[0]) - 1][1] + 1;
                    }
                    $content = substr($content, 0, $insertStart)
                        . $innerStart
                        . substr($content, $insertStart, $lastPos - $insertStart)
                        . $innerEnd
                        . substr($content, $lastPos);
                    $outerStart = $this->wiki->addToken('Size', array(
                        'size' => $labelSize,
                        'type' => 'start'
                    ));
                }
            }
        }

        $attr = $this->getAttrs(trim($matches[3]));

        $options = array('args' => $attr, 'type' => 'start',
            'count' => self::$count, 'label_size' => $labelSize);

        $start = $this->wiki->addToken($this->rule, $options);

        $end = $this->wiki->addToken($this->rule, array(
            'args' => $attr, 'type' => 'end',
            'count' => self::$count, 'label_size' => $labelSize));
        self::$count++;
        return $matches[1] . $matches[2] . $matches[2] . $start . "\n\n" . $content . "\n\n" . $end . $outerStart;
    
    }

}
