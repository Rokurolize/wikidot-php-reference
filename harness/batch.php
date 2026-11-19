<?php
// Batch driver for the reference implementation, same JSONL protocol
// as the ftml-side conformance drivers:
//   stdin:  {"id": ..., "source": ...} per line
//   stdout: {"id": ..., "output": ...} or {"id": ..., "error": ...}
// Modes:
//   expand: run ONLY the Include rule's parse over the source and
//           print the expanded source (the counterpart of ftml's
//           include() output, comparable to the G1.4 driver).
//   render: full transform to Xhtml.
//   tokens: full parse, print the token array as JSON in "output".
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

$mode = $argv[1] ?? 'expand';
$GLOBALS['REF_PAGES'] = ref_page_map();
$GLOBALS['REF_EXISTING_PAGES'] = array_keys(ref_page_map());

while (($line = fgets(STDIN)) !== false) {
    $line = trim($line);
    if ($line === '') continue;
    $case = json_decode($line, true);
    $id = $case['id'];
    $src = $case['source'];
    // Input stage: line-ending normalization (R2-INCLUDE.md C1).
    $src = str_replace("\r\n", "\n", $src);
    // Lone \r is NOT normalized here: it is still present at the
    // Include stage in the fossil's order (Prefilter, rule 2,
    // converts it afterwards), and the scanner/grammar split
    // treats it asymmetrically (see R2-INCLUDE.md C1).
    try {
        if ($mode === 'expand') {
            $wiki = new Text_Wiki(array('Include'));
            $wiki->parse($src);
            $out = $wiki->source;
            echo json_encode(array('id' => $id, 'output' => $out)), "\n";
        } elseif ($mode === 'tokens') {
            $wiki = ref_configure_wiki(new Text_Wiki());
            $wiki->parse($src);
            echo json_encode(array('id' => $id,
                'output' => json_encode($wiki->tokens))), "\n";
        } else {
            $wiki = ref_configure_wiki(new Text_Wiki());
            $out = $wiki->transform($src, 'Xhtml');
            echo json_encode(array('id' => $id, 'output' => $out)), "\n";
        }
    } catch (Throwable $e) {
        echo json_encode(array('id' => $id,
            'error' => get_class($e) . ': ' . $e->getMessage())), "\n";
    }
}
