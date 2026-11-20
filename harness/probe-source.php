<?php
// One-off R3 scoping probe: print the post-parse source (with \xFF
// placeholders made visible) alongside the token table for each
// JSONL case on stdin. Not part of the harness protocol.
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
require_once $root . '/Text/Wiki/Parse/Default/Math.php';
require_once __DIR__ . '/wiki-config.php';
require_once __DIR__ . '/pages.php';

$GLOBALS['REF_PAGES'] = ref_page_map();
$GLOBALS['REF_EXISTING_PAGES'] = array_keys(ref_page_map());


// R3.3 wire encoding (adopted 2026-11-21, the same encoding as
// state-restricted.php): recursively replace any string that is not
// valid UTF-8 with {"$bytes": [byte values]} so token option values
// spanning placeholders serialize instead of failing json_encode.
function ref_wire_encode($v) {
    if (is_string($v)) {
        if (preg_match('//u', $v) === 1) { return $v; }
        return array('$bytes' => array_values(unpack('C*', $v)));
    }
    if (is_array($v)) {
        $out = array();
        foreach ($v as $k => $x) { $out[$k] = ref_wire_encode($x); }
        return $out;
    }
    return $v;
}

while (($line = fgets(STDIN)) !== false) {
    $line = trim($line);
    if ($line === '') continue;
    $case = json_decode($line, true);
    $src = str_replace("\r\n", "\n", $case['source']);
    $wiki = ref_configure_wiki(new Text_Wiki());
    $wiki->vars['page'] = new RefPage('', 0, array());
    $wiki->parse($src);
    $vis = str_replace("\xFF", '<FF>', $wiki->source);
    echo json_encode(ref_wire_encode(array('id' => $case['id'], 'post_parse_source' => $vis, 'tokens' => $wiki->tokens))), "\n";
}
