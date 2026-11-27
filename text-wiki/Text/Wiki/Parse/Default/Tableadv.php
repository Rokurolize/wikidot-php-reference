<?php
/**
 *
 * Parses for advanced table.
 *
 * @category Text
 * @package Text_Wiki
 * @author Paul M. Jones <pmjones@php.net>
 * @author Michal Frackowiak
 * @license LGPL
 *
 */

/**
 * Advanced table block rule, corrected against live Wikidot behavior.
 *
 * An advanced table is a [[table ...]] block whose body is a run of
 * [[row ...]] blocks and each row's body is a run of [[cell ...]] or
 * [[hcell ...]] blocks. Whitespace between the blocks is discarded. A table
 * with no row, a row with no cell, or any non-row or non-cell text in those
 * bodies is not a table at all and stays literal. The closer name decides
 * whether a cell renders as a header cell, but only the exact lower-case
 * [[/hcell]] does: [[cell]]X[[/HCELL]] is a plain cell on live (REFCORR3
 * C-SUSPECT-LISTTABLE-2). Attribute heads tolerate a quoted ]] on a
 * table, while row and cell heads use the plain token grammar. Nested tables
 * are handled recursively before the enclosing rows and cells are split.
 *
 * REFCORR35: a terminal doubled quote in a table head (`style="a;""`) is
 * salvaged on live as a quoted value plus one literal quote inside that
 * value; it is not an unbalanced opener that may consume a quote from a
 * later block. The doubled-quote alternative is tried first so the head
 * ends at the real `]]`. REFCORR35 also keeps line breaks inside attribute
 * values as whitespace for normalizeValue() instead of deleting them as
 * control bytes: live serializes a newline in a style value as one space.
 */
class Text_Wiki_Parse_Tableadv extends Text_Wiki_Parse {

    public $regex = '~\[\[table((?:"[^"]*""|"[^"]*"|[^\]])*)\]\]((?:(?R)|.)*?)\[\[/table\]\]~si';

    // The Wikitext safe-attribute allowlist, lower-case names only at this
    // block level; data- names are allowed. aria- names and align are dropped
    // on live (REFCORR3 C-R45-2, C-R45-3).
    private $safeAttrs = array(
        'accept', 'alt', 'autocapitalize', 'autoplay', 'background',
        'bgcolor', 'border', 'buffered', 'checked', 'cite', 'class', 'cols',
        'colspan', 'contenteditable', 'controls', 'coords', 'datetime',
        'decoding', 'default', 'dir', 'dirname', 'disabled', 'download',
        'draggable', 'for', 'form', 'frameborder', 'headers', 'height',
        'hidden', 'high', 'href', 'hreflang', 'id', 'inputmode', 'ismap',
        'itemprop', 'kind', 'label', 'lang', 'list', 'loop', 'low', 'max',
        'maxlength', 'min', 'minlength', 'multiple', 'muted', 'name',
        'optimum', 'pattern', 'placeholder', 'poster', 'preload', 'readonly',
        'required', 'reversed', 'role', 'rows', 'rowspan', 'scope', 'selected',
        'shape', 'size', 'sizes', 'span', 'spellcheck', 'src', 'srclang',
        'start', 'step', 'style', 'tabindex', 'target', 'title', 'translate',
        'type', 'usemap', 'value', 'width', 'wrap'
    );

