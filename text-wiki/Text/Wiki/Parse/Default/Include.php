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
* G13 CORRECTION (2026-11-21, AUDIT-G13): the quoted
* consumption path (the Q1-Q3 mechanics above) is REMOVED.
* A quote-prefixed candidate is not a candidate at all; the
* scanner skips the line (live never consumes a quoted
* include; the reference was the last artifact still
* deleting tight quoted includes, including inside
* [[code]]; finding F-G14-1). The resolution layer gains
* the site-segment host gate (AUDIT-G13 site probes: the
* pair fires only when the site segment consists of
* [A-Za-z0-9.-]; '_' is excluded by probe
* muse-probe-g13fix-site-underscore, whose run falls back
* to whole-run page resolution), the site is no longer
* passed through slug normalization (canonicalization is
* R3 only; probe muse-probe-g13fix-site-upper names the
* site "FOO" verbatim), and a pair whose page part
* normalizes to empty now fires with the empty name
* (probe muse-probe-audit-g13-site-empty-page-norm,
* closing the C7 note in GRAMMAR-INCLUDE L6). F1
* resumption is corrected: on block-parse or resolution
* failure, scanning resumes at the next line start after
* the failed candidate's opener line, not at the
* candidate end (probe
* muse-probe-audit-g13-f1-bad-next-good). The
* pre-correction file is kept beside this one as
* Include.php.before-g13fix.php.
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
            $block = $this->refParseBlock(substr($src, $matchEnd));
            if ($block === null) {
                // F1 (corrected 2026-11-21): the failed
                // candidate stays literal; scanning resumes
                // at the next line start after the failed
                // candidate's opener line, so an include
                // beginning on an intervening line is still
                // found (probe
                // muse-probe-audit-g13-f1-bad-next-good).
                $resume = $this->refNextLineStart($src, $ls);
                $out .= substr($src, $pos, $resume - $pos);
                $pos = $resume;
                continue;
            }
            list($blockEndRel, $refRun, $args) = $block;
            $blockEnd = $matchEnd + $blockEndRel;
            $resolved = $this->refResolveRef($refRun);
            if ($resolved === null) {
                // Resolution failure (a charset gate): the
                // block stays literal; F1 resumption as
                // above.
                $resume = $this->refNextLineStart($src, $ls);
                $out .= substr($src, $pos, $resume - $pos);
                $pos = $resume;
                continue;
            }
            $out .= substr($src, $pos, $ls - $pos);
            $out .= $this->refFetch($resolved, $args);
            $pos = $blockEnd;
        }
        return $out;
    }

    // The offset of the first line start strictly after the
    // line containing $ls (F1 resumption); strlen($src) when
    // no newline remains.
    function refNextLineStart($src, $ls)
    {
        $nl = strpos($src, "\n", $ls);
        return ($nl === false) ? strlen($src) : $nl + 1;
    }

    // Find the next candidate at or after $from. Returns
    // array(lineStart, prefixLen, depth, matchEnd) or null.
    // S1/S2: line starts only, tight [[include, case-insensitive,
    // and at least one regex-whitespace char after "include".
    // G13: a line whose lead run contains a '>' (a quoted
    // line) is never a candidate; it is skipped whole (live
    // keeps quoted includes literal; F-G14-1), so the depth
    // of a returned candidate is always 0.
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
            if ($depth > 0) {
                $nl = strpos($src, "\n", $ls);
                if ($nl === false) {
                    return null;
                }
                $ls = $nl + 1;
                continue;
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
        return array($end + 2, $refRun, $args);
    }

    // G4/G5 (corrected 2026-11-21): raw segment split, then the
    // segment rule. Live's segment scanning is comment-unaware:
    // segments split on raw '|' bytes, '[!-- ... --]' bytes are
    // ordinary value bytes, and an unterminated comment is
    // ordinary text that cannot fail the block (AUDIT probes
    // muse-probe-audit-g14b-cmt-pipe and -cmt-unclosed; the
    // earlier comment-aware split modelled ftml's parse.rs
    // scan_include_arguments and was refuted by those probes).
    // Returns the ordered argument list (the X1 fold input);
    // never null.
    function refSegments($tail)
    {
        $segments = explode('|', $tail);
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
            $createHref = ($siteName != null) ? 'https://' . $siteName . '.wikidot.com/' . $pageName . '/edit/true' : '/' . $pageName . '/edit/true';
            $output = "\n\n".'[[div class="error-block"]]'."\n".sprintf(_('Included page "%s" does not exist ([%s create it now])'), htmlspecialchars($pageName), $createHref)."\n".'[[/div]]'."\n\n";
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
    //     be a dotted host, canonicalized per R3. G13
    //     (2026-11-21) corrects this branch in three ways:
    //     the site segment is gated on the host charset
    //     [A-Za-z0-9.-] (a run failing the gate falls
    //     through to the page-name rule below); the site
    //     passes through R3 canonicalization only, never
    //     slug normalization; and a page part normalizing
    //     to empty fires with the empty name instead of
    //     failing the block.
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
                    $siteSeg = substr($s, 1, $idx - 1);
                    // G13 site gate: AUDIT-G13 probes show a
                    // site run containing '/', '#', or a
                    // non-ASCII character never fires as a
                    // pair (the source stays literal), and
                    // probe muse-probe-g13fix-site-underscore
                    // shows '_' is outside the host set too
                    // (its run falls back to whole-run page
                    // resolution). A run failing the gate
                    // falls through to the page-name rule.
                    if (preg_match('/^[A-Za-z0-9.\-]+$/', $siteSeg)) {
                        // G13: R3 canonicalization only; the
                        // site is never slug-normalized
                        // (probe muse-probe-g13fix-site-upper
                        // names the site "FOO" verbatim), and
                        // a page part normalizing to empty
                        // fires with the empty name (probe
                        // muse-probe-audit-g13-site-empty-
                        // page-norm).
                        return array(
                            $this->refCanonicalSite($siteSeg),
                            $this->refNormalize($pagePart));
                    }
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
