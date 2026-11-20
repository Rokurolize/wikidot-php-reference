<?php

/**
*
* Parses for bulleted and numbered lists.
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
* Parses for bulleted and numbered lists.
*
* A line whose first character is '*' or '#' followed by exactly one space
* begins a bullet or numbered item, and each additional leading space before
* that marker opens one more level of nesting. A new marker type at the same
* depth ends the current run and starts a new list, as does a blank line. The
* outermost list must begin at column zero; an indented first line is literal
* text. The outer regex finds a maximal run; process() then turns its lines
* into the token stream consumed by the Xhtml render rule.
*
* R2 List corrections against live Wikidot (fossil-era artifacts): an item
* whose body is empty or whitespace-only is dropped unless a deeper item
* immediately follows it, in which case it survives as an empty list item
* holding the child list; a list whose every item is empty emits no list at
* all. Extra spaces after the marker are not part of the item body. A depth
* skip of more than one level is represented by one inline-style list-item
* wrapper per missing level, matching the live nested-list shape. See
* conformance-refphp/list/list/SECTION.md for the probes and pins.
*
* @category Text
*
* @package Text_Wiki
*
* @author Paul M. Jones <pmjones@php.net>
*
*/

class Text_Wiki_Parse_List extends Text_Wiki_Parse {

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

    public $regex = '/^((\*|#) .*\n)(?!\2 |(?: {1,}((?:\*|#) |\n)))/Usm';

    /**
    *
    * Generates a replacement for the matched text.  Token options are:
    *
    * 'type' =>
    *     'bullet_list_start' : the start of a bullet list
    *     'bullet_list_end'   : the end of a bullet list
    *     'number_start'      : the start of a number list
    *     'number_end'        : the end of a number list
    *     'sublist_start'     : an inline wrapper for a skipped depth level
    *     'sublist_end'       : the end of that wrapper
    *     'item_start'        : the start of item text
    *     'item_end'          : the end of item text
    *
    * 'level' => the zero-based nesting depth.
    *
    * 'count' => the item number at this depth.
    *
    * 'in_sublist' => whether a list or its close sits inside a wrapper.
    *
    * 'tail' => whether a list's last child was an item or a sublist wrapper.
    *
    * @access public
    *
    * @param array &$matches The array of matches from parse().
    *
    * @return A series of text and delimited tokens marking the different
    * list text and list elements.
    *
    */

    function process($matches)
    {
        // the replacement text we will return
        $return = '';

        // collect this run's item lines before deciding which survive
        $raw = array();
        preg_match_all(
            '=^( {0,})(\*|#) (.*)$=Ums',
            $matches[1],
            $list,
            PREG_SET_ORDER
        );
        foreach ($list as $val) {
            $raw[] = array(
                'depth' => strlen($val[1]),
                'type' => ($val[2] == '*') ? 'bullet' : 'number',
                'body' => ltrim($val[3], " \t"),
            );
        }

        // live drops a whitespace-only item unless a deeper item follows it;
        // a run with no surviving items leaves no list behind at all
        $items = array();
        $total = count($raw);
        foreach ($raw as $index => $item) {
            $empty = (trim($item['body']) === '');
            $hasChild = ($index + 1 < $total
                && $raw[$index + 1]['depth'] > $item['depth']);
            if (! $empty || $hasChild) {
                $items[] = $item;
            }
        }
        if (count($items) === 0) {
            return '';
        }

        // the stack holds one entry per open list, with the type of that
        // list and whether its most recent child was a sublist wrapper
        $stack = array();
        $itemcount = array();

        // close one level; a sublist tail closes its wrapper before the list
        $closeLevel = function ($level) use (&$return, &$stack) {
            $entry = $stack[$level];
            if ($entry['tail'] === 'sublist') {
                $return .= $this->wiki->addToken(
                    $this->rule,
                    array('type' => 'sublist_end', 'level' => $level)
                );
            }
            $return .= $this->wiki->addToken(
                $this->rule,
                array(
                    'type' => $entry['type'] . '_list_end',
                    'level' => $level,
                    'in_sublist' => $entry['in_sublist'],
                    'tail' => $entry['tail'],
                )
            );
            unset($stack[$level]);
        };

        foreach ($items as $item) {
            $depth = $item['depth'];
            $type = $item['type'];

            // open every missing level. The first new list is the child of
            // the current item; each further one is wrapped in an inline
            // list item, which is live's shape for a skipped depth.
            $firstNewLevel = count($stack);
            while ($depth >= count($stack)) {
                $level = count($stack);
                $inSublist = ($level > $firstNewLevel);
                if ($inSublist) {
                    $stack[$level - 1]['tail'] = 'sublist';
                    $return .= $this->wiki->addToken(
                        $this->rule,
                        array('type' => 'sublist_start', 'level' => $level)
                    );
                }
                $stack[$level] = array(
                    'type' => $type,
                    'in_sublist' => $inSublist,
                    'tail' => 'item',
                );
                $return .= $this->wiki->addToken(
                    $this->rule,
                    array(
                        'type' => $type . '_list_start',
                        'level' => $level,
                        'in_sublist' => $inSublist,
                    )
                );
            }

            // unwind to the item's depth
            while (count($stack) > $depth + 1) {
                $level = count($stack) - 1;
                $closeLevel($level);
                unset($itemcount[$level]);
            }

            if (! isset($itemcount[$depth])) {
                $itemcount[$depth] = 0;
            } else {
                $itemcount[$depth]++;
            }

            $return .= $this->wiki->addToken(
                $this->rule,
                array(
                    'type' => $type . '_item_start',
                    'level' => $depth,
                    'count' => $itemcount[$depth],
                    'first' => ($itemcount[$depth] === 0),
                )
            );
            $return .= $item['body'];
            $return .= $this->wiki->addToken(
                $this->rule,
                array(
                    'type' => $type . '_item_end',
                    'level' => $depth,
                    'count' => $itemcount[$depth],
                )
            );
        }

        // close every list still open at the end of the run
        while (count($stack) > 0) {
            $closeLevel(count($stack) - 1);
        }

        return "\n\n" . $return . "\n\n";
    }
}