    function process($matches) {
        $head = $matches[1];
        $body = $matches[2];
        // REFCORR27 C1: comments are invisible to the advanced-table grammar.
        // Comment leaves an opaque empty token behind when the comment was the
        // only text on an indented line (so paragraph framing outside tables is
        // preserved). Inside a table body that placeholder is not row/cell
        // text on live: note-immortality-amulet has exactly such a comment
        // between two rows, and live parses the nested table while the token
        // made this rule reject the whole outer table as non-row text.
        $delim = preg_quote($this->wiki->delim, '/');
        $body = preg_replace_callback('/' . $delim . '([0-9]+)' . $delim . '/',
            function ($m) {
                $token = isset($this->wiki->tokens[(int)$m[1]])
                    ? $this->wiki->tokens[(int)$m[1]] : null;
                return ($token !== null && $token[0] === 'Comment') ? '' : $m[0];
            }, $body);
        // Nested tables are converted to opaque tokens before the enclosing
        // body is split into rows, so inner [[row]] and [[cell]] never leak
        // into the outer row or cell grammar.
        $body = $this->_scanTableadv($body, true);

        $rowRe = '~\[\[row([^\]]*)\]\](.*?)\[\[/row\]\]~si';
        preg_match_all($rowRe, $body, $rows, PREG_SET_ORDER | PREG_OFFSET_CAPTURE);
        if (count($rows) === 0) {
            return $matches[0];
        }
        $leadingRows = substr($body, 0, $rows[0][0][1]);
        $leadingRows = preg_replace('~\[\[table(?:"[^"]*""|"[^"]*"|[^\]])*\]\]~si', '', $leadingRows);
        if (trim($leadingRows) !== '') {
            return $matches[0];
        }

        $cellRe = '~\[\[(cell|hcell)([^\]]*)\]\](.*?)\[\[/(cell|hcell)\]\]~si';
        $rowsOut = '';
        $rowCursor = $rows[0][0][1];
        $hasInterRowContent = false;
        foreach ($rows as $row) {
            $gap = substr($body, $rowCursor, $row[0][1] - $rowCursor);
            $gap = $this->interRowContent($gap);
            if (trim($gap) !== '') {
                $rowsOut .= $gap;
                $hasInterRowContent = true;
            }
            preg_match_all($cellRe, $row[2][0], $cells, PREG_SET_ORDER);
            if (count($cells) === 0) {
                return $matches[0];
            }
            if (trim(preg_replace($cellRe, '', $row[2][0])) !== '') {
                return $matches[0];
            }
            $cellsOut = '';
            foreach ($cells as $cell) {
                // REFCORR3 C-SUSPECT-LISTTABLE-2: the opener grammar stays
                // case-insensitive, but header-ness comes only from the exact
                // lower-case closer. An upper-case [[/HCELL]] is a plain cell.
                $isHeader = ($cell[4] === 'hcell');
                $attrs = $this->buildAttrs($cell[2], 'cell');
                $content = $cell[3];
                // Keep paragraph boundaries when the authored body carries
                // a blank line, otherwise trim the cell body to its text.
                if (strpos($content, "\n\n") === false) {
                    $content = trim($content);
                } else {
                    $content = "\n\n" . trim($content) . "\n\n";
                }
                $cellsOut .= $this->wiki->addToken($this->rule, array(
                    'type' => 'cellStart', 'header' => $isHeader, 'attrs' => $attrs))
                    . $content
                    . $this->wiki->addToken($this->rule, array(
                        'type' => 'cellEnd', 'header' => $isHeader));
            }
            $rowAttrs = $this->buildAttrs($row[1][0], 'row');
            $rowsOut .= $this->wiki->addToken($this->rule, array(
                'type' => 'rowStart', 'attrs' => $rowAttrs))
                . $cellsOut
                . $this->wiki->addToken($this->rule, array('type' => 'rowEnd'));
            $rowCursor = $row[0][1] + strlen($row[0][0]);
        }
        $gap = substr($body, $rowCursor);
        if (trim($gap) !== '') {
            return $matches[0];
        }

        $tableAttrs = $this->buildAttrs($head, 'table');
        $startOpts = array('type' => 'start', 'attrs' => $tableAttrs);
        if ($hasInterRowContent) {
            $startOpts['foster_content'] = true;
        }
        $start = $this->wiki->addToken($this->rule, $startOpts);
        $end = $this->wiki->addToken($this->rule, array('type' => 'end'));
        return $start . $rowsOut . $end;
    }

