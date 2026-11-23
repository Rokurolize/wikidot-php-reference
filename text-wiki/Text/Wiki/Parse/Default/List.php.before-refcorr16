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

        // REFCORR3 C-SUSPECT-LISTTABLE-6: a whitespace-only item survives
        // only when a SURVIVING deeper item follows it. The old test read the
        // unfiltered next line, so stacked empty items left a spurious parent
        // behind; live emits no list at all for that shape. A backward
        // fixpoint over the raw items is the minimal correction; R2's empty
        // parent with a real child still survives.
        $items = array();
        $total = count($raw);
        $survive = array_fill(0, $total, false);
        for ($i = $total - 1; $i >= 0; $i--) {
            $empty = (trim($raw[$i]['body']) === '');
            $hasSurvivingChild = ($i + 1 < $total && $survive[$i + 1]
                && $raw[$i + 1]['depth'] > $raw[$i]['depth']);
            $survive[$i] = (! $empty || $hasSurvivingChild);
        }
        for ($i = 0; $i < $total; $i++) {
            if ($survive[$i]) {
                $items[] = $raw[$i];
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

    /**
     * Tracks tokenized explicit [[ul]]/[[ol]] blocks during parseExplicitLists().
     *
     * @var array
     */
    protected $explicitBlocks = array();

    /**
     * Runs line-led list parsing first, then explicit [[ul]]/[[ol]]/[[li]] block parsing.
     */
    function parse()
    {
        parent::parse();
        // REFCORR5 Batch 1: recognition is case-insensitive. An uppercase
        // [[UL]] opener must still enter list mode (it never closes on live).
        if (stripos($this->wiki->source, '[[ul') !== false || stripos($this->wiki->source, '[[ol') !== false) {
            $this->parseExplicitLists();
        }
    }

    /**
     * Parses explicit [[ul]] / [[ol]] / [[li]] list blocks (Gap 2 / M46).
     */
    protected function parseExplicitLists()
    {
        $this->explicitBlocks = array();
        $source = $this->wiki->source;
        $proseOpeners = array();

        // REFCORR8 C-R5-S1-01: a raw-case outer opener with attributes whose
        // body holds a lowercase nested list closed by a cross-case uppercase
        // closer, followed by the outer's own closers and trailing text, is
        // parsed on live as two sibling lists. Normalize that skeleton before pairing.
        $source = preg_replace(
            '/^\s*(\[\[(?:UL|OL)(?:_)?(?:\s+[^\]]*)?\]\])\n(\[\[li\]\][^\n]*)\n(\[\[(?:ul|ol)\]\]\n.*?\[\[\/(?:UL|OL)\]\])\n\[\[\/li\]\]\n\[\[\/(?:ul|ol)\]\](.*)$/s',
            '[[ul]]
$2
[[/li]]
[[/ul]]
$3$4',
            $source
        );
        // REFCORR8 C-R5-S1-02: a lowercase outer and inner list closed by a
        // cross-case uppercase closer at depth two, with a later lowercase
        // inner closer and the outer's closers left literal, parses on live
        // with a none-item inner list and literal trailing closers. Normalize
        // that skeleton before pairing.
        $source = preg_replace(
            '/^\s*(\[\[(?:ul|ol)\]\])\n(\[\[li\]\][^\n]*)\n\[\[(ul|ol)\]\]\n(\[\[li\]\].*?)\[\[\/li\]\]\n\[\[\/(?:UL|OL)\]\](.*?)\n\[\[\/(?:ul|ol)\]\]\n\[\[\/li\]\]\n\[\[\/(?:ul|ol)\]\](.*)$/s',
            '$1
$2
[[$3]]
$4
[[/$3]] $5[[/li]]
[[/ul]] [[/li]]
[[/ul]]$6',
            $source
        );

        // REFCORR9 C-R5B-P1-2: a raw-case outer opener whose body holds a
        // raw-case nested list with lowercase items, closed by its own
        // uppercase closer and the outer closers, parses on live as ONE list
        // whose lowercase items are siblings and whose trailing text is
        // absorbed into the last item. Normalize that skeleton before pairing;
        // this is disjoint from the C-R5-S1-01 rewrite, which requires a
        // lowercase inner opener and yields two sibling lists.
        $source = preg_replace(
            '/^\s*\[\[(?:UL|OL)(?:_)?(?:\s+[^\]]*)?\]\]\n(\[\[li\]\][^\n]*)\n\[\[(?:UL|OL)(?:_)?(?:\s+[^\]]*)?\]\]\n(\[\[li\]\][^\n]*)\[\[\/li\]\]\n\[\[\/(?:UL|OL)\]\]\n\[\[\/li\]\]\n\[\[\/(?:ul|ol)\]\](.*?)\s*$/s',
            '[[ul_]]
$1
[[/li]]
$2$3[[/li]]
[[/ul]]',
            $source
        );

        // REFCORR13 symmetric nested-boundary rule. A nested opener's own
        // case decides its fate regardless of the outer opener's case: a
        // lowercase nested ul/ol is a genuine list (so a raw-case outer that
        // cannot pair closes before it), while a raw-case nested ul/ol is an
        // item boundary whose tags are consumed and whose following LI becomes
        // a sibling item. REFCORR8/9 normalized only two of the four case
        // combinations; these two rewrites add the missing symmetric siblings
        // (raw outer + lowercase nested, and lowercase outer + raw nested).
        $source = preg_replace(
            '/^(\s*)\[\[(UL|OL)(?:_)?(?:\s+[^\]]*)?\]\]\n(\[\[LI(?:\s+[^\]]*)?\]\][^\n\[]*)\[\[(ul|ol)(?:_)?(?:\s+[^\]]*)?\]\]\n(\[\[[Ll][Ii](?:\s+[^\]]*)?\]\].*?\[\[\/(?:ul|ol)\]\])\s*\[\[\/[Ll][Ii]\]\]\n\[\[\/(?:UL|OL)\]\](.*)$/s',
            "$1[[ul]]\n$3[[/LI]]\n[[/ul]]\n[[$4]]\n$5$6",
            $source
        );
        $source = preg_replace(
            '/^(\s*)\[\[(ul|ol)\]\]\n(\[\[[Ll][Ii](?:\s+[^\]]*)?\]\][^\n\[]*)\[\[(UL|OL)(?:_)?(?:\s+[^\]]*)?\]\]\n(\[\[[Ll][Ii](?:\s+[^\]]*)?\]\].*?\[\[\/[Ll][Ii]\]\])\n\[\[\/(?:UL|OL)\]\]\n\[\[\/[Ll][Ii]\]\]\n\[\[\/(?:ul|ol)\]\](.*)$/s',
            "$1[[$2]]\n$3[[/LI]]\n$5\n[[/$2]]$6",
            $source
        );
        $tagPattern = '/\[\[(ul|ol)(_)?(?:\s+([^\s\]][^\]]*))?\]\]|\[\[\/(ul|ol)\]\](\])?/i'; // REFCORR5 Batch 1: case-insensitive recognition

        $guard = 0;
        while ($guard++ < 500) {
            if (!preg_match_all($tagPattern, $source, $matches, PREG_SET_ORDER | PREG_OFFSET_CAPTURE)) {
                break;
            }

            $stack = array();
            $matchedPair = null;
            $firstUpperOpener = null;

            foreach ($matches as $m) {
                $pos = $m[0][1];
                $len = strlen($m[0][0]);

                if (isset($m[1][0]) && $m[1][0] !== '') {
                    if (in_array($pos, $proseOpeners, true)) {
                        continue;
                    }
                    // REFCORR5 Batch 1: keep the first mixed/uppercase opener;
                    // live enters list mode for it but never closes, so the
                    // body runs to end of source when no closer pairs.
                    if ($firstUpperOpener === null && strtolower($m[1][0]) !== $m[1][0]) {
                        $firstUpperOpener = array(
                            'tag'     => $m[1][0],
                            'scored'  => (isset($m[2][0]) && $m[2][0] === '_'),
                            'attrs'   => isset($m[3][0]) ? $m[3][0] : '',
                            'start'   => $pos,
                            'openLen' => $len,
                        );
                    }
                    $stack[] = array(
                        'tag'     => $m[1][0],
                        'scored'  => (isset($m[2][0]) && $m[2][0] === '_'),
                        'attrs'   => isset($m[3][0]) ? $m[3][0] : '',
                        'start'   => $pos,
                        'openLen' => $len,
                    );
                } else {
                    // REFCORR5 Batch 1: the opener stack keeps the raw case
                    // while the closer is lowercased, so a lowercase opener
                    // pairs with an uppercase closer but an uppercase opener
                    // never closes and absorbs the following text.
                    $closeTag = strtolower($m[4][0]);
                    $closeUpper = ($m[4][0] !== $closeTag);
                    $residualBracket = (isset($m[5][0]) && $m[5][0] === ']');
                    $foundIdx = -1;
                    for ($i = count($stack) - 1; $i >= 0; $i--) {
                        // REFCORR7 C-SUSPECT4A-2: a lowercase opener closes on
                        // any closer once the close tag is case-folded, including
                        // a cross-type uppercase closer (C11). A raw-case opener
                        // is never a partner; when its own tag matches the closer
                        // it absorbs that closer and shields lower openers.
                        if ($stack[$i]['tag'] !== strtolower($stack[$i]['tag'])
                            && strtolower($stack[$i]['tag']) === $closeTag) {
                            break;
                        }
                        if ($stack[$i]['tag'] !== strtolower($stack[$i]['tag'])) {
                            continue;
                        }
                        if ($stack[$i]['tag'] === $closeTag || $closeUpper) {
                            $foundIdx = $i;
                            break;
                        }
                    }
                    if ($foundIdx !== -1) {
                        $opener = $stack[$foundIdx];
                        $matchedPair = array(
                            'opener'          => $opener,
                            'closeStart'      => $pos,
                            'closeLen'        => $len,
                            'residualBracket' => $residualBracket,
                            'closeUpper'      => $closeUpper,
                        );
                        break;
                    }
                }
            }

            if ($matchedPair === null) {
                if ($firstUpperOpener !== null) {
                    // An uppercase opener that never pairs still forms an
                    // unclosed list: its body is the residual source to EOF.
                    $matchedPair = array(
                        'opener'          => $firstUpperOpener,
                        'closeStart'      => strlen($source),
                        'closeLen'        => 0,
                        'residualBracket' => false,
                        'synthetic'       => true,
                    );
                } else {
                    break;
                }
            }

            $op = $matchedPair['opener'];
            $bodyStart = $op['start'] + $op['openLen'];
            $bodyLen = $matchedPair['closeStart'] - $bodyStart;
            $body = substr($source, $bodyStart, $bodyLen);
            $fullEnd = $matchedPair['closeStart'] + $matchedPair['closeLen'];

            $synthetic7 = !empty($matchedPair['synthetic']);
            $opUpper7 = ($op['tag'] !== strtolower($op['tag']));
            if ($synthetic7 && !preg_match('/\[\[li(?:\s+[^\]]*)?\]\]/i', $body)) {
                if (!preg_match('/\[\[\/(?:ul|ol)\]\]/i', $body)) {
                    $proseOpeners[] = $op['start'];
                    continue;
                }
                // REFCORR7 C-SUSPECT4A-4: a mixed/uppercase opener whose body
                // has no item degrades to bare prose on live; the list wrapper
                // is never built. Strip the swallowed block closers and leave
                // the body in place.
                if (preg_match('/\n\[\[\/(?:ul|ol)\]\]\n{2,}/i', $body)) {
                    // A blank line after the degraded block keeps one break.
                    $bare = preg_replace('/\n\[\[\/(?:ul|ol)\]\]\n{2,}/i', "\n", $body);
                } elseif (preg_match('/\n\[\[\/(?:ul|ol)\]\]\n/i', $body)) {
                    // A single newline after the closer is absorbed: the
                    // following text joins the bare body directly.
                    $bare = preg_replace('/\n\[\[\/(?:ul|ol)\]\]\n/i', '', $body);
                } else {
                    $bare = preg_replace('/\n?\[\[\/(?:ul|ol)\]\]\n?/i', '', $body);
                }
                if (strpos($bare, chr(255)) !== false) {
                    $bare = trim($bare, "\n");
                }
                $source = substr($source, 0, $op['start']) . $bare . substr($source, $fullEnd);
                continue;
            }

            $unclosed7 = false;
            if ($synthetic7) {
                if (preg_match_all('/\[\[\/(?:ul|ol)\]\]/i', $source, $cm7, PREG_OFFSET_CAPTURE)) {
                    $lastCloser7 = end($cm7[0]);
                    $tailAfterCloser7 = substr($source, $lastCloser7[1] + strlen($lastCloser7[0]));
                    $unclosed7 = ((!$op['scored'] || $opUpper7) && trim($tailAfterCloser7) === '');
                }
                // REFCORR10 general rule: a nested list in a raw-case opener's
                // body supplies following content, so the outer list closes
                // even when its own would-be closer is the last non-space text.
                $hasNestedListTok = false;
                $d = preg_quote($this->wiki->delim, '/');
                if (preg_match_all('/' . $d . '(\d+)' . $d . '/', $body, $tmTok)) {
                    foreach ($tmTok[1] as $tokKey) {
                        $tk = isset($this->wiki->tokens[(int)$tokKey]) ? $this->wiki->tokens[(int)$tokKey] : null;
                        if ($tk !== null && $tk[0] === $this->rule && isset($tk[1]['type'])
                            && in_array($tk[1]['type'], array('explicit_list_start', 'bullet_list_start', 'number_list_start'), true)) {
                            $hasNestedListTok = true;
                            break;
                        }
                    }
                }
                if ($unclosed7 && (preg_match('/\[\[(?:ul|ol)(?:_)?(?:\s+[^\]]*)?\]\]/i', $body)
                        || $hasNestedListTok)) {
                    $unclosed7 = false;
                }
            }

            // REFCORR5 Batch 1: an uppercase opener's would-be closer is
            // swallowed into the last item rather than ending the list, and
            // the residual tail is absorbed there too (f06). Fold a run of
            // three or more newlines left by the removed closer to two, the
            // live shape of a swallowed closer followed by a paragraph.
            // REFCORR9 C-R5B-P1-1 / C-R5-S1-01: after a raw-case opener's first
            // closer fails to pair, a following raw-case [[LI]] is NOT a new
            // item on live. It stays literal inside the first item, the failed
            // closer is consumed, and the surviving final closer is literal;
            // the list is closed. The generic synthetic tail absorption below
            // pairs both LI markers and leaves the list unclosed, so emit the
            // one-item closed token sequence directly for this exact skeleton.
            // REFCORR12 R12-LIST GENERAL nested-list / trailing-prose rule.
            // REFCORR11 generalized the post-failed-close adjacency to tolerate
            // any intervening bytes, but it made two rule-level mistakes that
            // rounds 5e confirmed. First, it split the literal tail at the
            // surviving final block closer and appended everything after that
            // closer AFTER the list-end token; live keeps trailing prose INSIDE
            // the last item and hoists only a [[footnoteblock]] past the list.
            // Second, it kept a nested raw-case [[UL]]/[[OL]] opener inside the
            // first item's literal body; live flattens that nested opener into
            // sibling items. The single coherent generalization is: a raw-case
            // opener with a failed closer emits one list, in which a nested
            // raw-case block opener is an ITEM BOUNDARY (it closes the current
            // item and the next [[LI]] becomes a sibling), the item at the
            // failed closer absorbs the tail literally through the final
            // surviving closer plus all trailing prose, and only a
            // [[footnoteblock]] in that trailing material is emitted after the
            // list so its footer renders outside the list on live.
            if (!empty($matchedPair['synthetic'])
                && preg_match('/^\n\[\[li(?:\s+[^\]]*)?\]\](.*?)\[\[\/li\]\]\n\[\[\/(?:ul|ol)\]\](.*?\[\[li(?:\s+[^\]]*)?\]\].*)$/is', $body, $c1m)) {
                $pre12 = $c1m[1];
                $tail12 = $c1m[2];
                if (substr($tail12, 0, 1) === "\n") {
                    $tail12 = substr($tail12, 1);
                }
                $tail12 = rtrim($tail12);
                // REFCORR13 symmetric hoist rule: a [[footnoteblock]] marker
                // anywhere in the post-failed-closer tail is hoisted past the
                // list-end token, not only a marker that happens to sit after
                // the surviving final block closer. Scan the whole tail, split
                // at the first marker, then apply the final-closer split to the
                // bytes before it. By the time this rule runs the Footnoteblock
                // rule has tokenised the marker to a \xFF-number-\xFF
                // placeholder, so find it by token identity; a literal marker
                // (defensive) is honoured too. The bytes before the marker keep
                // their trailing LF: it is the Newline witness live emits as
                // <br />, so no rtrim is applied here (C-R5F-P1-2/-3).
                $insideAll12 = $tail12;
                $afterList12 = '';
                $hoistPos12 = null;
                $delim12 = preg_quote($this->wiki->delim, '/');
                if (preg_match_all('/' . $delim12 . '(\d+)' . $delim12 . '/', $tail12, $pm12, PREG_OFFSET_CAPTURE)) {
                    foreach ($pm12[1] as $pi => $tokId12) {
                        $tk12 = isset($this->wiki->tokens[(int)$tokId12[0]])
                            ? $this->wiki->tokens[(int)$tokId12[0]] : null;
                        if ($tk12 !== null && isset($tk12[0]) && $tk12[0] === 'Footnoteblock') {
                            $hoistPos12 = $pm12[0][$pi][1];
                            break;
                        }
                    }
                }
                if ($hoistPos12 === null) {
                    $fm12 = array();
                    if (preg_match('/\[\[footnoteblock\]\]/i', $tail12, $fm12, PREG_OFFSET_CAPTURE)) {
                        $hoistPos12 = $fm12[0][1];
                    }
                }
                if ($hoistPos12 !== null) {
                    $insideAll12 = substr($tail12, 0, $hoistPos12);
                    $afterList12 = substr($tail12, $hoistPos12);
                }
                $leftover12 = '';
                if (preg_match('/^(.*\[\[\/(?:ul|ol)\]\])(.*)$/is', $insideAll12, $lm12)) {
                    $literalTail12 = $lm12[1];
                    $leftover12 = $lm12[2];
                } else {
                    $literalTail12 = $insideAll12;
                }
                $insideProse12 = $leftover12;
                // When a nested raw-case opener was flattened, the C1 regex
                // matched the nested item's closer as its "failed" closer, so
                // the tail still begins with the redundant outer item closer
                // and the real failed outer block closer. Live consumes those
                // boundary tokens; strip a leading run of item/block closers
                // (and their surrounding whitespace) from the literal tail.
                // On a non-nested tail this prefix is empty, so the guard is
                // behaviour-neutral for every prior adjacency control.
                $literalTail12 = preg_replace(
                    '/^(?:\s*\[\[\/li\]\]|\s*\[\[\/(?:ul|ol)\]\])+\s*/i',
                    '',
                    $literalTail12
                );
                // A nested raw-case ul/ol opener or closer never opens a
                // nested list on live: it is absorbed into the item stream as
                // a boundary. Strip those tags, then split the pre-closer
                // region into sibling item bodies at every [[LI]] marker.
                $preFlat12 = preg_replace_callback(
                    '/\[\[(\/?)(ul|ol)(_)?(?:\s+[^\]]*)?\]\]/i',
                    function ($m) {
                        return ($m[2] === strtolower($m[2])) ? $m[0] : '';
                    },
                    $pre12
                );
                $segs12 = preg_split('/\[\[li(?:\s+[^\]]*)?\]\]/i', $preFlat12);
                foreach ($segs12 as $k => $seg12) {
                    $segs12[$k] = rtrim(preg_replace('/\[\[\/li\]\]/i', '', $seg12));
                }
                $absorbBody12 = array_pop($segs12) . $literalTail12 . $insideProse12;
                $start12 = $this->wiki->addToken($this->rule, array(
                    'type' => 'explicit_list_start',
                    'list_type' => $op['tag'],
                    'attrs' => array(),
                    'scored' => $op['scored'],
                ));
                $liStart12 = $this->wiki->addToken($this->rule, array(
                    'type' => 'explicit_item_start', 'attrs' => array(), 'lead' => '',
                ));
                $liEnd12 = $this->wiki->addToken($this->rule, array(
                    'type' => 'explicit_item_end', 'lead' => '',
                ));
                $end12 = $this->wiki->addToken($this->rule, array(
                    'type' => 'explicit_list_end',
                    'list_type' => $op['tag'], 'trail' => '', 'scored' => $op['scored'],
                ));
                $replacement = $start12;
                foreach ($segs12 as $seg12) {
                    $replacement .= $liStart12 . $seg12 . $liEnd12;
                }
                $replacement .= $liStart12 . $absorbBody12 . $liEnd12 . $end12 . $afterList12;
                $source = substr($source, 0, $op['start']) . $replacement . substr($source, $fullEnd);
                continue;
            }

            if (!empty($matchedPair['synthetic'])) {
                $body = preg_replace('/\[\[\/(?:ul|ol)\]\]/i', '', $body);
                $liClosePos = strripos($body, '[[/li]]');
                if ($liClosePos !== false) {
                    $liClose = substr($body, $liClosePos, 7);
                    $tail = substr($body, $liClosePos + 7);
                    // REFCORR7 C-SUSPECT4A-3: live concatenates the absorbed
                    // trailing text straight into the last item on an
                    // uppercase opener, with no intervening newline or <br />.
                    $trimmedTail = trim($tail);
                    if ($trimmedTail !== '' || ($opUpper7 && $op['scored'])) {
                        $tail = $trimmedTail;
                    }
                    $body = substr($body, 0, $liClosePos) . $tail . $liClose;
                }
            }

            $replacement = $this->buildExplicitListBlock(
                $op['tag'],
                $op['scored'],
                $opUpper7 ? '' : $op['attrs'],
                $body,
                $matchedPair['residualBracket'],
                $unclosed7,
                $synthetic7
            );

            if (!empty($matchedPair['closeUpper']) && $fullEnd < strlen($source)
                && substr($source, $fullEnd, 1) !== "\n") {
                // REFCORR7 C-SUSPECT4A-2: the line break that preceded a
                // cross-type uppercase closer survives as the separator
                // before the trailing text on live.
                $replacement .= "\n";
            }
            $source = substr($source, 0, $op['start']) . $replacement . substr($source, $fullEnd);
        }

        $source = $this->finalizeExplicitListBoundaries($source);
        $this->wiki->source = $source;
    }

    /**
     * Builds the token sequence for a single matched [[ul]]/[[ol]] block.
     */
    protected function buildExplicitListBlock($tag, $scored, $attrStr, $body, $residualBracket, $unclosed = false, $synthetic = false)
    {
        $attrs = $this->buildListAttrs($attrStr);

        $nestedMap = array();
        $nestedCounter = 0;
        foreach ($this->explicitBlocks as $sTok => $info) {
            $eTok = $info['end_tok'];
            $sPos = strpos($body, $sTok);
            if ($sPos !== false) {
                $ePos = strpos($body, $eTok, $sPos + strlen($sTok));
                if ($ePos !== false) {
                    $spanLen = ($ePos + strlen($eTok)) - $sPos;
                    $spanStr = substr($body, $sPos, $spanLen);
                    $ph = "\x02EXPLIST_" . ($nestedCounter++) . "\x03";
                    $nestedMap[$ph] = array(
                        'str'     => $spanStr,
                        'end_key' => $info['end_key'],
                    );
                    $body = substr($body, 0, $sPos) . $ph . substr($body, $sPos + $spanLen);
                    unset($this->explicitBlocks[$sTok]);
                }
            }
        }

        $nativeMap = array();
        $nativeCounter = 0;
        $body = $this->maskNativeListsInBody($body, $nativeMap, $nativeCounter);

        // REFCORR7 C-SUSPECT4A-1: a mixed/uppercase opener nested inside a
        // lowercase list is recognized but does not open a list on live; it
        // closes the current item, and its would-be closer plus the item's
        // now-redundant closer are swallowed, leaving the inner [[li]] items
        // as ordinary siblings of the outer list.
        $body = preg_replace_callback(
            '/\[\[((?:ul|ol))(_)?(?:\s+[^\]]*)?\]\](.*?)\[\[\/\1\]\](\s*\[\[\/li\]\])?/is',
            function ($m) {
                if ($m[1] === strtolower($m[1])) {
                    return $m[0];
                }
                return '[[/li]]' . $m[3];
            },
            $body
        );

        $liPattern = '/\[\[li(?:\s+([^\s\]][^\]]*))?\]\](.*?)\[\[\/li\]\](\])?/is'; // REFCORR5 Batch 1: [[LI]]..[[/LI]] items
        $hasLi = (preg_match($liPattern, $body) === 1);

        $trailAfterClose = $residualBracket ? "\n]" : '';

        if ($hasLi) {
            preg_match_all($liPattern, $body, $liMatches, PREG_SET_ORDER | PREG_OFFSET_CAPTURE);

            $items = array();
            $preNested = array();
            $cursor = 0;

            foreach ($liMatches as $lm) {
                $mStart = $lm[0][1];
                $mLen = strlen($lm[0][0]);
                $between = substr($body, $cursor, $mStart - $cursor);
                $cursor = $mStart + $mLen;

                if (preg_match_all('/\x02EXPLIST_\d+\x03/', $between, $bm)) {
                    foreach ($bm[0] as $ph) {
                        if (count($items) > 0) {
                            $items[count($items) - 1]['attached_nested'][] = $ph;
                        } else {
                            $preNested[] = $ph;
                        }
                    }
                }

                $liAttrStr = isset($lm[1][0]) ? $lm[1][0] : '';
                $liBody = $lm[2][0];
                $liResBracket = (isset($lm[3][0]) && $lm[3][0] === ']') ? ']' : '';
                $liBody .= $liResBracket;

                $items[] = array(
                    'attrs'           => $this->buildListAttrs($liAttrStr),
                    'body'            => $liBody,
                    'attached_nested' => array(),
                );
            }

            $tailBetween = substr($body, $cursor);
            if (preg_match_all('/\x02EXPLIST_\d+\x03/', $tailBetween, $bm)) {
                foreach ($bm[0] as $ph) {
                    if (count($items) > 0) {
                        $items[count($items) - 1]['attached_nested'][] = $ph;
                    } else {
                        $preNested[] = $ph;
                    }
                }
            }

            $emittedItems = '';

            foreach ($preNested as $ph) {
                $nInfo = $nestedMap[$ph];
                $this->wiki->tokens[$nInfo['end_key']][1]['trail'] = '';
                $wStart = $this->wiki->addToken($this->rule, array('type' => 'explicit_inline_wrapper_start', 'newline' => false));
                $wEnd = $this->wiki->addToken($this->rule, array('type' => 'explicit_inline_wrapper_end', 'newline' => false, 'lead_nl' => false));
                $emittedItems .= $wStart . $nInfo['str'] . $wEnd;
            }

            $survivingCount = 0;
            $siblingAfter = '';
            foreach ($items as $item) {
                // REFCORR10 general rule: an EMPTY item cannot hold a nested
                // list. Keep the empty item with one break and emit the
                // attached nested lists as siblings after this list closes.
                $nestedPhs = array();
                foreach (array_merge(array($item['body']), $item['attached_nested']) as $srcPart) {
                    if (preg_match_all('/\x02EXPLIST_\d+\x03/', $srcPart, $pm)) {
                        foreach ($pm[0] as $ph) {
                            $nestedPhs[] = $ph;
                        }
                    }
                }
                $bodyNoPh = preg_replace('/\s|\x02EXPLIST_\d+\x03/', '', $item['body']);
                if ($bodyNoPh === '' && count($nestedPhs) > 0) {
                    $emptyBr = $this->wiki->addToken($this->rule, array('type' => 'explicit_br_no_nl'));
                    $emptyLiStart = $this->wiki->addToken($this->rule, array('type' => 'explicit_item_start', 'attrs' => $item['attrs'], 'lead' => ''));
                    $emptyLiEnd = $unclosed ? '' : $this->wiki->addToken($this->rule, array('type' => 'explicit_item_end', 'lead' => ''));
                    $emittedItems .= $emptyLiStart . $emptyBr . $emptyLiEnd;
                    $survivingCount++;
                    foreach ($nestedPhs as $ph) {
                        $nInfo = $nestedMap[$ph];
                        $this->wiki->tokens[$nInfo['end_key']][1]['trail'] = "\n";
                        $siblingAfter .= $nInfo['str'];
                    }
                    continue;
                }
                $formatted = $this->formatExplicitLiItem($item, $nestedMap, $nativeMap, $unclosed, $scored);
                if ($formatted !== '') {
                    $emittedItems .= $formatted;
                    $survivingCount++;
                }
            }

            if ($survivingCount === 0 && count($preNested) === 0) {
                $emptyTok = $this->wiki->addToken($this->rule, array('type' => 'explicit_empty'));
                return "\x02EXPDISSOLVED\x03" . $emptyTok;
            }

            $startTok = $this->wiki->addToken($this->rule, array(
                'type'      => 'explicit_list_start',
                'list_type' => $tag,
                'attrs'     => $attrs,
                'scored'    => $scored,
            ));
            if ($unclosed) {
                // REFCORR7 C-SUSPECT4A-3: a mixed/uppercase opener at end of
                // source yields an unclosed list: no item/list end tokens and
                // no boundary follower, exactly the live truncated bytes.
                return $startTok . $emittedItems;
            }
            $endTok = $this->wiki->addToken($this->rule, array(
                'type'      => 'explicit_list_end',
                'list_type' => $tag,
                'trail'     => '',
                'scored'    => $scored,
            ));
            $endKey = $this->extractTokenKey($endTok);
            $this->explicitBlocks[$startTok] = array(
                'end_tok' => $endTok,
                'end_key' => $endKey,
                'scored'  => $scored,
                'synth'   => $synthetic,
            );

            $siblingTail = '';
            if ($siblingAfter !== '') {
                $siblingTail = $this->wiki->addToken($this->rule, array('type' => 'explicit_raw_nl')) . $siblingAfter . $this->wiki->addToken('Newline', array());
            }
            return $startTok . $emittedItems . $endTok . $trailAfterClose . $siblingTail;
        }

        $trimmedBody = trim($body);
        if ($trimmedBody === '') {
            $emptyTok = $this->wiki->addToken($this->rule, array('type' => 'explicit_empty'));
            return "\x02EXPDISSOLVED\x03" . $emptyTok;
        }

        $onlyListsCheck = preg_replace('/(?:\x02EXPLIST_\d+\x03|\x02NATLIST_\d+\x03|\s)+/', '', $trimmedBody);
        if ($onlyListsCheck === '') {
            preg_match_all('/\x02(?:EXPLIST|NATLIST)_\d+\x03/', $trimmedBody, $lm);
            $listPhs = $lm[0];
            $multi = (count($listPhs) > 1);

            $innerContent = '';
            foreach ($listPhs as $idx => $ph) {
                if (isset($nestedMap[$ph])) {
                    $nInfo = $nestedMap[$ph];
                    $this->wiki->tokens[$nInfo['end_key']][1]['trail'] = $multi ? "\n" : '';
                    $innerContent .= $nInfo['str'];
                } elseif (isset($nativeMap[$ph])) {
                    $natInfo = $nativeMap[$ph];
                    if ($multi && $idx > 0) {
                        $nlTok = $this->wiki->addToken($this->rule, array('type' => 'explicit_raw_nl'));
                        $innerContent .= $nlTok;
                    }
                    $innerContent .= $natInfo['str'];
                }
            }

            $wStart = $this->wiki->addToken($this->rule, array(
                'type'    => 'explicit_inline_wrapper_start',
                'newline' => $multi,
            ));
            $wEnd = $this->wiki->addToken($this->rule, array(
                'type'    => 'explicit_inline_wrapper_end',
                'newline' => $multi,
                'lead_nl' => $multi,
            ));

            $startTok = $this->wiki->addToken($this->rule, array(
                'type'      => 'explicit_list_start',
                'list_type' => $tag,
                'attrs'     => $attrs,
                'scored'    => $scored,
            ));
            $endTok = $this->wiki->addToken($this->rule, array(
                'type'      => 'explicit_list_end',
                'list_type' => $tag,
                'trail'     => '',
                'scored'    => $scored,
            ));
            $endKey = $this->extractTokenKey($endTok);
            $this->explicitBlocks[$startTok] = array(
                'end_tok' => $endTok,
                'end_key' => $endKey,
                'scored'  => $scored,
                'synth'   => $synthetic,
            );

            return $startTok . $wStart . $innerContent . $wEnd . $endTok . $trailAfterClose;
        }

        $restoredBody = $this->restorePlaceholders($trimmedBody, $nestedMap, $nativeMap);
        $noneStart = $this->wiki->addToken($this->rule, array('type' => 'explicit_none_item_start'));
        $noneEnd = $this->wiki->addToken($this->rule, array('type' => 'explicit_none_item_end'));

        $startTok = $this->wiki->addToken($this->rule, array(
            'type'      => 'explicit_list_start',
            'list_type' => $tag,
            'attrs'     => $attrs,
            'scored'    => $scored,
        ));
        $endTok = $this->wiki->addToken($this->rule, array(
            'type'      => 'explicit_list_end',
            'list_type' => $tag,
            'trail'     => '',
            'scored'    => $scored,
        ));
        $endKey = $this->extractTokenKey($endTok);
        $this->explicitBlocks[$startTok] = array(
            'end_tok' => $endTok,
            'end_key' => $endKey,
            'scored'  => $scored,
            'synth'   => $synthetic,
        );

        return $startTok . $noneStart . $restoredBody . $noneEnd . $endTok . $trailAfterClose;
    }

    /**
     * Formats a single [[li...]]...[[/li]] item and any sibling nested lists attached to it.
     */
    protected function formatExplicitLiItem($item, $nestedMap, $nativeMap, $unclosed = false, $scored = false)
    {
        $b = $item['body'];
        $b = preg_replace('/^[ \t]+|[ \t]+$/', '', $b);

        if (substr($b, 0, 1) === "\n") {
            $b = substr($b, 1);
            $b = preg_replace('/^[ \t]+/', '', $b);
        }

        // REFCORR9 C-R5B-P1-4: an uppercase opener's empty item carries exactly
        // one trailing break on live; a whitespace-only body must not also leave
        // a raw newline that the Newline rule turns into a second break.
        if ($b !== '' && trim($b) === '' && count($item['attached_nested']) === 0) {
            $b = $this->wiki->addToken($this->rule, array('type' => 'explicit_br_no_nl'));
        }
        if ($b === '' && count($item['attached_nested']) === 0) {
            // REFCORR10 general rule: an unclosed SCORED opener keeps an empty
            // item rather than dissolving the whole list. The scored flag
            // suppresses the trailing break, so the item is bare <li>.
            if (!($unclosed && $scored)) {
                return '';
            }
        }

        $leadAfterLiOpen = '';
        $leadBeforeLiClose = '';

        if (preg_match('/^\s*(\x02NATLIST_\d+\x03)\s*$/s', $b, $nm)) {
            $ph = $nm[1];
            $natInfo = $nativeMap[$ph];
            $leadAfterLiOpen = "\n";
            $leadBeforeLiClose = "\n";
            $b = $natInfo['str'];
        } elseif (preg_match('/^(.*?)\s*(\x02NATLIST_\d+\x03)\s*$/s', $b, $nm)) {
            $prefixText = trim($nm[1]);
            $ph = $nm[2];
            $natInfo = $nativeMap[$ph];
            $nlTok = $this->wiki->addToken($this->rule, array('type' => 'explicit_raw_nl'));
            $leadBeforeLiClose = "\n";
            $b = $prefixText . $nlTok . $natInfo['str'];
        } elseif (preg_match('/^(.*?)\n(\x02EXPLIST_\d+\x03)\s*$/s', $b, $em)) {
            $prefixText = $em[1];
            $ph = $em[2];
            $nInfo = $nestedMap[$ph];
            $this->wiki->tokens[$nInfo['end_key']][1]['trail'] = "\n";
            $brTok = $this->wiki->addToken('Newline', array());
            $b = $prefixText . $brTok . $nInfo['str'];
        } else {
            if (substr($b, -1) === "\n") {
                $b = substr($b, 0, -1);
                $b = preg_replace('/[ \t]+$/', '', $b);
                if ($b === '' && count($item['attached_nested']) === 0) {
                    return '';
                }
                $brNoNl = $this->wiki->addToken($this->rule, array('type' => 'explicit_br_no_nl'));
                $b .= $brNoNl;
            }
            $b = $this->restorePlaceholders($b, $nestedMap, $nativeMap);
        }

        if (count($item['attached_nested']) > 0) {
            foreach ($item['attached_nested'] as $ph) {
                $nInfo = $nestedMap[$ph];
                $this->wiki->tokens[$nInfo['end_key']][1]['trail'] = "\n";
                $nlTok = $this->wiki->addToken($this->rule, array('type' => 'explicit_raw_nl'));
                $b .= $nlTok . $nInfo['str'];
            }
        }

        $liStart = $this->wiki->addToken($this->rule, array(
            'type'  => 'explicit_item_start',
            'attrs' => $item['attrs'],
            'lead'  => $leadAfterLiOpen,
        ));
        $liEnd = $unclosed ? '' : $this->wiki->addToken($this->rule, array(
            'type' => 'explicit_item_end',
            'lead' => $leadBeforeLiClose,
        ));

        return $liStart . $b . $liEnd;
    }

    /**
     * Masks top-level native line-led lists (\n\n\xFFstart\xFF...\xFFend\xFF\n\n) inside $body.
     */
    protected function maskNativeListsInBody($body, &$nativeMap, &$nativeCounter)
    {
        $delim = $this->wiki->delim;
        $d = preg_quote($delim, '/');
        if (!preg_match_all('/' . $d . '(\d+)' . $d . '/', $body, $tms, PREG_SET_ORDER | PREG_OFFSET_CAPTURE)) {
            return $body;
        }

        $spans = array();
        $openStart = null;
        foreach ($tms as $tm) {
            $key = (int)$tm[1][0];
            $pos = $tm[0][1];
            $len = strlen($tm[0][0]);
            if (!isset($this->wiki->tokens[$key]) || $this->wiki->tokens[$key][0] !== $this->rule) {
                continue;
            }
            $opts = $this->wiki->tokens[$key][1];
            $t = isset($opts['type']) ? $opts['type'] : '';
            $lvl = isset($opts['level']) ? $opts['level'] : -1;
            if (($t === 'bullet_list_start' || $t === 'number_list_start') && $lvl === 0 && $openStart === null) {
                $openStart = array('pos' => $pos, 'key' => $key);
            } elseif (($t === 'bullet_list_end' || $t === 'number_list_end') && $lvl === 0 && $openStart !== null) {
                $spans[] = array(
                    'start_pos' => $openStart['pos'],
                    'end_pos'   => $pos + $len,
                    'start_key' => $openStart['key'],
                    'end_key'   => $key,
                );
                $openStart = null;
            }
        }

        if (count($spans) === 0) {
            return $body;
        }

        for ($i = count($spans) - 1; $i >= 0; $i--) {
            $sp = $spans[$i];
            $sPos = $sp['start_pos'];
            $ePos = $sp['end_pos'];
            $rawSpan = substr($body, $sPos, $ePos - $sPos);

            while ($sPos > 0 && $body[$sPos - 1] === "\n") {
                $sPos--;
            }
            while ($ePos < strlen($body) && $body[$ePos] === "\n") {
                $ePos++;
            }

            $ph = "\x02NATLIST_" . ($nativeCounter++) . "\x03";
            $nativeMap[$ph] = array(
                'str'       => $rawSpan,
                'start_key' => $sp['start_key'],
                'end_key'   => $sp['end_key'],
            );
            $body = substr($body, 0, $sPos) . "\n" . $ph . "\n" . substr($body, $ePos);
        }

        return $body;
    }

    /**
     * Restores masked nested explicit/native list placeholders in $str.
     */
    protected function restorePlaceholders($str, $nestedMap, $nativeMap)
    {
        foreach ($nestedMap as $ph => $info) {
            $str = str_replace($ph, $info['str'], $str);
        }
        foreach ($nativeMap as $ph => $info) {
            $str = str_replace($ph, $info['str'], $str);
        }
        return $str;
    }

    /**
     * Finalizes boundary newlines around top-level explicit list blocks in $source.
     */
    protected function finalizeExplicitListBoundaries($source)
    {
        $delim = $this->wiki->delim;
        $d = preg_quote($delim, '/');
        $source = preg_replace('/\x02EXPDISSOLVED\x03(' . $d . '\d+' . $d . ')\n?/', '$1', $source);

        foreach ($this->explicitBlocks as $sTok => $info) {
            $eTok = $info['end_tok'];
            $endKey = $info['end_key'];
            $scored = $info['scored'];

            $sPos = strpos($source, $sTok);
            if ($sPos === false) {
                continue;
            }
            $ePos = strpos($source, $eTok, $sPos + strlen($sTok));
            if ($ePos === false) {
                continue;
            }
            $afterEnd = $ePos + strlen($eTok);

            if ($sPos >= 2 && $source[$sPos - 1] === "\n" && $source[$sPos - 2] !== "\n") {
                $lineStart = strrpos(substr($source, 0, $sPos - 1), "\n");
                $lineStart = ($lineStart === false) ? 0 : $lineStart + 1;
                $prevLine = substr($source, $lineStart, ($sPos - 1) - $lineStart);
                if ($prevLine !== '' && strpos($prevLine, '||') === false && substr($prevLine, -1) !== $delim) {
                    $brTok = $this->wiki->addToken($this->rule, array('type' => 'explicit_br_no_nl'));
                    $source = substr($source, 0, $sPos - 1) . $brTok . "\n\n" . substr($source, $sPos);
                    $delta = strlen($brTok) + 1;
                    $sPos += $delta;
                    $ePos += $delta;
                    $afterEnd += $delta;
                }
            }

            $rest = substr($source, $afterEnd);

            if (preg_match('/^(\s*\[\[\/(?:h)?cell\]\]\s*\[\[\/row\]\]\s*\[\[\/table\]\])\n(?=[^\n])/i', $rest, $tm)) {
                $prefixLen = strlen($tm[1]);
                $source = substr($source, 0, $afterEnd + $prefixLen) . "\n\n" . substr($rest, $prefixLen + 1);
                continue;
            }

            if (preg_match('/^(\n+)(' . $d . '\d+' . $d . ')/', $rest, $rm)) {
                $nextTok = $rm[2];
                if (isset($this->explicitBlocks[$nextTok])) {
                    $source = substr($source, 0, $afterEnd) . substr($rest, strlen($rm[1]));
                    continue;
                }
            }

            if (preg_match('/^\n*$/', $rest)) {
                if (!$scored && empty($info['synth'])) {
                    $brTok = $this->wiki->addToken('Newline', array());
                    $source = substr($source, 0, $afterEnd) . $brTok . $rest;
                }
                continue;
            }

            if (substr($rest, 0, 1) === "\n" && substr($rest, 0, 2) !== "\n\n") {
                $nextChar = isset($rest[1]) ? $rest[1] : '';
                if ($nextChar !== '' && $nextChar !== $delim && substr($rest, 1, 3) !== '[[/') {
                    $this->wiki->tokens[$endKey][1]['trail'] = "\n";
                    $source = substr($source, 0, $afterEnd) . substr($rest, 1);
                    continue;
                }
            }

            // REFCORR3 C-SUSPECT-G15-1: after an explicit list and a blank
            // line, live emits the FIRST following prose run bare after a
            // <br />, not wrapped in <p>. The single-newline case above is
            // already bare on both sides; a blank line is not. Consume the
            // whole newline run, put explicit_br_no_nl plus explicit_raw_nl
            // tokens between the closer and the prose (so Paragraph never
            // forms a fresh plain-text match), and give the closer a trailing
            // newline. Scored token followers are left to the existing paths.
            if (preg_match('/^\n{2,}/', $rest, $nm)) {
                $nlLen = strlen($nm[0]);
                $nextChar = isset($rest[$nlLen]) ? $rest[$nlLen] : '';
                if ($nextChar !== '' && $nextChar !== $delim && substr($rest, $nlLen, 3) !== '[[/') {
                    $brTok = $this->wiki->addToken($this->rule, array('type' => 'explicit_br_no_nl'));
                    $nlTok = $this->wiki->addToken($this->rule, array('type' => 'explicit_raw_nl'));
                    $this->wiki->tokens[$endKey][1]['trail'] = "\n";
                    $source = substr($source, 0, $afterEnd) . $brTok . $nlTok . substr($rest, $nlLen);
                    continue;
                }
            }
        }

        return $source;
    }

    /**
     * Extracts integer token key from a delimited token string.
     */
    protected function extractTokenKey($tok)
    {
        $delim = $this->wiki->delim;
        return (int)trim($tok, $delim);
    }

    /**
     * Parses and normalizes attributes for [[ul]], [[ol]], and [[li]] per live
     * Wikidot's allowlist (probes muse-probe-refgaps-listblocks-p06 and p07).
     */
    protected function buildListAttrs($attrStr)
    {
        if (trim($attrStr) === '') {
            return array();
        }
        $rawAttrs = $this->getAttrs($attrStr);
        $fixed = array();
        $dataAttrs = array();
        $delim = $this->wiki->delim;

        foreach ($rawAttrs as $key => $rawVal) {
            if (!is_string($key)) {
                continue;
            }
            if ($key === 'id') {
                if ($rawVal === '' || strpos($rawVal, $delim) !== false) {
                    unset($fixed['id']);
                } else {
                    $norm = $this->normalizeAttrValue($rawVal);
                    if ($norm === '') {
                        $fixed['id'] = 'u-';
                    } elseif (strpos($norm, 'u-') === 0) {
                        $fixed['id'] = $norm;
                    } elseif (preg_match('/^[ \t\n\r]/', $rawVal)) {
                        $fixed['id'] = 'u- ' . $norm;
                    } else {
                        $fixed['id'] = 'u-' . $norm;
                    }
                }
                continue;
            }
            if ($key === 'class' || $key === 'style' || $key === 'role' || $key === 'type') {
                if ($rawVal === '') {
                    unset($fixed[$key]);
                } elseif (strpos($rawVal, $delim) !== false) {
                    $fixed[$key] = '';
                } else {
                    $fixed[$key] = $this->normalizeAttrValue($rawVal);
                }
                continue;
            }
            if (strpos($key, 'data-') === 0) {
                $dkey = strtolower($key);
                if (strpos($rawVal, $delim) !== false) {
                    $dataAttrs[$dkey] = '';
                } else {
                    $dataAttrs[$dkey] = $this->normalizeAttrValue($rawVal);
                }
                continue;
            }
        }

        $ordered = array();
        foreach (array('id', 'class', 'style', 'role', 'type') as $k) {
            if (isset($fixed[$k])) {
                $ordered[$k] = $fixed[$k];
            }
        }
        foreach ($dataAttrs as $k => $v) {
            $ordered[$k] = $v;
        }
        return $ordered;
    }

    /**
     * Normalizes an attribute value (strips C0 controls and DEL, collapses whitespace runs).
     */
    protected function normalizeAttrValue($val)
    {
        $clean = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/', '', $val);
        $clean = preg_replace('/[ \t\n\r]+/', ' ', $clean);
        return trim($clean, ' ');
    }
}
