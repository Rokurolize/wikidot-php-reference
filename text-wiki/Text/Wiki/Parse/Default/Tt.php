<?php

/**
*
* Find source text marked for teletype (monospace).
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
* Find source text marked for teletype (monospace).
*
* Defined by text surrounded by two curly braces. On parsing, the text
* itself is left in place, but the starting and ending instances of
* curly braces are replaced with tokens.
*
* Token options are:
*
* 'type' => ['start'|'end'] The starting or ending point of the
* teletype text.  The text itself is left in the source.
*
* @category Text
*
* @package Text_Wiki
*
* @author Paul M. Jones <pmjones@php.net>
* @author Michal Frackowiak
*
*/

class Text_Wiki_Parse_Tt extends Text_Wiki_Parse {

    /**
    *
    * The regular expression used to parse the source text.
    *
    * @access public
    *
    * @var string
    *
    * @see parse()
    *
    */

    public $regex = "/{{({*?.*}*?)}}/U";

    /**
    *
    * Apply the monospace rule with source-context offsets.
    *
    * The base class applies the regex with preg_replace_callback(), which
    * gives process() only the matched text and no surrounding context. Live
    * Wikidot (and ftml's monospace rule) hoist edge padding out of the <tt>
    * container and only re-emit it as a separator when the neighbouring
    * source character is non-whitespace, so the offsets are needed here.
    * preg_match_all() with the same regex walks the same non-overlapping
    * left-to-right matches; literal text between them is copied verbatim.
    *
    * @access public
    *
    * @return void
    *
    */

    function parse()
    {
        if (! $this->regex) {
            return;
        }
        $source = $this->wiki->source;
        $matches = array();
        preg_match_all($this->regex, $source, $matches, PREG_OFFSET_CAPTURE);
        if (empty($matches[0])) {
            return;
        }
        $out = '';
        $cursor = 0;
        $length = strlen($source);
        foreach ($matches[0] as $index => $match) {
            $whole = $match[0];
            $start = $match[1];
            $end = $start + strlen($whole);
            $out .= substr($source, $cursor, $start - $cursor);
            $before = $start > 0 ? $source[$start - 1] : '';
            $after = $end < $length ? $source[$end] : '';
            $tail = substr($source, $end);
            $out .= $this->process($matches, $index, $before, $after, $tail);
            $cursor = $end;
        }
        $out .= substr($source, $cursor);
        $this->wiki->source = $out;
    }

    /**
    *
    * Generates a replacement for the matched text.
    *
    * Leading and trailing literal spaces/tabs are padding, not content:
    * live and ftml strip them from inside <tt> and re-emit a single
    * separator outside it only when the adjacent source character is not
    * whitespace (and, for a trailing pad, not when the next construct is
    * itself a padded monospace opener, which supplies the separator). Runs
    * of interior spaces/tabs collapse to one space. An empty body, a
    * padding-only body and the exact string "0" produce no <tt> container;
    * a padding-only body still leaves one visible space.
    *
    * @access public
    *
    * @param array &$matches The array of matches from parse().
    *
    * @return string A pair of delimited tokens to be used as a
    * placeholder in the source text surrounding the teletype text.
    *
    */

    function process($matches, $index = 0, $before = '', $after = '', $tail = '')
    {
        $body = $matches[1][$index][0];

        $leading = '';
        while ($body !== '' && ($body[0] === ' ' || $body[0] === "\t")) {
            $leading .= $body[0];
            $body = substr($body, 1);
        }
        $trailing = '';
        while ($body !== '' && (substr($body, -1) === ' ' || substr($body, -1) === "\t")) {
            $trailing = substr($body, -1) . $trailing;
            $body = substr($body, 0, -1);
        }
        $body = preg_replace('/[ \t]+/', ' ', $body);

        if ($body === '' || $body === '0') {
            if ($body === '' && ($leading !== '' || $trailing !== '')) {
                return ' ';
            }
            return '';
        }

        $lead_out = ($leading !== '' && $before !== ''
            && ! preg_match('/\s/', $before)) ? ' ' : '';
        $padded_follower = ($tail !== '' && preg_match('/^\{\{[ \t]/', $tail) === 1);
        $trail_out = ($trailing !== '' && $after !== ''
            && ! preg_match('/\s/', $after) && ! $padded_follower) ? ' ' : '';

        $start = $this->wiki->addToken(
            $this->rule, array('type' => 'start')
        );

        $end = $this->wiki->addToken(
            $this->rule, array('type' => 'end')
        );

        return $lead_out . $start . $body . $end . $trail_out;
    }
}