    function parse() {
        // REFCORR22 R2 established the recursive expression as the behavioral
        // grammar: it backtracks inside ambiguous quoted table heads, pairing
        // the nested opener with the close inside the quoted text and leaving
        // the trailing quote/brackets in the outer cell. REFCORR24 removes the
        // 8192-byte split that sent larger inputs to the linear scanner, whose
        // first-nested-match head approximation left those same quoted-head
        // tables literal. Fresh live evidence (the muse-probe-tadv-thr-*
        // witnesses, stage sizes 8100..16000) shows Wikidot parses them at
        // every size, so the grammar must run at every size too.
        //
        // The only reason the grammar was withheld from large inputs was
        // PCRE JIT stack exhaustion (PREG_JIT_STACKLIMIT_ERROR), not a grammar
        // mismatch. The JIT compiler's fixed stack is the limiting resource;
        // the interpreted PCRE path honors the much larger
        // pcre.backtrack_limit / pcre.recursion_limit and completes the same
        // match. Disable JIT only for this call and restore it immediately, so
        // the grammar runs at corpus scale without changing global PCRE state.
        $oldJit = ini_get('pcre.jit');
        ini_set('pcre.jit', '0');
        // REFCORR-next framing: PREG_OFFSET_CAPTURE lets the callback see
        // where the match sits in the source, so processPreserveBoundary()
        // can reproduce the scanner's boundary-newline treatment. Without
        // the offset the callback only sees $matches[0] (which starts at
        // `[[table` and ends at `]]`), never the adjoining source newlines,
        // so the guard in processPreserveBoundary() was dead code and the
        // regex path dropped the scanner's blank line around a tokenized
        // table. That blank line is what makes the following spacer line a
        // new paragraph on live, rather than a <br /> inside the table's
        // paragraph. The grammar itself is unchanged.
        $replaced = preg_replace_callback(
            $this->regex,
            array(&$this, 'processPreserveBoundary'),
            $this->wiki->source,
            -1,
            $matchCount,
            PREG_OFFSET_CAPTURE
        );
        ini_set('pcre.jit', $oldJit);
        if ($replaced !== null) {
            $this->wiki->source = $replaced;
            return;
        }
        // Retain the linear scanner solely as a last-resort fallback if PCRE
        // itself reports an error even on the interpreted path.
        $this->wiki->source = $this->_scanTableadv($this->wiki->source);
    }

    /**
     * Keep the direct regex path byte-compatible with the scanner's
     * boundary-newline treatment. The scanner (_scanTableadv) adds one "\n"
     * before and after a replaced table when the source has one there;
     * that blank line is what lets the Paragraph rule close the paragraph
     * around a table and start a fresh one for an adjacent spacer line,
     * matching live. With PREG_OFFSET_CAPTURE the callback can see the
     * match offset in $this->wiki->source and reproduce exactly that, while
     * leaving the regex, process() and path selection untouched.
     */
    function processPreserveBoundary($matches)
    {
        $full = $matches[0][0];
        $offset = $matches[0][1];
        $plain = array();
        foreach ($matches as $k => $m) {
            $plain[$k] = $m[0];
        }
        $replacement = $this->process($plain);
        if ($replacement !== $full) {
            $src = $this->wiki->source;
            $n = strlen($src);
            if ($offset > 0 && $src[$offset - 1] === "\n") {
                $replacement = "\n" . $replacement;
            }
            $end = $offset + strlen($full);
            if ($end < $n && $src[$end] === "\n") {
                $replacement .= "\n";
            }
        }
        return $replacement;
    }

