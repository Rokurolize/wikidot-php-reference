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
    
    public $regex = '/(\n)?\[\[collapsible(\s.*?)?\]\](.*?)\[\[\/collapsible\]\] */msi';

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
        
        $content = $matches[3];

        // When [[size ...]][[collapsible ...]][[/size]] wraps only the opener,
        // transfer font-size to Collapsible's fold labels and suppress the
        // dangling Size pair while keeping token delimiters for Newline.
        $labelSize = null;
        $delim = $this->wiki->delim;
        $q = preg_quote($delim, '/');
        if (preg_match('/^' . $q . '(\d+)' . $q . '/', $content, $mm)) {
            $eid = (int)$mm[1];
            $et = isset($this->wiki->tokens[$eid]) ? $this->wiki->tokens[$eid] : null;
            if ($et && $et[0] === 'Size' && isset($et[1]['type']) && $et[1]['type'] === 'end') {
                $sizeDepth = 0;
                $sid = null;
                for ($j = $eid - 1; $j >= 0; $j--) {
                    $t = $this->wiki->tokens[$j];
                    if ($t[0] !== 'Size' || !isset($t[1]['type'])) {
                        continue;
                    }
                    if ($t[1]['type'] === 'end') {
                        $sizeDepth++;
                    } elseif ($t[1]['type'] === 'start') {
                        if ($sizeDepth === 0) {
                            $sid = $j;
                            break;
                        }
                        $sizeDepth--;
                    }
                }
                if ($sid !== null) {
                    $labelSize = $this->wiki->tokens[$sid][1]['size'];
                    $this->wiki->tokens[$sid][1]['type'] = 'suppressed';
                    $this->wiki->tokens[$eid][1]['type'] = 'suppressed';
                }
            }
        }

        $attr = $this->getAttrs(trim($matches[2]));

        $options = array('args' => $attr, 'type' => 'start',
            'count' => self::$count, 'label_size' => $labelSize);

        $start = $this->wiki->addToken($this->rule, $options);

        $end = $this->wiki->addToken($this->rule, array(
            'args' => $attr, 'type' => 'end',
            'count' => self::$count, 'label_size' => $labelSize));
        self::$count++;
        return $matches[1] . $matches[1] . $start . "\n\n" . $content . "\n\n" . $end;
    
    }

}
