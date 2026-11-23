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
        // REFCORR11 — apply the same unconditional live C0-control filter the
        // footnote branch applies, before the empty-Raw strip and re-trim;
        // PHP trim excludes form feed (12), so a FF between two empty Raw
        // placeholders survived REFCORR8 as a non-empty body and separator
        // space (C-R5D-R3-2) where live settles an empty entry.
        // vars['bibitems'][$label] above stays byte-identical so the compared
        // state and token wire shape do not change. TAB, LF-derived spaces,
        // CR and NBSP are all preserved.
        // REFCORR12 — narrow to the live-discarded set D = C0 bytes below 0x20
        // except TAB (9), LF (10), CR (13) and ESC (27), i.e.
        // [\x00-\x08\x0B\x0C\x0E-\x1A\x1C-\x1F]. Live keeps ESC in a note body
        // (C-R5E-P4-1 / C-R5E-S1-2), so the REFCORR11 upper range was one byte
        // too wide; FF and the rest of D are still dropped on every shape.
        $content = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1A\x1C-\x1F]/', '', $content);
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
        // REFCORR8 (C-R5-R3-2): re-trim the visible remainder after the
        // empty-Raw strip. REFCORR7 trimmed only before the strip and kept
        // the body verbatim, so two placeholders separated by whitespace
        // left a stray space that made 'empty' false and the body non-empty;
        // live folds both to empty. vars['bibitems'][$label] was set above
        // and stays byte-identical, so compared state is unchanged and no
        // compared field is added; only the emitted body and flag change.
        $visible = trim($visible);
        $content = $visible;
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
