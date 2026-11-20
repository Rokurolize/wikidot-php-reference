<?php

/**
*
* Includes the contents of another PHP script into the source text.
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
* This class implements a Text_Wiki_Parse to include the results of a
* script directly into the source at parse-time; thus, the output of the
* script will be parsed by Text_Wiki.  This differs from the 'embed'
* rule, which incorporates the results at render-time, meaning that the
* 'embed' content is not parsed by Text_Wiki.
*
* DANGER!
*
* This rule is inherently not secure; it allows cross-site scripting to
* occur if the embedded output has <script> or other similar tags.  Be
* careful.
*
* @category Text
*
* @package Text_Wiki
*
* @author Paul M. Jones <pmjones@php.net>
*
* R2 REWRITE (2026-11-20, coordinator): the fossil's single regex
* scanner is replaced by a hand scanner implementing the
* live-adjudicated include grammar (GRAMMAR-INCLUDE.md rules
* S1-S5, G1-G5, Q1-Q3, F1-F2, X1-X4; correction classes C2, C3
* and C5 of conformance-refphp/R2-INCLUDE.md). Kept from the
* fossil: the substitution fold (str_replace per argument, in
* source order; already live-exact), the fetch through
* DB_PagePeer::selectByName on the current site, the
* missing-page error block, the "\n\n" splice padding, the
* inclusions bookkeeping, and the 5-pass recursion loop.
* C4 added 2026-11-20: the resolution layer (GRAMMAR R1-R5 as
* corrected by L6) in refResolveRef/refNormalize below, with
* cross-site fetch through the stub's selectBySiteAndName.
* refNormalize is exact for ASCII; non-ASCII input is bounded
* (this PHP has no intl or mbstring: no NFKC, ASCII-only case
* fold), the same fragment bound as the G1.4 Lean driver.
* Still open: the current live missing-page message text
* (class M update).
*/

class Text_Wiki_Parse_Include extends Text_Wiki_Parse {

    public $conf = array(
        'base' => '/path/to/scripts/'
    );

    public $file = null;

    public $output = null;

    public $vars = null;

    public $regex = '/^\[\[include ([a-zA-Z0-9\s\-:]+?)(\s+.*?)?(?:\]\])$/ims';

    function parse(){
        $level = 0;
        do{
            $oldSource = $this->wiki->source;
            $this->wiki->source = $this->refExpandPass($oldSource);
            $level++;
        }while($oldSource != $this->wiki->source && $level<5);
    }

    // One expansion pass over $src (ftml include() is also one
    // pass; the fossil recursion loop above re-runs passes).
    function refExpandPass($src)
    {
        $len = strlen($src);
        $out = '';
        $pos = 0;
        while (true) {
            $cand = $this->refFindCandidate($src, $pos);
            if ($cand === null) {
                $out .= substr($src, $pos);
                break;
            }
            list($ls, $plen, $depth, $matchEnd) = $cand;
            $candEnd = $this->refFindIncludeEnd($src, $matchEnd);
            if ($candEnd === null) {
                // S5: no terminator, the rest is untouched.
                $out .= substr($src, $pos);
                break;
            }
            if ($depth > 0) {
                $consumed = $this->refQuotedAttempt($src, $ls, $depth, $candEnd);
                if ($consumed !== null) {
                    // Q2: consumed and deleted, never fetched.
                    $out .= substr($src, $pos, $ls - $pos);
                    $pos = $consumed;
                    continue;
                }
                // Q3: the fallback is the unquoted parse from the
                // LINE START, which the '>' prefix makes fail; the
                // candidate is literal and scanning resumes at
                // the candidate end (grid q-broken-continuation).
                $out .= substr($src, $pos, $candEnd - $pos);
                $pos = $candEnd;
                continue;
            }
            $block = $this->refParseBlock(substr($src, $matchEnd));
            if ($block === null) {
                // F1: literal text, resume at the candidate end.
                $out .= substr($src, $pos, $candEnd - $pos);
                $pos = $candEnd;
                continue;
            }
            list($blockEndRel, $refRun, $args) = $block;
            $blockEnd = $matchEnd + $blockEndRel;
            $resolved = $this->refResolveRef($refRun);
            if ($resolved === null) {
                // Resolution failure (empty page after split
                // and normalization): the block stays literal.
                $out .= substr($src, $pos, $candEnd - $pos);
                $pos = $candEnd;
                continue;
            }
            $out .= substr($src, $pos, $ls - $pos);
            $out .= $this->refFetch($resolved, $args);
            $pos = $blockEnd;
        }
        return $out;
    }