    /**
     * REFCORR16: linear-time scan replacing the whole-document recursive (?R) preg_replace_callback, whose PCRE JIT stack exhaustion silently wiped large documents (measured on real pages in the package 2.1 holdout). The public $regex remains the definitional pattern; the scanner reproduces the pattern's pairing semantics exactly, including PCRE's preference order at each body position (closer first, then a complete nested block, then one character) and its demotion backtrack: a nested block that leaves the enclosing block unclosable is demoted to literal text so the enclosing block can close at the nested block's closer.
     * process() applies the same scan to a table body for its nested
     * tables, as it applied the regex before.
     */
    private function _scanTableadv($src, $insideTable = false) {
        $n = strlen($src);
        $out = '';
        $last = 0;
        $pos = 0;
        $memo = array();
        while ($pos < $n) {
            $cand = stripos($src, '[[table', $pos);
            if ($cand === false) {
                break;
            }
            $m = $this->_tableadvBlock($src, $cand, $memo);
            if ($m === false) {
                $pos = $cand + 1;
                continue;
            }
            $out .= substr($src, $last, $cand - $last);
            $rep = $this->process($m[1]);
            if ($rep !== $m[1][0]) {
                // REFCORR37: inside an advanced-table cell an explicit-break
                // lead owns a paragraph boundary on live. Break consumed the
                // newline before this nested table, so restore the boundary
                // at the nested-table replacement point.
                if ($insideTable && $this->_precededByBreakToken($src, $cand)) {
                    $rep = "\n\n" . $rep;
                } elseif ($insideTable && $this->_precededByWhitespaceSeam($src, $cand)) {
                    $rep = $this->wiki->addToken('Break') . "\n\n" . $rep;
                } elseif ($cand > 0 && $src[$cand - 1] === "\n") {
                    $rep = "\n" . $rep;
                }
                $tailSpaces = preg_match('/\[\[\/table\]\]([ \t]*)$/i', $m[1][0], $tm) ? strlen($tm[1]) : 0;
                if ($insideTable && $tailSpaces > 0 && $this->_followedByWhitespaceSeam($src, $m[0], $tailSpaces)) {
                    $rep .= "\n\n" . $this->wiki->addToken('Break');
                } elseif ($m[0] < $n && $src[$m[0]] === "\n") {
                    $rep .= "\n";
                }
            }
            $out .= $rep;
            $last = $m[0];
            $pos = $m[0];
        }
        return $out . substr($src, $last);
    }

    private function _precededByWhitespaceSeam($src, $pos) {
        $i = $pos;
        $after = 0;
        while ($i > 0 && ($src[$i - 1] === ' ' || $src[$i - 1] === "\t")) {
            $i--;
            $after++;
        }
        if ($after === 0 || $i === 0 || $src[$i - 1] !== "\n") {
            return false;
        }
        $i--;
        $before = 0;
        while ($i > 0 && ($src[$i - 1] === ' ' || $src[$i - 1] === "\t")) {
            $i--;
            $before++;
        }
        return $before > 0 && $i > 0 && !ctype_space($src[$i - 1]);
    }

    private function _followedByWhitespaceSeam($src, $pos, $before = null) {
        $n = strlen($src);
        $i = $pos;
        if ($before === null) {
            $before = 0;
            while ($i < $n && ($src[$i] === ' ' || $src[$i] === "\t")) {
                $i++;
                $before++;
            }
        }
        if ($before === 0) {
            return false;
        }
        while ($i < $n && $src[$i] === "\xff" && preg_match('/\G\xff(\d+)\xff/A', $src, $m, 0, $i)) {
            $token = $this->wiki->tokens[(int)$m[1]] ?? null;
            if (!$token || $token[0] !== 'Comment') {
                break;
            }
            $i += strlen($m[0]);
        }
        if ($i >= $n || $src[$i] !== "\n") {
            return false;
        }
        $i++;
        $after = 0;
        while ($i < $n && ($src[$i] === ' ' || $src[$i] === "\t")) {
            $i++;
            $after++;
        }
        return $after > 0 && $i < $n && !ctype_space($src[$i]);
    }

