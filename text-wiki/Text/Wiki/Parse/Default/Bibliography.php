<?php

/**
 * 
 * Parses the [[bibliography]] block.
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
 * Parses the [[bibliography]] block.
 *
 * @category Text
 * 
 * @package Text_Wiki
 * 
 * @author Michal Frackowiak
 * 
 */

class Text_Wiki_Parse_Bibliography extends Text_Wiki_Parse {

    public $regex = null;

    function parse() {
        $regex = '/^\[\[bibliography(\s+[^\]]+)?\]\](.*?)\[\[\/bibliography\]\][ ]*$/sm';
        $this->wiki->source = preg_replace_callback($regex, array(
            &$this, 'process'), $this->wiki->source, 1);
    }

    function process($matches) {
        $inner = $matches[2];
        $args = $this->getAttrs($matches[1]);
        $title = $args['title'];
        if ($this->wiki->vars['bibitems'] == null) {
            $this->wiki->vars['bibitems'] = array();
            $this->wiki->vars['bibitemIds'] = array();
        }
        // Bibitem (position 22) runs before this rule on live, so a
        // ': label : text' line is already an entry token in the joined
        // body. Walk the body line by line and lay the newline tokens out
        // as live does: a newline before a residual run and after it when
        // an entry follows, consecutive residual lines separated by one
        // space, and definition lines adjacent with no separator. The
        // pattern's \s consumes a line break after the second colon, which
        // is how a value written on the following line joins its label.
        $bi = $this->wiki->parseObj['Bibitem'];
        $pattern = '/^:\s?([a-z0-9]+)\s?:\s(.*)(\n|$)|^([^\n]*)(\n|$)/mi';
        $prev = null;
        $self = $this;
        $inside = preg_replace_callback($pattern,
            function ($m) use (&$bi, &$prev, $self) {
                $isDef = isset($m[1]) && $m[1] !== '';
                if ($isDef) {
                    $prefix = ($prev === 'res')
                        ? $self->wiki->addToken($self->rule, array('type' => 'nl'))
                        : '';
                    $replacement = $bi->process(array($m[0], $m[1], $m[2]));
                    $prev = 'def';
                } else {
                    $text = isset($m[4]) ? $m[4] : '';
                    if (trim($text) === '') {
                        return '';
                    }
                    if ($prev === null || $prev === 'def') {
                        $prefix = $self->wiki->addToken($self->rule, array('type' => 'nl'));
                    } else {
                        $prefix = ' ';
                    }
                    // Live collapses runs of ASCII whitespace inside a
                    // residual body line to a single space, including a
                    // leading tab after the colon; non-breaking spaces are
                    // left alone.
                    // REFCORR12 — drop the live-discarded C0 set D before that
                    // fold. PCRE \s includes FF (12) and VT (11), both in D,
                    // so folding first would turn an FF into an ordinary space
                    // that Tighten.php:99 can no longer remove; live purifies
                    // the FF itself (C-R5E-S1-3). D is the C0 range below 0x20
                    // except TAB (9), LF (10), CR (13) and ESC (27), the same
                    // class the footnote, bibitem and Tighten paths use; TAB
                    // and CR are kept and still fold to one space, and ESC is
                    // kept verbatim.
                    $text = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1A\x1C-\x1F]/', '', $text);
                    $replacement = preg_replace('/\s+/', ' ', $text);
                    $prev = 'res';
                }
                return $prefix . $replacement;
            }, $inner);

        return "\n" . $this->wiki->addToken($this->rule, array(
            'type' => 'start', 'title' => $title)) . $inside . $this->wiki->addToken($this->rule, array(
            'type' => 'end')) . "\n";
    }

    function insertBibitem($matches) {
        return $matches[2];
    }

}
