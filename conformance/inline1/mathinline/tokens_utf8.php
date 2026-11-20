<?php
// Supplementary analysis driver (evidence only). Same protocol and setup as
// ref-php/harness/batch.php tokens, but encodes invalid UTF-8 in token option
// strings with JSON_INVALID_UTF8_SUBSTITUTE so the four placeholder-bearing
// Mathinline cases are inspectable. The authoritative harness output remains
// ref-tokens-before.jsonl / ref-tokens-after.jsonl; this file only recovers
// the bytes json_encode() there refuses. Does not edit the shared harness.
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
while (($line = fgets(STDIN)) !== false) {
    $line = trim($line);
    if ($line === '') continue;
    $case = json_decode($line, true);
    Text_Wiki_Parse_Math::$equationsArray = array();
    $src = str_replace("\r\n", "\n", $case['source']);
    $wiki = ref_configure_wiki(new Text_Wiki());
    $wiki->vars['footnotes'] = array();
    $wiki->vars['bibitems'] = array();
    $wiki->vars['bibitemIds'] = array();
    $tags = (isset($case['tags']) && is_array($case['tags'])) ? $case['tags'] : array();
    $wiki->vars['page'] = new RefPage('', 0, $tags);
    $wiki->parse($src);
    $enc = json_encode($wiki->tokens, JSON_INVALID_UTF8_SUBSTITUTE);
    echo json_encode(array('id' => $case['id'], 'output' => $enc)), "\n";
}
