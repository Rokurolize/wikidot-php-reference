<?php
// Local diagnostic driver (NOT part of the shared harness): runs ONLY the
// Text_Wiki_Parse_Module654 rule, so the rule's own matching space is visible
// without Modulepre's lowercase rewrite shadowing it. Mirrors the shared
// ref-php/harness/batch.php bootstrap but uses new Text_Wiki(array('Module654')).
// Usage: /usr/bin/php module654-only.php render|tokens < battery.jsonl
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
require_once dirname(__DIR__, 3) . '/ref-php/harness/wiki-config.php';
$mode = $argv[1] ?? 'render';
while (($line = fgets(STDIN)) !== false) {
    $line = trim($line);
    if ($line === '') continue;
    $case = json_decode($line, true);
    $src = str_replace("\r\n", "\n", $case['source']);
    try {
        $wiki = ref_configure_wiki(new Text_Wiki(array('Module654')));
        if ($mode === 'tokens') {
            $wiki->parse($src);
            echo json_encode(array('id' => $case['id'],
                'output' => json_encode($wiki->tokens))), "\n";
        } else {
            $out = $wiki->transform($src, 'Xhtml');
            echo json_encode(array('id' => $case['id'], 'output' => $out)), "\n";
        }
    } catch (Throwable $e) {
        echo json_encode(array('id' => $case['id'],
            'error' => get_class($e) . ': ' . $e->getMessage())), "\n";
    }
}
