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