    // Find the next candidate at or after $from. Returns
    // array(lineStart, prefixLen, depth, matchEnd) or null.
    // S1/S2: line starts only, tight [[include, case-insensitive,
    // and at least one regex-whitespace char after "include".
    function refFindCandidate($src, $from)
    {
        $len = strlen($src);
        $ls = $from;
        while ($ls <= $len) {
            // lead run: blanks and '>' only
            $i = $ls;
            $depth = 0;
            $lastGt = -1;
            while ($i < $len && ($src[$i] === ' ' || $src[$i] === "\t" || $src[$i] === '>')) {
                if ($src[$i] === '>') {
                    $depth++;
                    $lastGt = $i - $ls;
                }
                $i++;
            }
            $plen = ($depth > 0) ? $lastGt + 1 : 0;
            $at = $ls + $plen;
            if ($at + 9 <= $len
                && substr_compare($src, '[[include', $at, 9, true) === 0
                && $at + 9 < $len
                && strpos(" \t\n\r\x0B\x0C", $src[$at + 9]) !== false) {
                return array($ls, $plen, $depth, $at + 9);
            }
            $nl = strpos($src, "\n", $ls);
            if ($nl === false) {
                return null;
            }
            $ls = $nl + 1;
        }
        return null;
    }

    // S4: the first ]] at or after $from that is followed by a
    // newline or by end of input. Returns the offset just after
    // the ]], or null.
    function refFindIncludeEnd($src, $from)
    {
        $len = strlen($src);
        $i = $from;
        while (($j = strpos($src, ']]', $i)) !== false) {
            $after = $j + 2;
            if ($after >= $len || $src[$after] === "\n") {
                return $after;
            }
            $i = $j + 1;
        }
        return null;
    }

    // Q1: try the quoted strategies (candidate-end bound, then
    // whole-region bound). On success returns the original offset
    // just after the consumed range; null on failure.
    function refQuotedAttempt($src, $ls, $depth, $candEnd)
    {
        $bounds = array($candEnd, strlen($src));
        foreach ($bounds as $bound) {
            $region = substr($src, $ls, $bound - $ls);
            $lines = explode("\n", $region);
            $stripped = array();
            $normLines = array();
            $ok = true;
            foreach ($lines as $line) {
                $s = $this->refStripQuotePrefix($line, $depth);
                if ($s === null) {
                    $ok = false;
                    break;
                }
                $stripped[] = $s[0];
                $normLines[] = $s[1];
            }
            if (!$ok) {
                continue;
            }
            $norm = implode("\n", $normLines);
            // The normalized text starts with the opener.
            if (strlen($norm) < 9 || substr_compare($norm, '[[include', 0, 9, true) !== 0) {
                continue;
            }
            $block = $this->refParseBlock(substr($norm, 9));
            if ($block === null) {
                continue;
            }
            $normEnd = 9 + $block[0];
            return $ls + $this->refOrigOffset($lines, $stripped, $normEnd);
        }
        return null;
    }

