<?php
// R2 tool: find which parse rule first removes (or changes) a target
// string in the post-parse source. Runs the pipeline with growing
// prefixes of the default rule list and reports the first prefix
// whose output source no longer contains the target.
// Usage: php rule-bisect.php <input-file> <target-string>
error_reporting(E_ALL & ~E_DEPRECATED & ~E_WARNING);
ini_set('display_errors', 'stderr');
define('WIKIDOT_ROOT', dirname(__DIR__) . '/wikidot-root');
$root = dirname(__DIR__) . '/text-wiki';
ini_set('include_path', $root . PATH_SEPARATOR
    . dirname(__DIR__) . '/wikidot-root/lib' . PATH_SEPARATOR
    . ini_get('include_path'));
require_once dirname(__DIR__) . '/wikidot-root/lib/WDStringUtils.php';
require_once __DIR__ . '/ozone-stubs.php';
require_once $root . '/Text/Wiki.php';
require_once __DIR__ . '/wiki-config.php';
require_once __DIR__ . '/pages.php';
$GLOBALS['REF_PAGES'] = ref_page_map();

$src = file_get_contents($argv[1]);
$target = $argv[2];
$probe = new Text_Wiki();
$all = $probe->rules;
echo "total rules: ", count($all), "\n";
for ($n = 1; $n <= count($all); $n++) {
    $rules = array_slice($all, 0, $n);
    $wiki = new Text_Wiki($rules);
    $wiki->parse($src);
    $found = strpos($wiki->source, $target) !== false;
    echo str_pad($n, 3), ' ', str_pad(end($rules), 16), $found ? "target present" : "TARGET GONE", "\n";
    if (!$found) break;
}
