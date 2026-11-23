<?php

// vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
/**
 * Defaultoved anchor rule parser for Text_Wiki.
 *
 * PHP versions 4 and 5
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    $Id$
 * @link       http://pear.php.net/package/Text_Wiki
 */

/**
 * Parses for anchor targets ([[# name]]) and anchor elements ([[a ...]]...[[/a]], [[a_ ...]]...[[/a]]).
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Parse_Anchor extends Text_Wiki_Parse {
    
    /**
    *
    * The regular expression used to parse the source text for named anchors.
    *
    * @access public
    *
    * @var string
    *
    * @see parse()
    *
    */
    public $regex = '/(\[\[# )([-_A-Za-z0-9.%]+?)(\]\])/i';
    
    /**
    *
    * Parses both named anchors ([[# name]]) and block/inline anchor pairs
    * ([[a ...]]...[[/a]] and [[a_ ...]]...[[/a]]).
    *
    * @access public
    *
    */
    function parse()
    {
        // 1. Named anchors [[# name]] and invalid-name [[# ...]] fallback
        $this->parseNamedAnchors();

        // 2. [[a ...]]...[[/a]] and [[a_ ...]]...[[/a]]
        $this->parseAnchorElements();
    }

    /**
    *
    * Generates a replacement for the matched named anchor text.
    *
    * @access public
    *
    * @param array $matches The array of matches from parse().
    *
    * @return string A delimited token to be used as a placeholder in
    * the source text.
    *
    */
    function process($matches)
    {
        $name = $matches[2];
        return $this->wiki->addToken($this->rule, array('name' => $name));
    }

    /**
    *
    * Scans for [[# ...]] named anchors on a single line.
    * Valid names (^[-_A-Za-z0-9.%]+$) emit a named Anchor token (<a name="..."></a>).
    * Non-empty invalid names emit the javascript:; pseudo-link form with
    * leading/trailing spaces hoisted outside the inner <a> tag, unless closed
    * by a residual ']]]' outside a triple-bracket wrapper.
    *
    */
    function parseNamedAnchors()
    {
        $source = $this->wiki->source;
        if (strpos($source, '[[#') === false) {
            return;
        }

        $pattern = '/\[\[#[ \t]([^\n\]]*)\]\](\])?/';
        if (!preg_match_all($pattern, $source, $matches, PREG_SET_ORDER | PREG_OFFSET_CAPTURE)) {
            return;
        }

        $out = '';
        $cursor = 0;

        foreach ($matches as $m) {
            $fullStart = $m[0][1];
            $fullLen = strlen($m[0][0]);
            $name = $m[1][0];
            $residualCloser = isset($m[2][0]) && $m[2][0] === ']';

            $out .= substr($source, $cursor, $fullStart - $cursor);

            // C-SUSPECT-XRULE-6: an earlier rule's placeholder in the name
            // leaves the whole bracket form literal on live, with the inner
            // token resolving in place.
            if (strpos($name, $this->wiki->delim) !== false) {
                $out .= $m[0][0];
                $cursor = $fullStart + $fullLen;
                continue;
            }

            if (trim($name) === '') {
                $out .= $m[0][0];
                $cursor = $fullStart + $fullLen;
                continue;
            }

            if (preg_match('/^[-_A-Za-z0-9.%]+$/', $name)) {
                $tok = $this->process(array($m[0][0], '[[# ', $name, ']]'));
                $out .= $tok . ($residualCloser ? ']' : '');
                $cursor = $fullStart + $fullLen;
                continue;
            }

            // Invalid characters in [[# ...]]: if closed by ']]]' and not preceded
            // by '[', leave literal (so Url does not partially consume it).
            $precededByBracket = ($fullStart > 0 && $source[$fullStart - 1] === '[');
            if ($residualCloser && !$precededByBracket) {
                $tok = $this->wiki->addToken($this->rule, array(
                    'type' => 'literal',
                    'text' => $m[0][0]
                ));
                $out .= $tok;
                $cursor = $fullStart + $fullLen;
                continue;
            }

            // Split leading/trailing horizontal spaces around the invalid name.
            $leadWs = '';
            $trailWs = '';
            $trimmed = $name;
            if (preg_match('/^([ \t]+)(.*)$/s', $trimmed, $lm)) {
                $leadWs = $lm[1];
                $trimmed = $lm[2];
            }
            if (preg_match('/^(.*?)([ \t]+)$/s', $trimmed, $tm)) {
                $trimmed = $tm[1];
                $trailWs = $tm[2];
            }

            $tok = $this->wiki->addToken($this->rule, array(
                'type' => 'invalid_named',
                'lead' => $leadWs,
                'text' => $trimmed,
                'trail' => $trailWs
            ));
            $out .= $tok . ($residualCloser ? ']' : '');
            $cursor = $fullStart + $fullLen;
        }

        if ($cursor < strlen($source)) {
            $out .= substr($source, $cursor);
        }

        $this->wiki->source = $out;
    }

    /**
    *
    * Scans and tokenizes [[a ...]]...[[/a]] and [[a_ ...]]...[[/a]] pairs.
    *
    */
    function parseAnchorElements()
    {
        $source = $this->wiki->source;
        if (stripos($source, '[[a') === false) {
            return;
        }

        if (!isset($this->wiki->vars['scored_anchors']) || !is_array($this->wiki->vars['scored_anchors'])) {
            $this->wiki->vars['scored_anchors'] = array();
        }

        $pattern = '/\[\[a(_)?(?:\s+([^\s\]][^\]]*))?\]\](.*?)\[\[\/a\]\]/si';
        if (!preg_match_all($pattern, $source, $matches, PREG_SET_ORDER | PREG_OFFSET_CAPTURE)) {
            return;
        }

        $out = '';
        $cursor = 0;
        $srcLen = strlen($source);
        $openerPattern = '/\[\[a(_)?(?:\s+([^\s\]][^\]]*))?\]\]/si';

        foreach ($matches as $m) {
            $fullStart = $m[0][1];
            if ($fullStart < $cursor) {
                continue;
            }
            $fullLen = strlen($m[0][0]);
            $fullEnd = $fullStart + $fullLen;

            $out .= substr($source, $cursor, $fullStart - $cursor);

            $scored = (isset($m[1][0]) && $m[1][0] === '_');
            $attrStr = isset($m[2][0]) ? $m[2][0] : '';
            $body = $m[3][0];

            $attrs = $this->buildAnchorAttrs($attrStr);

            // Check if body itself contains a nested [[a...]] opener (e.g.
            // [[a href="/1"]]x[[a href="/2"]]y[[/a]]z[[/a]]). On live and in
            // ftml, the inner [[a...]] closes the outer <a> before opening the
            // inner <a>, and a subsequent matching [[/a]] closer is consumed.
            if (!$scored && preg_match($openerPattern, $body, $innerM, PREG_OFFSET_CAPTURE)) {
                $innerPos = $innerM[0][1];
                $innerLen = strlen($innerM[0][0]);
                $innerAttrStr = isset($innerM[2][0]) ? $innerM[2][0] : '';
                $innerAttrs = $this->buildAnchorAttrs($innerAttrStr);

                $outerBody = substr($body, 0, $innerPos);
                $innerBody = substr($body, $innerPos + $innerLen);

                $s1 = $this->wiki->addToken($this->rule, array('type' => 'start', 'attrs' => $attrs));
                $e1 = $this->wiki->addToken($this->rule, array('type' => 'end'));
                $s2 = $this->wiki->addToken($this->rule, array('type' => 'start', 'attrs' => $innerAttrs));
                $e2 = $this->wiki->addToken($this->rule, array('type' => 'end'));

                $out .= $s1 . $outerBody . $e1 . $s2 . $innerBody . $e2;

                // If there is a trailing [[/a]] on the same line before any next [[a...]], consume it.
                $restAfter = substr($source, $fullEnd);
                if (preg_match('/^([^\n]*?)\[\[\/a\]\]/i', $restAfter, $closeM)) {
                    if (!preg_match($openerPattern, $closeM[1])) {
                        $out .= $closeM[1];
                        $cursor = $fullEnd + strlen($closeM[0]);
                        continue;
                    }
                }
                $cursor = $fullEnd;
                continue;
            }

            if ($scored) {
                // If preceded by non-newline content across 1-2 newlines, join onto previous line.
                if (preg_match('/([^\n])(\n{1,2})$/s', $out, $pm)) {
                    $out = substr($out, 0, -strlen($pm[2]));
                }
                // Strip a single leading and trailing newline inside the scored anchor body.
                if (substr($body, 0, 1) === "\n") {
                    $body = substr($body, 1);
                }
                if (substr($body, -1) === "\n") {
                    $body = substr($body, 0, -1);
                }
            }

            // Boundary horizontal space movement (spaces/tabs at body edges).
            $leadSpace = (preg_match('/^[ \t]+/', $body) === 1);
            if ($leadSpace) {
                $body = preg_replace('/^[ \t]+/', '', $body);
            }
            $trailSpace = ($body !== '' && preg_match('/[ \t]+$/', $body) === 1);
            if ($trailSpace) {
                $body = preg_replace('/[ \t]+$/', '', $body);
            }

            $nextPos = $fullEnd;
            if ($scored) {
                // If followed by 1-2 newlines and then non-newline content, join the following line.
                if (preg_match('/^\n{1,2}(?=[^\n])/s', substr($source, $fullEnd), $nm)) {
                    $nextPos += strlen($nm[0]);
                }
            }

            $prefix = '';
            if ($leadSpace) {
                $prevChar = ($out !== '') ? substr($out, -1) : '';
                if ($prevChar !== '' && $prevChar !== "\n" && $prevChar !== ' ' && $prevChar !== "\t") {
                    $prefix = ' ';
                }
            }

            $suffix = '';
            if ($trailSpace) {
                $nextChar = ($nextPos < $srcLen) ? $source[$nextPos] : '';
                if ($nextChar !== '' && $nextChar !== "\n" && $nextChar !== ' ' && $nextChar !== "\t") {
                    $suffix = ' ';
                }
            }

            if (!$scored && strpos($body, "\n\n") !== false && strpos($body, '[[') === false) {
                // Paragraph split inside plain [[a ...]]...[[/a]]: wrap each paragraph run.
                $parts = preg_split('/(\n{2,})/', $body, -1, PREG_SPLIT_DELIM_CAPTURE);
                $rebuilt = '';
                foreach ($parts as $idx => $part) {
                    if ($idx % 2 === 1) {
                        $rebuilt .= $part;
                    } else {
                        $startTok = $this->wiki->addToken($this->rule, array('type' => 'start', 'attrs' => $attrs));
                        $endTok = $this->wiki->addToken($this->rule, array('type' => 'end'));
                        $rebuilt .= $startTok . $part . $endTok;
                    }
                }
                $out .= $prefix . $rebuilt . $suffix;
            } else {
                $startTok = $this->wiki->addToken($this->rule, array('type' => 'start', 'attrs' => $attrs));
                $endTok = $this->wiki->addToken($this->rule, array('type' => 'end'));
                if ($scored) {
                    $this->wiki->vars['scored_anchors'][$endTok] = $startTok;
                }
                $out .= $prefix . $startTok . $body . $endTok . $suffix;
            }

            $cursor = $nextPos;
        }

        if ($cursor < $srcLen) {
            $out .= substr($source, $cursor);
        }

        $this->wiki->source = $out;
    }

    /**
    *
    * Parses and normalizes attributes for [[a ...]] / [[a_ ...]] according to
    * live Wikidot's allowlist, u- id isolation, data-* lowercasing, href
    * verbatim vs slug classification, and target="_blank" star handling.
    *
    * @param string $attrStr Raw attribute string from opener head.
    * @return array Normalized attribute map in canonical emission order.
    *
    */
    function buildAnchorAttrs($attrStr)
    {
        $rawAttrs = (trim($attrStr) !== '') ? $this->getAttrs($attrStr) : array();

        $fixed = array();
        $dataAttrs = array();
        $rawHref = null;
        $delim = $this->wiki->delim;

        foreach ($rawAttrs as $key => $rawVal) {
            if (!is_string($key)) {
                continue;
            }
            if ($key === 'href') {
                $rawHref = $rawVal;
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
            if ($key === 'class' || $key === 'style' || $key === 'role' || $key === 'type' || $key === 'target') {
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

        // Normalize href and starred target="_blank"
        $finalHref = '';
        if ($rawHref !== null && $rawHref !== '') {
            $starred = false;
            $hrefRest = $rawHref;
            if ($hrefRest[0] === '*') {
                $starred = true;
                $hrefRest = substr($hrefRest, 1);
            }

            if ($this->isVerbatimHref($hrefRest)) {
                if ($starred && !isset($fixed['target'])) {
                    $fixed['target'] = '_blank';
                }
                if (strpos($hrefRest, $delim) !== false) {
                    $finalHref = '';
                } else {
                    $normHref = $this->normalizeAttrValue($hrefRest);
                    $normHref = str_replace(' ', '%20', $normHref);
                    $normHref = preg_replace_callback('/[^\x00-\x7F]/', function ($m) {
                        $bytes = unpack('C*', $m[0]);
                        $enc = '';
                        foreach ($bytes as $b) {
                            $enc .= '%' . strtoupper(str_pad(dechex($b), 2, '0', STR_PAD_LEFT));
                        }
                        return $enc;
                    }, $normHref);
                    $finalHref = $normHref;
                }
            } else {
                $finalHref = $this->normalizeUnsafeHref($hrefRest);
            }
        }

        // Assemble in canonical emission order:
        // 1. id, class, style, role, type
        // 2. data-* (in authored order)
        // 3. href (always emitted)
        // 4. target
        $ordered = array();
        foreach (array('id', 'class', 'style', 'role', 'type') as $k) {
            if (isset($fixed[$k])) {
                $ordered[$k] = $fixed[$k];
            }
        }
        foreach ($dataAttrs as $k => $v) {
            $ordered[$k] = $v;
        }
        $ordered['href'] = $finalHref;
        if (isset($fixed['target'])) {
            $ordered['target'] = $fixed['target'];
        }

        return $ordered;
    }

    /**
    *
    * Strips C0 control bytes (except \t, \n, \r) and DEL, then collapses runs
    * of ASCII whitespace to a single space and trims both ends.
    *
    */
    function normalizeAttrValue($val)
    {
        $clean = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/', '', $val);
        $clean = preg_replace('/[ \t\n\r]+/', ' ', $clean);
        return trim($clean, ' ');
    }

    /**
    *
    * Checks whether an anchor href (after optional leading '*') is in live
    * Wikidot's verbatim href class.
    *
    */
    function isVerbatimHref($href)
    {
        if ($href === '') {
            return false;
        }
        if ($href[0] === '#' || $href[0] === '/') {
            return true;
        }
        $prefixes = array(
            'http://',
            'https://',
            'ftp://',
            'mailto:',
            'gopher://',
            'news://',
            'mms://',
            'git://',
            'sftp://',
            'ssh://',
            'svn://',
            'telnet://',
            'cvs://',
        );
        foreach ($prefixes as $p) {
            if (strpos($href, $p) === 0) {
                return true;
            }
        }
        return false;
    }

    /**
    *
    * Normalizes a non-verbatim anchor href into a lowercased page-slug form.
    *
    */
    function normalizeUnsafeHref($href)
    {
        $norm = $this->normalizeAttrValue($href);
        $norm = preg_replace('/^(?:\xC2\xA0)+|(?:\xC2\xA0)+$/', '', $norm);
        $norm = str_replace(array('\\', "\xC2\xA0"), '', $norm);

        $out = '';
        $pendingSep = false;
        $pendingColon = false;
        $len = strlen($norm);

        for ($i = 0; $i < $len; $i++) {
            $ch = $norm[$i];
            if (ctype_alnum($ch)) {
                if ($pendingSep) {
                    $out .= $pendingColon ? ':' : '-';
                    $pendingSep = false;
                    $pendingColon = false;
                }
                $out .= strtolower($ch);
            } elseif ($ch === ':') {
                if ($out !== '') {
                    $pendingSep = true;
                    $pendingColon = true;
                }
            } else {
                if ($out !== '') {
                    $pendingSep = true;
                }
            }
        }

        return $out;
    }
}
?>
