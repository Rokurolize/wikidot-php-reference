<?php
// Reference harness configuration: mirrors WikiTransformation::resetWiki()
// (fossil php/utils/WikiTransformation.php) in its default page mode, so the
// standalone Text_Wiki runs under the same configuration production used.
// Mode-specific overrides (post/list) and per-page settings (setPage) are
// environment, to be layered in as R2 needs them.

// The fossil registers a global page-existence callback for freelinks.
// The reference harness treats a fixed in-memory page set as existing;
// R2 will wire it to the differential corpus's page set.
// REFCORR13 R13-AGY2 D13: the callback's truthy value is the PAGE ID the
// render rules pass to DB_PagePeer::selectByPrimaryKey(), not a bare bool.
// Returning true here was what made textFromTitle resolution unreachable.
$GLOBALS['REF_EXISTING_PAGES'] = array();
function wikiPageExists($page) {
    if (in_array($page, $GLOBALS['REF_EXISTING_PAGES'], true)) {
        return function_exists('ref_page_id') ? ref_page_id($page) : 1;
    }
    return false;
}

function ref_configure_wiki($wiki) {
    $format = 'Xhtml';
    $wiki->setRenderConf($format, 'freelink', 'view_url', '/%s');
    $wiki->setRenderConf($format, 'freelink', 'new_url', '/%s');
    $wiki->setRenderConf($format, 'url', 'images', false);
    $wiki->setRenderConf($format, 'freelink', 'new_text', '');
    $wiki->setRenderConf($format, 'freelink', 'css_new', 'newpage');
    $wiki->setRenderConf($format, 'table', 'css_table', 'wiki-content-table');
    $wiki->setRenderConf($format, 'freelink', 'exists_callback', 'wikiPageExists');
    // R2-inline1 harness matter, disclosed in conformance-refphp/R2-INLINE1.md:
    // live's saved-page view resolves all five resetWiki interwiki templates
    // over https:// (probes muse-probe-r2in1-x-x21, -x24 with the coordinator's
    // direct anonymous GETs). The R1-era table here carried http://; the site
    // set and the %s slots are unchanged, only the scheme is brought forward.
    // This is configuration, not rule behavior, so no Interwiki rule file is
    // edited for it.
    $interWikis = array(
        'wikipedia'    => 'https://en.wikipedia.org/wiki/%s',
        'wikipedia.pl' => 'https://pl.wikipedia.org/wiki/%s',
        'pl.wikipedia' => 'https://pl.wikipedia.org/wiki/%s',
        'google'       => 'https://www.google.com/search?q=%s',
        'dictionary'   => 'https://dictionary.reference.com/browse/%s',
    );
    $wiki->setRenderConf($format, 'interwiki', 'sites', $interWikis);
    $wiki->setParseConf('interwiki', 'sites', $interWikis);
    $wiki->disableRule('wikilink');
    return $wiki;
}
