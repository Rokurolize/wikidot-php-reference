<?php
// vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
/**
  * Freelink rule end renderer for Xhtml
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
 * The wikilink render class.
 */
require_once 'Text/Wiki/Render/Xhtml/Wikilink.php';

/**
 * This class renders free links in XHTML.
 *
 * Two live-settled differences from the inherited Wikilink renderer are
 * handled here (see conformance-refphp/link/freelink/SECTION.md): the
 * Wikilink new-page branch omitted the anchor from the href, whereas live and
 * ftml keep it, and a bare external URL target renders as an external href
 * rather than a local page slug. Everything else is the inherited behavior.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Freelink extends Text_Wiki_Render_Xhtml_Wikilink {

    function token($options)
    {
        $page = isset($options['page']) ? $options['page'] : '';
        $text = isset($options['text']) ? $options['text'] : '';
        $anchor = isset($options['anchor']) ? $options['anchor'] : '';
        $extra = isset($options['extra']) ? $options['extra'] : '';
        $url = isset($options['url']) ? $options['url'] : null;
        $site = isset($options['site']) ? $options['site'] : null;
        $nonbr = !empty($options['nonbr']);
        $textFromTitle = !empty($options['textFromTitle']);

        // A bare external URL target is an external link, not a local slug.
        if ($url) {
            // REFCORR13 D07: an empty pipe label falls back to the slugified URL page name, as on live, instead of emitting an empty anchor.
            if ($textFromTitle && trim($text) === '') {
                $text = $page;
            }
            $text = htmlspecialchars(trim($text), ENT_COMPAT, 'UTF-8');
            if ($nonbr) {
                $text = str_replace(' ', '&nbsp;', $text);
            }
            // REFCORR3 C-SUSPECT-SERVING-2: the parse rule puts target
            // "_blank" on a starred URL; a plain URL has no target option
            // and its pinned output is unchanged.
            $target = isset($options['target']) ? $options['target'] : '';
            $targetAttr = $target !== ''
                ? ' target="' . htmlspecialchars($target, ENT_COMPAT, 'UTF-8') . '"'
                : '';
            // REFCORR13 C-R5F-R2-4 plus D06: live percent-encodes every non-ASCII byte of the external Freelink href and keeps the peeled #fragment or /#/route suffix; the reference kept them raw or dropped them. Apply Url.php's bytewise encoder to the target plus suffix before the ENT_COMPAT escape; the authored label is untouched.
            $hrefUrl = preg_replace_callback('/[^\x00-\x7F]/', function ($m) {
                $bytes = unpack('C*', $m[0]);
                $out = '';
                foreach ($bytes as $byte) {
                    $out .= '%' . strtoupper(str_pad(dechex($byte), 2, '0', STR_PAD_LEFT));
                }
                return $out;
            }, $url . $anchor . $extra);
            return '<a' . $targetAttr . ' href="' . htmlspecialchars($hrefUrl, ENT_COMPAT, 'UTF-8') . '">' . $text . '</a>';
        }

        // The fossil site branch (cross-site http://site.URL_DOMAIN/page) is
        // unreachable after the parse correction removed the :: convention;
        // live treats :: as a local slug. Kept for completeness only.
        if ($site) {
            $o = '<a href="http://' . $site . '.' . GlobalProperties::$URL_DOMAIN . '/' . $page . '">';
            $o .= htmlspecialchars(trim($text), ENT_COMPAT, 'UTF-8');
            $o .= '</a>';
            return $o;
        }

        // Existence check, identical to the parent Wikilink renderer.
        $callback = isset($this->conf['exists_callback']) ? $this->conf['exists_callback'] : null;
        if ($callback) {
            $exists = call_user_func($callback, $page);
        } else {
            $list =& $this->getConf('pages');
            $exists = is_array($list) ? in_array($page, $list) : true;
        }

        if ($exists && $textFromTitle) {
            // Serving-layer lookup still owned by the fossil; a harness stub
            // need is reported to root rather than edited by this rule owner.
            $pageObj = DB_PagePeer::instance()->selectByPrimaryKey($exists);
            $text = $pageObj->getTitleOrUnixName();
        } elseif (! $exists && $textFromTitle) {
            $text = $page;
        }

        $page = htmlspecialchars(trim($page), ENT_COMPAT, 'UTF-8');
        // C1: append the anchor (and a /#/ hash-route suffix) in BOTH the
        // existing and new-page branches. The inherited Wikilink renderer
        // dropped the anchor in the new-page branch; live and ftml keep it.
        $suffix = htmlspecialchars(trim($anchor), ENT_COMPAT, 'UTF-8') . htmlspecialchars(trim($extra), ENT_COMPAT, 'UTF-8');
        $text = htmlspecialchars(trim($text), ENT_COMPAT, 'UTF-8');
        if ($nonbr) {
            $text = str_replace(' ', '&nbsp;', $text);
        }

        if ($exists) {
            $wiki = $this->wiki;
            if (empty($wiki->vars['internalLinksExist'])) {
                $wiki->vars['internalLinksExist'] = array();
            }
            $wiki->vars['internalLinksExist'][$exists] = $exists;

            $href = $this->getConf('view_url');
            if (strpos($href, '%s') === false) {
                $href = $href . $page . $suffix;
            } else {
                $href = sprintf($href, $page . $suffix);
            }
            $css = $this->formatConf(' class="%s"', 'css');
            return "<a$css href=\"$href\">$text</a>";
        }

        $wiki = $this->wiki;
        if (empty($wiki->vars['internalLinksNotExist'])) {
            $wiki->vars['internalLinksNotExist'] = array();
        }
        $wiki->vars['internalLinksNotExist'][$page] = $page;

        $href = $this->getConf('new_url', null);
        if (! $href || trim($href) == '') {
            return $text;
        }
        if (strpos($href, '%s') === false) {
            $href = $href . $page . $suffix;
        } else {
            $href = sprintf($href, $page . $suffix);
        }
        $css = $this->formatConf(' class="%s"', 'css_new');
        $new = $this->getConf('new_text');
        $pos = $this->getConf('new_text_pos');
        if (! $pos || ! $new) {
            return "<a$css href=\"$href\">$text</a>";
        } elseif ($pos == 'before') {
            return "<a$css href=\"$href\">$new</a>$text";
        }
        return "$text<a$css href=\"$href\">$new</a>";
    }
}