    // Strip one line's quote prefix (depth '>' markers, blanks
    // allowed around each). Returns array(charsStripped, rest)
    // or null when the line does not carry the prefix.
    function refStripQuotePrefix($line, $depth)
    {
        $i = 0;
        $len = strlen($line);
        for ($k = 0; $k < $depth; $k++) {
            while ($i < $len && ($line[$i] === ' ' || $line[$i] === "\t")) {
                $i++;
            }
            if ($i >= $len || $line[$i] !== '>') {
                return null;
            }
            $i++;
        }
        while ($i < $len && ($line[$i] === ' ' || $line[$i] === "\t")) {
            $i++;
        }
        return array($i, substr($line, $i));
    }

    // Map an offset in the normalized (prefix-stripped) text back
    // to an offset in the original region.
    function refOrigOffset($lines, $stripped, $normOff)
    {
        $acc = 0;
        $origAcc = 0;
        $n = count($lines);
        for ($j = 0; $j < $n; $j++) {
            $normLen = strlen($lines[$j]) - $stripped[$j];
            if ($normOff <= $acc + $normLen) {
                return $origAcc + $stripped[$j] + ($normOff - $acc);
            }
            $acc += $normLen + 1;
            $origAcc += strlen($lines[$j]) + 1;
        }
        return $origAcc;
    }

    // Parse a block body starting just after "[[include".
    // Returns array(endOffsetRelative, refRun, args) or null.
    // G1-G5 plus the C5 disposition (leading-colon refs are
    // resolved by the fetch layer, not rejected here).
    function refParseBlock($text)
    {
        $len = strlen($text);
        $i = 0;
        // whitespace after include: the GRAMMAR set (space,
        // newline, tab), narrower than the scanner's regex \s+
        // (grid cr-after: a lone \r here fails the block)
        $ws = 0;
        while ($i < $len && strpos(" \t\n", $text[$i]) !== false) {
            $i++;
            $ws++;
        }
        if ($ws === 0) {
            return null;
        }
        // page_ref run (G2 page chars)
        $refStart = $i;
        while ($i < $len && strpos(" \t\n[|]\"'", $text[$i]) === false) {
            $i++;
        }
        $refRun = substr($text, $refStart, $i - $refStart);
        if ($refRun === '') {
            return null;
        }
        // block end (G1): first ]] followed by a grammar
        // newline (\n, \r\n, or a lone \r) or by end of text;
        // wider than the scanner's candidate end (S4)
        $end = null;
        for ($j = $i; ($k = strpos($text, ']]', $j)) !== false; $j = $k + 1) {
            $after = $k + 2;
            if ($after >= $len || $text[$after] === "\n" || $text[$after] === "\r") {
                $end = $k;
                break;
            }
        }
        if ($end === null) {
            return null;
        }
        if ($i === $end) {
            return array($end + 2, $refRun, array());
        }
        // whitespace before the tail is required (a tight pipe
        // fails the block, per the grammar)
        $ws = 0;
        while ($i < $end && strpos(" \t\n", $text[$i]) !== false) {
            $i++;
            $ws++;
        }
        if ($ws === 0) {
            return null;
        }
        // G3: stray open brackets (a '[' run not starting a
        // comment), plus one optional space
        if ($i < $end && $text[$i] === '[' && substr($text, $i, 4) !== '[!--') {
            while ($i < $end && $text[$i] === '[') {
                $i++;
            }
            if ($i < $end && $text[$i] === ' ') {
                $i++;
            }
        }
        $tail = substr($text, $i, $end - $i);
        $args = $this->refSegments($tail);
        if ($args === null) {
            return null;
        }
        return array($end + 2, $refRun, $args);
    }

    // G4/G5: comment-aware segment split, then the segment rule.
    // Returns the ordered argument list (the X1 fold input), or
    // null when an unterminated comment fails the whole block.
    function refSegments($tail)
    {
        $segments = array();
        $cur = '';
        $len = strlen($tail);
        $i = 0;
        while ($i < $len) {
            if (substr($tail, $i, 4) === '[!--') {
                $close = strpos($tail, '--]', $i + 4);
                if ($close === false) {
                    return null;
                }
                $cur .= substr($tail, $i, $close + 3 - $i);
                $i = $close + 3;
                continue;
            }
            if ($tail[$i] === '|') {
                $segments[] = $cur;
                $cur = '';
                $i++;
                continue;
            }
            $cur .= $tail[$i];
            $i++;
        }
        $segments[] = $cur;
        $args = array();
        foreach ($segments as $seg) {
            $arg = $this->refSegmentArg($seg);
            if ($arg !== null) {
                $args[] = $arg;
            }
        }
        return $args;
    }