    private function _precededByBreakToken($src, $pos) {
        $delim = $this->wiki->delim;
        if ($pos < 4 || $src[$pos - 1] !== $delim) {
            return false;
        }
        $start = strrpos(substr($src, 0, $pos - 1), $delim);
        if ($start === false) {
            return false;
        }
        $id = substr($src, $start + 1, $pos - $start - 2);
        if (!preg_match('/^[0-9]+$/', $id)) {
            return false;
        }
        $tok = isset($this->wiki->tokens[(int)$id])
            ? $this->wiki->tokens[(int)$id] : null;
        return $tok !== null && strtolower($tok[0]) === 'break';
    }

    private function _tableadvBlock($src, $p, &$memo) {
        $bk = 'b' . $p;
        if (array_key_exists($bk, $memo)) {
            return $memo[$bk];
        }
        if (!preg_match('/\G\[\[table((?:"[^"]*""|"[^"]*"|[^\]])*)\]\]/si', $src, $om, 0, $p)) {
            return $memo[$bk] = false;
        }
        $bodyStart = $p + strlen($om[0]);
        if (stripos($src, '[[/table]]', $bodyStart) === false) {
            return $memo[$bk] = false;
        }
        $c = $this->_tableadvBody($src, $bodyStart, $memo, $bodyStart);
        if ($c === false) {
            return $memo[$bk] = false;
        }
        $matches = array(substr($src, $p, $c[1] - $p), $om[1], substr($src, $bodyStart, $c[0] - $bodyStart));
        return $memo[$bk] = array($c[1], $matches);
    }

    private function _tableadvBody($src, $pos, &$memo, $bodyStart = null) {
        $sk = 's' . $pos;
        if (array_key_exists($sk, $memo)) {
            return $memo[$sk];
        }
        if (preg_match('/\G\[\[\/table\]\][ \t]*/i', $src, $cm, 0, $pos)) {
            return $memo[$sk] = array($pos, $pos + strlen($cm[0]));
        }
        // REFCORR35: when a nested opener is the first content of an enclosing
        // table body (only whitespace before it), live demotes that opener to
        // literal text and closes the enclosing table at the first available
        // closer. PCRE's recursive body and the old scanner instead consumed
        // that closer for the nested block and paired the outer with a later
        // table's closer, leaving consecutive tables literal. Only this
        // leading-opener shape is demoted; a nested table inside a row or
        // cell keeps its own closer and its normal nested structure.
        if ($bodyStart !== null && $pos === $bodyStart) {
            $nextTable = stripos($src, '[[table', $pos);
            if ($nextTable !== false
                && trim(substr($src, $bodyStart, $nextTable - $bodyStart)) === '') {
                $closer = stripos($src, '[[/table]]', $nextTable);
                if ($closer !== false) {
                    preg_match('/\G\[\[\/table\]\][ \t]*/i', $src, $cm, 0, $closer);
                    return $memo[$sk] = array($closer, $closer + strlen($cm[0]));
                }
            }
        }
        if (stripos($src, '[[table', $pos) === $pos) {
            $sub = $this->_tableadvBlock($src, $pos, $memo);
            if ($sub !== false) {
                $rest = $this->_tableadvBody($src, $sub[0], $memo);
                if ($rest !== false) {
                    return $memo[$sk] = $rest;
                }
            }
        }
        $next = strpos($src, '[[', $pos + 1);
        if ($next === false) {
            return $memo[$sk] = false;
        }
        return $memo[$sk] = $this->_tableadvBody($src, $next, $memo);
    }

    private function interRowContent($gap) {
        if (substr($gap, 0, 1) === "\n") {
            $gap = substr($gap, 1);
        }
        $gap = rtrim($gap, "\n");
        return $gap;
    }

    private function normalizeValue($value) {
        // REFCORR35: tab, LF and CR are whitespace to be collapsed to a
        // single space, not control bytes to delete. The live probe's
        // spacing-only shape serializes `padding: 0.5em;\nline-height:` as
        // `padding: 0.5em; line-height:`; deleting the newline produced the
        // no-space form. Other C0 bytes and DEL stay invisible as before.
        $value = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/', '', $value);
        $value = preg_replace('/\s+/u', ' ', $value);
        return trim($value);
    }

