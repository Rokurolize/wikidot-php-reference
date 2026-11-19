<?php
// Reference harness configuration: mirrors WikiTransformation::resetWiki()
// (fossil php/utils/WikiTransformation.php) in its default page mode, so the
// standalone Text_Wiki runs under the same configuration production used.
// Mode-specific overrides (post/list) and per-page settings (setPage) are
// environment, to be layered in as R2 needs them.

// The fossil registers a global page-existence callback for freelinks.
// The reference harness treats a fixed in-memory page set as existing;
// R2 will wire it to the differential corpus's page set.
$GLOBALS['REF_EXISTING_PAGES'] = array();
function wikiPageExists($page) {
    return in_array($page, $GLOBALS['REF_EXISTING_PAGES'], true);
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
    $interWikis = array(
        'wikipedia'    => 'http://en.wikipedia.org/wiki/%s',
        'wikipedia.pl' => 'http://pl.wikipedia.org/wiki/%s',
        'pl.wikipedia' => 'http://pl.wikipedia.org/wiki/%s',
        'google'       => 'http://www.google.com/search?q=%s',
        'dictionary'   => 'http://dictionary.reference.com/browse/%s',
    );
    $wiki->setRenderConf($format, 'interwiki', 'sites', $interWikis);
    $wiki->setParseConf('interwiki', 'sites', $interWikis);
    $wiki->disableRule('wikilink');
    return $wiki;
}