    // One segment: key = value with a static-identifier key and
    // a non-empty value (the PHP trim set at both ends), else
    // inert (null).
    function refSegmentArg($seg)
    {
        $src = ltrim($seg, " \t\n\r\0\x0B");
        if (!preg_match('/^[A-Za-z0-9\-_]+/', $src, $m)) {
            return null;
        }
        $key = $m[0];
        $after = ltrim(substr($src, strlen($key)), " \t\n\r\0\x0B");
        if ($after === '' || $after[0] !== '=') {
            return null;
        }
        $value = ltrim(substr($after, 1), " \t\n\r\0\x0B");
        $value = rtrim($value, " \t\n\r\0\x0B");
        if ($value === '') {
            return null;
        }
        return array($key, $value);
    }

    // Fetch and substitute (the fossil body, with the fold fed
    // by the ordered argument list). Returns the replacement
    // text with the fossil's "\n\n" padding (class P).
    function refFetch($resolved, $args)
    {
        list($siteName, $pageName) = $resolved;
        $display = ($siteName !== null) ? ':'.$siteName.':'.$pageName : $pageName;

        if ($siteName !== null) {
            $page = DB_PagePeer::instance()->selectBySiteAndName($siteName, $pageName);
        } else {
            $runData = Ozone::getRunData();
            $site = $runData->getTemp("site");
            $page = DB_PagePeer::instance()->selectByName($site->getSiteId(), $pageName);
        }

        if ($page == null) {
            $output = "\n\n".'[[div class="error-block"]]'."\n".sprintf(_('Page to be included %s can not be found!'), htmlspecialchars($pageName))."\n".'[[/div]]'."\n\n";
            $wiki = $this->wiki;
            if (empty($wiki->vars['inclusionsNotExist'])) {
                $wiki->vars['inclusionsNotExist'] = array();
            }
            $wiki->vars['inclusionsNotExist'][$display] = $display;
            return $output;
        }

        $output = $page->getSource();
        $wiki = $this->wiki;
        if (empty($wiki->vars['inclusions'])) {
            $wiki->vars['inclusions'] = array();
        }
        $wiki->vars['inclusions'][$page->getPageId()] = $page->getPageId();

        // The fold (X1-X4): raw values, source order, every
        // occurrence of the literal placeholder.
        foreach ($args as $arg) {
            $output = str_replace('{$'.$arg[0].'}', $arg[1], $output);
        }
        return "\n\n".$output."\n\n";
    }

