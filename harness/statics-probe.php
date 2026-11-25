<?php
// REFCORR23 two-documents-one-process probe. Unlike batch.php this
// driver deliberately performs no per-document static resets: it renders
// document B alone in one invocation, or document A followed by document B
// in a second invocation, with a fresh Text_Wiki object for each document.
// Comparing the two B outputs is the R1-style process-isolation pin.
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

$scenarios = array(
    'collapsible' => array(
        'a' => "[[collapsible]]\nseed\n[[/collapsible]]",
        'b' => "[[collapsible]]\nsecond\n[[/collapsible]]",
    ),
    'collapsible-wire' => array(
        'a' => "[[collapsible]]\nsame\n[[/collapsible]]",
        'b' => "[[collapsible]]\nsame\n[[/collapsible]]",
        'wire' => true,
    ),
    'tabview' => array(
        'a' => "[[tabview]]\n[[tab Seed]]\nseed\n[[/tab]]\n[[/tabview]]",
        'b' => "[[tabview]]\n[[tab Second]]\nsecond\n[[/tab]]\n[[/tabview]]",
    ),
    'math' => array(
        'a' => "[[math eq]]\nx\n[[/math]]",
        'b' => "ref [[eref eq]]",
    ),
    'newline' => array(
        'a' => "[[div]]\nseed\n[[/div]]\n[[table]]\n[[row]]\n[[cell]]\na\n[[/cell]]\n[[/row]]\n[[/table]]",
        'b' => "[[div]]\nx\n[[/div]]\n[[table]]\n[[row]]\n[[cell]]\ny\n[[/cell]]\n[[/row]]\n[[/table]]",
    ),
    'freelink' => array(
        'a' => "[[[Łukasz|person]]]",
        'b' => "[[[Αθήνα|city]]]",
    ),
    'heading' => array(
        'a' => "+ Seed",
        'b' => "+ Alpha\n\n+ Beta",
    ),
    'mathinline' => array(
        'a' => "[[$x [[date 0]] y$]]",
        'b' => "[[$a [[date 0]] b$]]",
    ),
    'code-highlighter' => array(
        'a' => "[[code type=\"php\"]]\n<?php echo \"a\";\n[[/code]]",
        'b' => "[[code type=\"php\"]]\n<?php echo \"b\";\n[[/code]]",
    ),
    'pagepeer' => array(
        'a' => "[[include muse-probe-g14-target]]",
        'b' => "[[[muse-probe-agy-hunt-title-target|]]]",
    ),
    'userpeer' => array(
        'a' => "[[user Rokurolize]]",
        'b' => "[[user Rokurolize]]",
    ),
    'filepeer' => array(
        'a' => "[[gallery]]",
        'b' => "[[gallery]]",
        'pageName' => 'muse-probe-g14-target',
    ),
    'flickrhandler' => array(
        'a' => "[[image flickr:123]]",
        'b' => "[[image flickr:124]]",
    ),
    'modulemanager' => array(
        'a' => "[[module Rate]]",
        'b' => "[[module Rate]]",
    ),
);

$scenario = isset($argv[1]) ? $argv[1] : '';
$mode = isset($argv[2]) ? $argv[2] : '';
if (!isset($scenarios[$scenario]) || !in_array($mode, array('solo', 'pair'), true)) {
    fwrite(STDERR, "usage: statics-probe.php SCENARIO solo|pair\n");
    exit(2);
}

function ref_statics_render($source, $pageName, $wire = false) {
    $GLOBALS['REF_STATICS_WIRE'] = $wire;
    $wiki = ref_configure_wiki(new Text_Wiki());
    $wiki->vars['footnotes'] = array();
    $wiki->vars['bibitems'] = array();
    $wiki->vars['bibitemIds'] = array();
    $wiki->vars['page'] = new RefPage('', 0, array());
    if ($pageName !== null) {
        $wiki->vars['pageName'] = $pageName;
    }
    $out = $wiki->transform($source, 'Xhtml');
    $facts = array(
        'collapsible_counts' => array(),
        'tabview_ids' => array(),
        'equations' => array(),
        'stub_hits' => function_exists('ref_stubs_hit') ? ref_stubs_hit() : array(),
    );
    foreach ($wiki->tokens as $tok) {
        if ($tok[0] === 'Collapsible' && isset($tok[1]['type'])
            && $tok[1]['type'] === 'start' && array_key_exists('count', $tok[1])) {
            $facts['collapsible_counts'][] = $tok[1]['count'];
        }
        if ($tok[0] === 'Tabview' && isset($tok[1]['tabviewId'])) {
            $facts['tabview_ids'][] = $tok[1]['tabviewId'];
        }
    }
    if (isset($wiki->vars['equationsArray']) && is_array($wiki->vars['equationsArray'])) {
        $facts['equations'] = $wiki->vars['equationsArray'];
    }
    if (!empty($GLOBALS['REF_STATICS_WIRE'])) {
        $facts['tokens_json'] = json_encode($wiki->tokens, JSON_INVALID_UTF8_SUBSTITUTE);
        $facts['tokens_sha256'] = hash('sha256', $facts['tokens_json']);
    }
    return array('output' => $out, 'facts' => $facts, 'wiki' => $wiki);
}

$spec = $scenarios[$scenario];
$pageName = isset($spec['pageName']) ? $spec['pageName'] : null;
$result = array('scenario' => $scenario, 'mode' => $mode);
if ($mode === 'pair') {
    $wire = !empty($spec['wire']);
    $a = ref_statics_render($spec['a'], $pageName, $wire);
    $result['a_output'] = $a['output'];
    $result['a_facts'] = $a['facts'];
}
$b = ref_statics_render($spec['b'], $pageName, isset($wire) ? $wire : !empty($spec['wire']));
$result['b_output'] = $b['output'];
$result['b_facts'] = $b['facts'];
echo json_encode($result, JSON_INVALID_UTF8_SUBSTITUTE), "\n";
