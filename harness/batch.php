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
    if (function_exists('ref_reset_stubs')) {
        ref_reset_stubs();
    }
    // R2-next: optional per-case page tags for the Iftags rule, R2-notes:
    // always inject a page object, with an empty tag set when the case has no
    // "tags" array. The Iftags parse rule drops its whole body when vars['page']
    // is unset, so an absent page is NOT an untagged page; the earlier
    // if ($caseTags) guard mis-modelled live's untagged pages and was corrected
    // on the Bibliography owner's evidence (bib51/bib52, probes p11/p12),
    // disclosed in conformance-refphp/R2-NOTES.md. Root-owned stub.
    $caseTags = (isset($case['tags']) && is_array($case['tags'])) ? $case['tags'] : array();
    // Input stage: line-ending normalization (R2-INCLUDE.md C1).
    $src = str_replace("\r\n", "\n", $src);
    // Lone \r is NOT normalized here: it is still present at the
    // Include stage in the fossil's order (Prefilter, rule 2,
    // converts it afterwards), and the scanner/grammar split
    // treats it asymmetrically (see R2-INCLUDE.md C1).
    try {
        if ($mode === 'expand') {
            $wiki = new Text_Wiki(array('Include'));
            $wiki->vars['page'] = new RefPage('', 0, $caseTags);
            $wiki->parse($src);
            $out = $wiki->source;
            $resp = array('id' => $id, 'output' => $out);
            $stubsHit = function_exists('ref_stubs_hit') ? ref_stubs_hit() : array();
            if (!empty($stubsHit)) {
                $resp['stub_mediated'] = true;
                $resp['stubs'] = $stubsHit;
            }
            echo json_encode($resp), "\n";
        } elseif ($mode === 'tokens') {
            $wiki = ref_configure_wiki(new Text_Wiki());
            // R2-notes: defensive per-case reset of footnote/bibliography
            // document state. Text_Wiki::$vars is an instance property and
            // each case gets a fresh Text_Wiki, so no leak was observed. These
            // lines are behaviour-neutral insurance and are disclosed in
            // conformance-refphp/R2-NOTES.md.
            $wiki->vars['footnotes'] = array();
            $wiki->vars['bibitems'] = array();
            $wiki->vars['bibitemIds'] = array();
            $wiki->vars['page'] = new RefPage('', 0, $caseTags);
            $wiki->parse($src);
            $resp = array('id' => $id, 'output' => json_encode($wiki->tokens));
            $stubsHit = function_exists('ref_stubs_hit') ? ref_stubs_hit() : array();
            if (!empty($stubsHit)) {
                $resp['stub_mediated'] = true;
                $resp['stubs'] = $stubsHit;
            }
            echo json_encode($resp), "\n";
        } else {
            $wiki = ref_configure_wiki(new Text_Wiki());
            // R2-notes defensive per-case footnote/bibliography state reset
            // (see the tokens branch above and R2-NOTES.md for the audit).
            $wiki->vars['footnotes'] = array();
            $wiki->vars['bibitems'] = array();
            $wiki->vars['bibitemIds'] = array();
            $wiki->vars['page'] = new RefPage('', 0, $caseTags);
            $out = $wiki->transform($src, 'Xhtml');
            $resp = array('id' => $id, 'output' => $out);
            $stubsHit = function_exists('ref_stubs_hit') ? ref_stubs_hit() : array();
            if (!empty($stubsHit)) {
                $resp['stub_mediated'] = true;
                $resp['stubs'] = $stubsHit;
            }
            echo json_encode($resp), "\n";
        }
    } catch (Throwable $e) {
        $resp = array('id' => $id,
            'error' => get_class($e) . ': ' . $e->getMessage());
        $stubsHit = function_exists('ref_stubs_hit') ? ref_stubs_hit() : array();
        if (!empty($stubsHit)) {
            $resp['stub_mediated'] = true;
            $resp['stubs'] = $stubsHit;
        }
        echo json_encode($resp), "\n";
    }
}
