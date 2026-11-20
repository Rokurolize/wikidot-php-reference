<?php
// Local inspection helper (evidence only): prints Mathinline token content
// in hex for nominated sources. Mirrors batch.php's setup and configuration;
// does not edit or replace the shared harness.
error_reporting(E_ALL & ~E_DEPRECATED & ~E_WARNING);
ini_set('display_errors', 'stderr');
define('WIKIDOT_ROOT', dirname(__DIR__, 3) . '/ref-php/wikidot-root');
$root = dirname(__DIR__, 3) . '/ref-php/text-wiki';
ini_set('include_path', $root . PATH_SEPARATOR
    . dirname(__DIR__, 3) . '/ref-php/wikidot-root/lib' . PATH_SEPARATOR
    . ini_get('include_path'));
require_once dirname(__DIR__, 3) . '/ref-php/wikidot-root/lib/WDStringUtils.php';
require_once dirname(__DIR__, 3) . '/ref-php/harness/ozone-stubs.php';
require_once $root . '/Text/Wiki.php';
require_once $root . '/Text/Wiki/Parse/Default/Math.php';
require_once dirname(__DIR__, 3) . '/ref-php/harness/wiki-config.php';
require_once dirname(__DIR__, 3) . '/ref-php/harness/pages.php';
$GLOBALS['REF_PAGES'] = ref_page_map();
$GLOBALS['REF_EXISTING_PAGES'] = array_keys(ref_page_map());
$sources = array(
    'basic' => '[[$ x^2 $]]',
    'single-newline' => "[[$ E =\nmc^2 $]]",
    'raw-inside' => '[[$ a@@raw@@b $]]',
    'comment-inside' => '[[$ a[!--c--]b $]]',
);
foreach ($sources as $name => $src) {
    $wiki = ref_configure_wiki(new Text_Wiki());
    $wiki->vars['page'] = new RefPage('', 0, array());
    $wiki->parse($src);
    $found = array();
    foreach ($wiki->tokens as $tok) {
        if ($tok[0] === 'Mathinline') {
            $found[] = bin2hex($tok[1]['content']) . '  (' . json_encode($tok[1]['content'], JSON_INVALID_UTF8_SUBSTITUTE) . ')';
        }
    }
    echo $name, ': ', implode(' | ', $found), "\n";
    if ($name !== 'basic') {
        foreach ($wiki->tokens as $tid => $tok) {
            echo '    token ', $tid, ' = ', $tok[0], "\n";
        }
    }
}
