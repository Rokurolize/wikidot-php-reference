<?php

/**
*
* Parses for heading text.
*
* @category Text
*
* @package Text_Wiki
*
* @author Paul M. Jones <pmjones@php.net>
*
* @license LGPL
*
* @version $Id$
*
*/

/**
*
* Parses for heading text.
*
* This class implements a Text_Wiki_Parse to find source text marked to
* be a heading element, as defined by text on a line by itself prefixed
* with a number of plus signs (+). The heading text itself is left in
* the source, but is prefixed and suffixed with delimited tokens marking
* the start and end of the heading.
*
* @category Text
*
* @package Text_Wiki
*
* @author Paul M. Jones <pmjones@php.net>
*
*/

class Text_Wiki_Parse_Heading extends Text_Wiki_Parse {

    /**
    *
    * The regular expression used to parse the source text and find
    * matches conforming to this rule.  Used by the parse() method.
    *
    * Group 1 is the one-to-six plus run (the heading level). Group 2 is
    * the optional Wikidot no-toc suffix: a '*' immediately after the plus
    * run means the heading is rendered without an anchor and is omitted
    * from the table of contents. Group 3 is the heading text. The run of
    * whitespace after the prefix is consumed whole: live drops every
    * space or tab between the prefix and the first text character, not
    * just the first one (live probes muse-probe-r2block-head-p13-double-
    * space, -p19-tab-after and -p20-three-spaces).
    *
    * @access public
    *
    * @var string
    *
    * @see parse()
    *
    */

    public $regex = '/^(\+{1,6})(\*?)[ \t]+(.*)/m';

    public $conf = array(
        'id_prefix' => 'toc'
    );

    /**
    *
    * Generates a replacement for the matched text.  Token options are:
    *
    * 'type' => ['start'|'start-notoc'|'end'] The starting or ending point
    * of the heading text. A 'start' token carries a sequential tocN anchor
    * for the table of contents; a 'start-notoc' token deliberately does not,
    * and the Toc rule skips it because it filters on the exact 'start' type.
    *
    * @access public
    *
    * @param array &$matches The array of matches from parse().
    *
    * @return string A pair of delimited tokens to be used as a
    * placeholder in the source text surrounding the heading text.
    *
    */

    function process($matches)
    {
        // Keep a running count for anchored heading IDs. Live numbers only
        // the '+' headings, in document order, starting at zero; a '*'
        // heading has no id and does not consume a number. This counter is
        // the sole source of the anchors the Toc rule links to.
        if ($this->wiki->vars['headline_id'] === null) {
            $this->wiki->vars['headline_id'] = 0;
        }

        $level = strlen($matches[1]);
        $hasToc = ($matches[2] === '');
        $prefix = htmlspecialchars($this->getConf('id_prefix'));

        if ($hasToc) {
            $id = $prefix . $this->wiki->vars['headline_id'];
            $startType = 'start';
            $this->wiki->vars['headline_id']++;
        } else {
            $id = null;
            $startType = 'start-notoc';
        }

        $start = $this->wiki->addToken(
            $this->rule,
            array(
                'type' => $startType,
                'level' => $level,
                'text' => $matches[3],
                'id' => $id
            )
        );

        $end = $this->wiki->addToken(
            $this->rule,
            array(
                'type' => 'end',
                'level' => $level
            )
        );

        return "\n".$start . $matches[3] . $end . "\n\n";
    }
}
