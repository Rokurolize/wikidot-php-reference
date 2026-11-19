<?php
// R1 harness: drive the standalone Text_Wiki copy (ref-php/text-wiki).
// Usage: php transform.php render|tokens  < input.wikitext
//   render: print the Xhtml output of Text_Wiki::transform
//   tokens: parse only, print the token array as JSON
// No behavior configuration yet: the default rule list, exactly as
// WikiTransformation constructs it (new Text_Wiki()).
error_reporting(E_ALL & ~E_DEPRECATED);
ini_set('display_errors', 'stderr');
// The OZONE bootstrap defined WIKIDOT_ROOT for the vendored library;
// the reference harness does the same, pointing at the reconstructed
// root layout in ref-php/wikidot-root/ (Text_Highlighter, tmp, conf).
define('WIKIDOT_ROOT', dirname(__DIR__) . '/wikidot-root');
$root = dirname(__DIR__) . '/text-wiki';
ini_set('include_path', $root . PATH_SEPARATOR
    . dirname(__DIR__) . '/wikidot-root/lib' . PATH_SEPARATOR
    . ini_get('include_path'));
require_once dirname(__DIR__) . '/wikidot-root/lib/WDStringUtils.php';
require_once __DIR__ . '/ozone-stubs.php';
require_once $root . '/Text/Wiki.php';

$mode = $argv[1] ?? 'render';
require_once __DIR__ . '/pages.php';
$GLOBALS['REF_PAGES'] = ref_page_map();
$src = file_get_contents('php://stdin');
// Input stage (see R2-INCLUDE.md C1): the pipeline normalizes all
// line endings to \n (Prefilter's own first step); applying it
// before the Include rule is what lets includes fire on CRLF text,
// as they do live.
$src = str_replace("\r\n", "\n", $src);
// Lone \r stays: see batch.php's note (R2-INCLUDE.md C1).
require_once __DIR__ . '/wiki-config.php';
$wiki = ref_configure_wiki(new Text_Wiki());
if ($mode === 'tokens') {
    $wiki->parse($src);
    echo json_encode($wiki->tokens, JSON_PRETTY_PRINT | JSON_INVALID_UTF8_SUBSTITUTE), "\n";
} else {
    echo $wiki->transform($src, 'Xhtml');
    echo "\n";
}
