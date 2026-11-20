<?php
// R3 state driver, restricted-pipeline variant (disclosed harness
// addition for the R3 Lean mirroring, alongside batch.php; derived
// from probe-source.php). Where batch.php renders or expands, this
// driver exposes the parse-phase state pair itself: the post-parse
// source split into text segments and token references, plus the
// token table.
//
// Usage: php state-restricted.php Rule1,Rule2,...
//   stdin:  {"id": ..., "source": ...} per line (same JSONL protocol
//           as batch.php; the input stage normalizes CRLF to LF
//           exactly as batch.php and probe-source.php do).
//   stdout: {"id": ..., "segments": [...], "tokens": {...}} per line,
//           where a segment is {"t": "literal text"} or {"k": <id>}
//           with <id> the token's key in "tokens" (the process-global
//           Text_Wiki token id; consumers canonicalize by renumbering
//           per document in table order, per R3-SCOPE.md). Token
//           entries are [rule name, options] as stored by Text_Wiki.
//
// The wiki is constructed with ONLY the named rules, in the order
// given (the batch.php expand mode's subset construction is the
// in-tree precedent), so the state reflects a partial pipeline: the
// conformance oracle for an R3 stage whose runner implements exactly
// those rules.
//
// R3.3 protocol strengthening (disclosed harness change; the
// reference's behavior is untouched, only this driver's wire format
// changes): a token option value whose bytes are not valid UTF-8
// (in this pipeline, exactly the claimed texts that span an earlier
// rule's placeholder and so contain the delimiter byte 0xFF) used to
// make json_encode fail for the whole case, and both drivers then
// emitted an identical error record that the comparison counted as
// a pass with no content evidence (R3.2's PASS-UNREPRESENTABLE).
// Such a string is now encoded, recursively, as
// {"$bytes": [b0, b1, ...]} (the list of its byte values), a shape
// no genuine option value can take: option keys in the reference's
// parse rules are fixed ASCII identifiers chosen by the rule
// authors, and no rule builds a single-key "$bytes" map or a bare
// integer-list option value. Valid-UTF-8 strings cross as ordinary
// JSON strings, so the encoding is a function of the byte content
// alone and is injective on the value space: two distinct byte
// strings either decode to two distinct JSON strings (UTF-8
// decoding is injective on valid encodings), or at least one is
// encoded as a byte list distinct from any string and from any
// other byte list. The Lean driver applies the identical rule at
// its serialization layer (TokenState.lean's serOptVal), and the
// comparison tool (conformance compare.py) decodes the shape back
// to a byte string, canonicalizing placeholder indices inside it
// through the same per-document renumbering as segment references.
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

// R3.3 wire encoding (see the header note): recursively replace any
// string that is not valid UTF-8 with {"$bytes": [byte values]}.
// Array keys are not transformed: every key in the output structure
// is either created by this driver or is a parse rule's option name,
// all ASCII identifiers, hence always valid UTF-8.
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
    fwrite(STDERR, "usage: state-restricted.php Rule1,Rule2,...\n");
    exit(2);
}

while (($line = fgets(STDIN)) !== false) {
    $line = trim($line);
    if ($line === '') continue;
    $case = json_decode($line, true);
    $id = $case['id'];
    // Input stage: line-ending normalization (R2-INCLUDE.md C1), as
    // in batch.php and probe-source.php.
    $src = str_replace("\r\n", "\n", $case['source']);
    try {
        $wiki = new Text_Wiki($rules);
        $wiki->vars['page'] = new RefPage('', 0, array());
        $wiki->parse($src);
        // Split the post-parse source on the delimiter byte: parts
        // alternate text / token id / text / ... / text.
        $parts = explode($wiki->delim, $wiki->source);
        $segments = array();
        foreach ($parts as $i => $part) {
            if ($i % 2 === 0) {
                $segments[] = array('t' => $part);
            } else {
                $segments[] = array('k' => (int)$part);
            }
        }
        $out = ref_wire_encode(array('id' => $id, 'segments' => $segments,
            'tokens' => $wiki->tokens));
        $json = json_encode($out);
        if ($json === false) {
            echo json_encode(array('id' => $id,
                'error' => 'json_encode failed: ' . json_last_error_msg())), "\n";
        } else {
            echo $json, "\n";
        }
    } catch (Throwable $e) {
        echo json_encode(array('id' => $id,
            'error' => get_class($e) . ': ' . $e->getMessage())), "\n";
    }
}
