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
 */
class Text_Wiki_Parse_Tableadv extends Text_Wiki_Parse {

    public $regex = '~\[\[table((?:"[^"]*"|[^\]])*)\]\]((?:(?R)|.)*?)\[\[/table\]\]~si';

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
        // Nested tables are converted to opaque tokens before the enclosing
        // body is split into rows, so inner [[row]] and [[cell]] never leak
        // into the outer row or cell grammar.
        $body = preg_replace_callback($this->regex, array(&$this, 'process'), $body);

        $rowRe = '~\[\[row([^\]]*)\]\](.*?)\[\[/row\]\]~si';
        preg_match_all($rowRe, $body, $rows, PREG_SET_ORDER);
        if (count($rows) === 0) {
            return $matches[0];
        }
        if (trim(preg_replace($rowRe, '', $body)) !== '') {
            return $matches[0];
        }

        $cellRe = '~\[\[(cell|hcell)([^\]]*)\]\](.*?)\[\[/(cell|hcell)\]\]~si';
        $rowsOut = '';
        foreach ($rows as $row) {
            preg_match_all($cellRe, $row[2], $cells, PREG_SET_ORDER);
            if (count($cells) === 0) {
                return $matches[0];
            }
            if (trim(preg_replace($cellRe, '', $row[2])) !== '') {
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
            $rowAttrs = $this->buildAttrs($row[1], 'row');
            $rowsOut .= $this->wiki->addToken($this->rule, array(
                'type' => 'rowStart', 'attrs' => $rowAttrs))
                . $cellsOut
                . $this->wiki->addToken($this->rule, array('type' => 'rowEnd'));
        }

        $tableAttrs = $this->buildAttrs($head, 'table');
        $start = $this->wiki->addToken($this->rule, array(
            'type' => 'start', 'attrs' => $tableAttrs));
        $end = $this->wiki->addToken($this->rule, array('type' => 'end'));
        return $start . $rowsOut . $end;
    }

    function parse() {
        $this->wiki->source = preg_replace_callback($this->regex, array(
            &$this, 'process'), $this->wiki->source);
    }

    private function normalizeValue($value) {
        $value = preg_replace('/[\x00-\x1F\x7F]/', '', $value);
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
            // REFCORR8 C-R5-P3-2: a data-* key is recognised by its exact
            // lower-case `data-` prefix and folded to lower case as a
            // whole, matching the List and Div siblings. Other block-head
            // keys stay case sensitive: an upper-case key is dropped.
            if (strpos($key, 'data-') === 0) {
                $key = strtolower($key);
            }
            if (preg_match('/^[a-z][a-z0-9-]*$/', $key) !== 1) {
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