    // The resolution layer (GRAMMAR R1-R5, with the L6 live
    // correction as completed by the C6 round, probe batches
    // C5-C5g). Returns array(siteOrNull, page), or null when
    // the include does not fire (the block then stays
    // literal). The live rule, as probed:
    // (1) A well-formed site pair (':' site ':' page, site
    //     non-empty, page part non-empty after the extra
    //     split) resolves cross-site; the site segment may
    //     be a dotted host, canonicalized per R3. This
    //     branch is unchanged from the C4 implementation.
    // (2) Any other run resolves as a page name ONLY if the
    //     whole run consists of [A-Za-z0-9\-_:]; a run
    //     containing any other character ('.', '/', '#',
    //     '+', '~', ...) does not fire at all. There is no
    //     extra split on this path: '#' and '/' block the
    //     include rather than splitting (C5g).
    // (3) On the page-name path the normalized result may
    //     be empty (':', ':::', '---', ':-'): the include
    //     still fires and the fetch misses, so the empty
    //     name proceeds to refFetch (C5c/C5d/C5e).
    function refResolveRef($run)
    {
        $s = trim($run);
        if ($s === '') {
            return null;
        }
        if ($s[0] === ':') {
            $idx = strpos($s, ':', 1);
            if ($idx !== false && $idx > 1) {
                $pagePart = substr($s, $idx + 1);
                // C5h: the pair's page part is gated on the
                // same charset as the page-name path. A '#'
                // or '/' in it does not split; it kills the
                // pair (and the gated fallback below then
                // leaves the block literal), including for
                // same-site pairs.
                if ($pagePart !== ''
                    && preg_match('/^[A-Za-z0-9\-_:]+$/', $pagePart)) {
                    $site = $this->refNormalize(
                        $this->refCanonicalSite(substr($s, 1, $idx - 1)));
                    $page = $this->refNormalize($pagePart);
                    if ($page === '') {
                        return null;
                    }
                    return array($site, $page);
                }
            }
        }
        if (!preg_match('/^[A-Za-z0-9\-_:]+$/', $s)) {
            return null;
        }
        return array(null, $this->refNormalize($s));
    }

    // R2: split at the first '#' or '/'; the remainder is an
    // extra that never reaches the fetch.
    function refSplitPage($p)
    {
        $cut = strlen($p);
        foreach (array('#', '/') as $ch) {
            $at = strpos($p, $ch);
            if ($at !== false && $at < $cut) {
                $cut = $at;
            }
        }
        return substr($p, 0, $cut);
    }

    // R3: canonical_include_site. One trailing dot is stripped
    // for the test; a <slug>.wikidot.com host (case-insensitive
    // suffix, slug of [A-Za-z0-9-]+) canonicalizes to the slug
    // with its case preserved; anything else is returned as-is.
    function refCanonicalSite($raw)
    {
        $t = trim($raw);
        if ($t !== '' && $t[strlen($t) - 1] === '.') {
            $t = substr($t, 0, -1);
        }
        if (preg_match('/^([A-Za-z0-9-]+)\.wikidot\.com$/i', $t, $m)) {
            return $m[1];
        }
        return $raw;
    }

    // R4: wikidot-normalize, step order as in the crate. Exact
    // for ASCII; non-ASCII case folding is ASCII-only here and
    // NFKC is unavailable (no intl), the recorded bound.
    function refNormalize($s)
    {
        $s = trim($s);
        if ($s !== '' && $s[0] === '/') {
            $s = substr($s, 1);
        }
        $s = strtolower($s);
        $s = preg_replace('/[^\p{L}\p{N} :\-_]/u', '-', $s);
        // merge every colon except the last into a dash
        $last = strrpos($s, ':');
        if ($last !== false) {
            $s = str_replace(':', '-', substr($s, 0, $last)) . substr($s, $last);
        }
        // underscores: one at index > 0 whose previous char is
        // not ':' becomes a dash
        $out = '';
        $chars = preg_split('//u', $s, -1, PREG_SPLIT_NO_EMPTY);
        foreach ($chars as $i => $c) {
            if ($c === '_' && $i > 0 && $chars[$i - 1] !== ':') {
                $out .= '-';
            } else {
                $out .= $c;
            }
        }
        $s = $out;
        $s = preg_replace('/^-+/', '', $s);
        $s = preg_replace('/-+$/', '', $s);
        $s = preg_replace('/-+/', '-', $s);
        $s = preg_replace('/:+/', ':', $s);
        do {
            $prev = $s;
            $s = str_replace(array(':-', '-:'), ':', $s);
        } while ($s !== $prev);
        do {
            $prev = $s;
            $s = str_replace(array('_-', '-_'), '_', $s);
        } while ($s !== $prev);
        $s = trim($s, ':');
        if (substr($s, 0, 9) === '_default:') {
            $s = substr($s, 9);
        }
        return $s;
    }
}
