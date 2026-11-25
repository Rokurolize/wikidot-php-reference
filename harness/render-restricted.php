<?php
// R4.6 restricted transform harness (carried over from R4.2 unchanged) (disclosed harness addition for
// the render-equivalence tier, modeled exactly on harness/batch.php's
// render branch and harness/state-restricted.php's construction):
// like batch.php render mode, but the wiki is constructed with ONLY
// the named rules, in the order given, so the render reflects a
// partial pipeline. This is the render counterpart of
// state-restricted.php and the counterpart of the restricted
// transform harness the coordinator used for the R4.1 pilot gate
// (REPORT-R4-VERIFY.md).
//
// Usage: php render-restricted.php Rule1,Rule2,...
//   stdin:  {"id": ..., "source": ..., "tags"?: [...]} per line
//   stdout: {"id": ..., "output": ...} per line, or
//           {"id": ..., "error": ...} on a thrown exception.
//   The output string is wire-encoded with the R3.3 encoding of
//   state-restricted.php (a string that is not valid UTF-8 crosses as
//   {"$bytes": [b0, ...]}), because a render can legitimately carry
//   the raw delimiter byte (Delimiter tokens) or other non-UTF-8
//   bytes that plain json_encode would silently drop.
//
// Per-case construction mirrors batch.php exactly: a fresh Text_Wiki
// per case built through ref_configure_wiki, the defensive
// footnote/bibliography var resets, a RefPage injected with the case's tags (always, empty
// when the case has none), and CRLF -> LF input normalization.
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
$GLOBALS['REF_EXISTING_PAGES'] = array_keys(ref_page_map());

function ref_wire_encode($v) {
    if (is_string($v)) {
        if (preg_match('//u', $v) === 1) {
            return $v;
        }
        return array('$bytes' => array_values(unpack('C*', $v)));
    }
    if (is_array($v)) {
        $out = array();
        foreach ($v as $k => $x) {
            $out[$k] = ref_wire_encode($x);
        }
        return $out;
    }
    return $v;
}

$rules = array_filter(array_map('trim', explode(',', $argv[1] ?? '')));
if (!$rules) {
    fwrite(STDERR, "usage: render-restricted.php Rule1,Rule2,...\n");
    exit(2);
}

while (($line = fgets(STDIN)) !== false) {
    $line = trim($line);
    if ($line === '') continue;
    $case = json_decode($line, true);
    $id = $case['id'];
    $src = $case['source'];
    $caseTags = (isset($case['tags']) && is_array($case['tags'])) ? $case['tags'] : array();
    $src = str_replace("\r\n", "\n", $src);
    try {
        $wiki = ref_configure_wiki(new Text_Wiki($rules));
        $wiki->vars['footnotes'] = array();
        $wiki->vars['bibitems'] = array();
        $wiki->vars['bibitemIds'] = array();
        $wiki->vars['page'] = new RefPage('', 0, $caseTags);
        $out = $wiki->transform($src, 'Xhtml');
        echo json_encode(ref_wire_encode(array('id' => $id, 'output' => $out))), "\n";
    } catch (Throwable $e) {
        echo json_encode(array('id' => $id,
            'error' => get_class($e) . ': ' . $e->getMessage())), "\n";
    }
}
