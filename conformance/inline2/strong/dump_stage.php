<?php
error_reporting(E_ALL & ~E_DEPRECATED & ~E_WARNING);
$root = dirname(__DIR__,3) . '/ref-php/text-wiki';
set_include_path($root . PATH_SEPARATOR . dirname(__DIR__,3) . '/ref-php/wikidot-root/lib' . PATH_SEPARATOR . get_include_path());
require_once dirname(__DIR__,3) . '/ref-php/wikidot-root/lib/WDStringUtils.php';
require_once dirname(__DIR__,3) . '/ref-php/harness/ozone-stubs.php';
require_once $root . '/Text/Wiki.php';
require_once dirname(__DIR__,3) . '/ref-php/harness/wiki-config.php';
$src = $argv[1] ?? "|| **A || B** || C ||\nx";
$wiki = ref_configure_wiki(new Text_Wiki());
// stop just before Strong (rule 'Colortext' is the one before Strong in the list)
$stop = 'Colortext';
$wiki->rules = array_slice($wiki->rules, 0, array_search($stop, $wiki->rules, true));
$wiki->parse($src);
$s = $wiki->source;
// render token markers as [ID:Rule]
$s = preg_replace_callback('/\xFF(\d+)\xFF/', function($m) use ($wiki){
    $t = $wiki->tokens[(int)$m[1]];
    return '{' . $m[1] . ':' . $t[0] . '/' . ($t[1]['type'] ?? '') . '}';
}, $s);
echo "SOURCE-BEFORE-STRONG:\n" . str_replace("\xFF",'<FF>',$s) . "\n";
