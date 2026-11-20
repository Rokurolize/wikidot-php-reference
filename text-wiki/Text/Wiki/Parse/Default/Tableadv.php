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
 * whether a cell renders as a header cell, so [[cell]]x[[/hcell]] is a header
 * and [[hcell]]x[[/cell]] is not. Attribute heads tolerate a quoted ]] on a
 * table, while row and cell heads use the plain token grammar. Nested tables
 * are handled recursively before the enclosing rows and cells are split.
 */
class Text_Wiki_Parse_Tableadv extends Text_Wiki_Parse {

    public $regex = '~\[\[table((?:"[^"]*"|[^\]])*)\]\]((?:(?R)|.)*?)\[\[/table\]\]~si';

    // The Wikitext safe-attribute allowlist, lower-case names only at this
    // block level; data- and aria- names are allowed with a safe suffix.
    private $safeAttrs = array(
        'accept', 'align', 'alt', 'autocapitalize', 'autoplay', 'background',
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
                $isHeader = (strtolower($cell[4]) === 'hcell');
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
        if (strpos($key, 'aria-') === 0) {
            $suffix = substr($key, 5);
            return $suffix !== '' && preg_match('/^[A-Za-z0-9-]+$/', $suffix) === 1;
        }
        return in_array($key, $this->safeAttrs, true);
    }

    private function buildAttrs($text, $owner) {
        $parsed = $this->getAttrs(trim($text));
        $attrs = array();
        foreach ($parsed as $key => $value) {
            // Block heads at this level are case sensitive: an upper-case
            // key is dropped rather than folded.
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
        ksort($attrs);
        return $attrs;
    }
}
