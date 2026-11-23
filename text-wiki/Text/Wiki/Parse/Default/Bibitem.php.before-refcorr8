<?php

/**
 * 
 * Parses bibliography items within the [[bibliography]] block.
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
 * Parses bibliography items within the [[bibliography]] block.
 *
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Michal Frackowiak
 * 
 */

class Text_Wiki_Parse_Bibitem extends Text_Wiki_Parse {

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

    function process($matches) {
        $label = $matches[1];
        $content = $matches[2];
        $content = trim(str_replace("\n", " ", $content));
        $this->wiki->vars['bibitems'][$label] = $content;
        $id = count($this->wiki->vars['bibitemIds']) + 1;
        $this->wiki->vars['bibitemIds'][$label] = $id;
        // R2-notes: live renders an empty entry as "N." with no trailing
        // space, so tell the render rule whether the trimmed body is empty.
        // REFCORR7: an empty-Raw placeholder is \xFF<id>\xFF naming a token
        // ['Raw', ['text' => '']] whose render is nothing, so an entry whose
        // stored content is only such placeholders is an empty body
        // (S4C bib-empty). Strip those placeholders only to compute the
        // 'empty' flag; vars['bibitems'][$label] keeps the exact stored
        // bytes, so the compared state/token wire shape is otherwise intact.
        $delim = preg_quote($this->wiki->delim, '/');
        $visible = preg_replace_callback(
            '/' . $delim . '(\d+)' . $delim . '/',
            function ($m) {
                $tok = $this->wiki->tokens[(int) $m[1]] ?? null;
                if ($tok !== null && $tok[0] === 'Raw'
                    && isset($tok[1]['text']) && $tok[1]['text'] === '') {
                    return '';
                }
                return $m[0];
            },
            $content);
        return $this->wiki->addToken($this->rule, 
                array(
                    'label' => $label, 
                    'id' => $id, 
                    'type' => 'start',
                    'empty' => ($visible === ''))) .
                 $content . $this->wiki->addToken(
                        $this->rule, 
                        array(
                            'type' => 'end'));
    }
}