    private function isolateId($value) {
        if ($value === '') {
            return '';
        }
        $collapsed = $this->normalizeValue($value);
        if (strpos($value, 'u-') === 0) {
            return $collapsed;
        }
        $prefix = preg_match('/^\s/', $value) ? 'u- ' : 'u-';
        return $prefix . $collapsed;
    }

    private function isSafeAttr($key) {
        if (strpos($key, 'data-') === 0) {
            return true;
        }
        // REFCORR3 C-R45-2 / C-SUSPECT-LISTTABLE-8: live drops aria-*
        // attributes on advanced tables; the ftml ranking's "other" class
        // does not rescue them. No aria- branch here.
        return in_array($key, $this->safeAttrs, true);
    }

    private function buildAttrs($text, $owner) {
        $parsed = $this->getAttrs(trim($text));
        $attrs = array();
        foreach ($parsed as $key => $value) {
            // REFCORR8 C-R5-P3-2 folds a data-* key to lower case; REFCORR9
            // C-R5B-P3-2 admits `_` in the data-* key grammar, which the
            // general block-head grammar deliberately still rejects. REFCORR10
            // generalizes the folded data-* suffix to the live-observed key
            // class [a-z0-9._-]: lower-case letters, digits, underscore,
            // hyphen and dot. This is the union of every cached live key shape
            // (foo, 9foo, foo_, foo_bar-baz, foo.bar); the added dot byte is
            // the sole generalization demanded by C-R5C-P3-1. The recognised
            // prefix stays the exact lower-case `data-`, so an upper-case
            // DATA- prefix, aria-*, align and every other non-data key keep
            // their settled behavior, and the general advKeyOk class is not
            // widened.
            if (strpos($key, 'data-') === 0) {
                $key = strtolower($key);
                if (preg_match('/^data-[a-z0-9._-]*$/', $key) !== 1) {
                    continue;
                }
            } else if (preg_match('/^[a-z][a-z0-9-]*$/', $key) !== 1) {
                continue;
            }
            if (!$this->isSafeAttr($key) || $key === 'title' || $key === 'hidden') {
                continue;
            }
            if ($owner !== 'cell' && ($key === 'colspan' || $key === 'rowspan')) {
                continue;
            }
            if ($value === '') {
                continue;
            }
            if ($owner === 'cell'
                && ($key === 'colspan' || $key === 'rowspan')
                && $value === '0') {
                continue;
            }
            $normalized = $key === 'id'
                ? $this->normalizeValue($this->isolateId($value))
                : $this->normalizeValue($value);
            if ($normalized === ''
                && in_array($key, array('class', 'id', 'role', 'style', 'type'), true)) {
                continue;
            }
            $attrs[$key] = $normalized;
        }
        // REFCORR3 C-R45-1: live orders attributes by a fixed wikidot rank
        // (id, class, style, role, type, then data-* in authored order, then
        // the remaining attributes in authored order), not by name. The
        // fossil's ksort put colspan before data-name; MEASURE-TABLE showed
        // ftml already emits live's raw order. uksort is stable in PHP 8,
        // so equal-ranked keys keep their authored order.
        $rank = function ($key) {
            $named = array('id' => 0, 'class' => 1, 'style' => 2,
                'role' => 3, 'type' => 4);
            if (isset($named[$key])) {
                return $named[$key];
            }
            return strpos($key, 'data-') === 0 ? 5 : 6;
        };
        uksort($attrs, function ($a, $b) use ($rank) {
            $ra = $rank($a);
            $rb = $rank($b);
            return $ra === $rb ? 0 : ($ra < $rb ? -1 : 1);
        });
        return $attrs;
    }
}
