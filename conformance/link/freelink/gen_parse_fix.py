#!/usr/bin/env python3
"""Regenerate the corrected Freelink parse rule from its preserved before-bytes.
The transliteration map is extracted from ftml's read-only
src/parsing/rule/impls/link_triple_transliteration.rs at the recorded HEAD; it
is data copied into the PHP rule, not an edit to ftml. Run from any cwd."""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WORKTREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BEFORE = os.path.join(HERE, "Freelink.parse.before.php")
TARGET = os.path.join(WORKTREE, "ref-php", "text-wiki", "Text", "Wiki", "Parse", "Default", "Freelink.php")
FTML_TABLE = "/home/roku/src/Rokurolize/ftml/src/parsing/rule/impls/link_triple_transliteration.rs"

src = open(FTML_TABLE, encoding="utf-8").read()
pairs = re.findall(r"'([^'])'\s*=>\s*\"([^\"]*)\"", src)

def php_q(s):
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"

map_lines = "\n".join("        %s => %s," % (php_q(k), php_q(v)) for k, v in pairs)

NEW_METHOD = r'''
    /**
     * Live-shaped freelink processing. The fossil regex captured a page, an
     * optional alpha-initial anchor and a pipe-free label; live Wikidot treats
     * the whole bracket interior as a target with any number of pipes in the
     * label, allows digit-initial anchors, transliterates non-ASCII page names,
     * strips a leading _default: category, recognizes /#/ hash routes, and
     * links bare URLs externally. The corrections are numbered C1-C6 in
     * conformance-refphp/link/freelink/SECTION.md; every shape changed here was
     * settled by the frozen live captures in this directory.
     */
    function process($matches)
    {
        $raw = isset($matches[1]) ? $matches[1] : '';
        $labelRaw = isset($matches[2]) ? $matches[2] : '';

        // Live leaves a genuinely empty target and an anchor-only target with
        // no leading space literal ([[[|Label]]], [[[#a|L]]], [[[#a]]]).
        if ($raw === '' || $raw[0] === '|') {
            return $matches[0];
        }
        if (preg_match('/^#[^ \t]/', $raw)) {
            return $matches[0];
        }

        // C1/C2: malformed multi-hash targets stay literal, matching live and
        // the ftml corpus pins (home###, a##b, a#b#c). A /#/ hash route is the
        // one exception and is handled below.
        if (strpos($raw, '##') !== false && strpos($raw, '/#/') === false) {
            return $matches[0];
        }
        if (substr_count($raw, '#') > 1 && strpos($raw, '/#/') === false) {
            return $matches[0];
        }

        // C1: peel an anchor or a hash-route suffix off the target. A leading
        // space before a hash is part of the target, so '[[[ #a | L ]]]'
        // yields an empty page with anchor #a, which live renders as /#a.
        $anchor = '';
        $extra = '';
        if (strpos($raw, '/#/') !== false) {
            list($base, $rest) = explode('/#/', $raw, 2);
            $raw = $base;
            $extra = '#/' . $rest;
        } elseif (($hashPos = strpos($raw, '#')) !== false) {
            $anchor = rtrim(substr($raw, $hashPos));
            $raw = substr($raw, 0, $hashPos);
        }

        $leadingSpace = (bool) preg_match('/^[ \t]/', $raw);
        $trimmed = trim($raw);

        // C5: a bare, non-leading-space URL is an external link. The label is
        // the URL itself when no pipe label was authored.
        $url = null;
        if (! $leadingSpace && freelink_is_url($trimmed)) {
            $url = $trimmed;
            if ($labelRaw === '') {
                $text = $url;
            } else {
                $text = substr($labelRaw, 1);
            }
            $options = array(
                'site' => null,
                'page' => '',
                'text' => $text,
                'anchor' => '',
                'extra' => '',
                'url' => $url,
                'textFromTitle' => null,
            );
            return $this->wiki->addToken($this->rule, $options);
        }

        // C6: non-ASCII page names go through ftml's explicit transliteration
        // table; unmapped characters act as separators, as on live.
        $slugSource = $raw;
        if (preg_match('/[^\x00-\x7F]/u', $slugSource)) {
            $slugSource = freelink_transliterate($slugSource);
        }

        // C4: a leading _default: is a category marker, not part of the slug,
        // and a leading underscore is otherwise preserved (nonbr is dropped).
        if (preg_match('/^_default:/i', $slugSource)) {
            $slugSource = substr($slugSource, 9);
        }
        $page = WDStringUtils::toUnixName($slugSource);

        if ($labelRaw === '') {
            // No pipe label: live strips a category prefix from the display
            // text but keeps the rest of the authored target.
            $text = $raw;
            // A leading : or / is part of the authored display text on live
            // (e.g. [[[:scp-wiki : system : Recent Changes]]]), so only a
            // category prefix after a real page name is stripped here.
            if ($text[0] !== ':' && $text[0] !== '/' && strpos($text, ':') !== false) {
                $text = substr($text, strpos($text, ':') + 1);
            }
            $text = trim($text);
        } elseif (trim($labelRaw) === '|') {
            // Empty pipe label: the renderer fills the text from the page
            // title when the page exists, otherwise from the slug.
            $text = '|';
        } else {
            $text = substr($labelRaw, 1);
        }

        $options = array(
            'site' => null,
            'page' => $page,
            'text' => $text,
            'anchor' => $anchor,
            'extra' => $extra,
            'url' => null,
            'textFromTitle' => (trim($labelRaw) === '|') ? true : null,
        );
        return $this->wiki->addToken($this->rule, $options);
    }
}

// Helpers live at file scope; the class above is closed before them.
function freelink_is_url($s)
{
    $schemes = array('http://', 'https://', 'ftp://', 'file://', 'feed:',
        'git://', 'gopher://', 'irc://', 'irc6://', 'ircs://', 'sftp://',
        'ssh://', 'telnet://', 'rtmp://', 'resource://', 'chrome://',
        'chrome-extension://', 'content://', 'cvs://', 'blob:', 'dns:',
        'mailto:', 'mms:', 'news:', 'nntp:', 'tel:', 'sms:', 'skype:', 'xmpp:');
    foreach ($schemes as $scheme) {
        if (stripos($s, $scheme) === 0) {
            return true;
        }
    }
    return false;
}

function freelink_transliterate($s)
{
    static $map = array(
%s
    );
    $out = '';
    $chars = preg_split('//u', $s, -1, PREG_SPLIT_NO_EMPTY);
    foreach ($chars as $ch) {
        if ($ch === '#' || $ch === ':' || $ch === '/' || $ch === ' ' || $ch === '_' || $ch === '-') {
            $out .= $ch;
            continue;
        }
        if (isset($map[$ch])) {
            $out .= $map[$ch];
        } else {
            $out .= ' ';
        }
    }
    return $out;
}
''' % map_lines

# Keep the original header/docblock (everything before the process() docblock)
# and replace the constructor's regex plus the whole process() method.
src_php = open(BEFORE, encoding="utf-8").read()
doc_pos = src_php.find('    /**\n    * \n    * Generates a replacement')
assert doc_pos > 0, "process docblock not found"
head = src_php[:doc_pos]
# Replace the fossil regex in the constructor with the live-shaped one.
real = head.rfind('$this->regex =')
assert real > 0, "fossil regex assignment not found"
ctor_end = head.find('\n    }', real)
assert ctor_end > 0, "constructor end not found"
new_ctor = '''           $this->regex =
            '/'.                                        // START regex
            "\\\\[\\\\[\\\\[".                            // triple open
            "([^\\\\]\\\\[]+?)".                          // target (no brackets, non-greedy)
            "(\\\\|[^\\\\]\\\\[]*)?".                    // optional pipe label (pipes allowed)
            "\\\\]\\\\]\\\\]".                            // triple close
            '/';                                        // END regex
    }'''
head = head[:real] + new_ctor + head[ctor_end + len('\n    }'):]
out = head + NEW_METHOD
open(TARGET, "w", encoding="utf-8").write(out)
print("wrote corrected parse rule with", len(pairs), "transliteration entries")
