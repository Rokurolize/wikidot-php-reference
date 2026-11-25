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
        // R3.12 disclosed driver change: the wiki is constructed
        // through ref_configure_wiki exactly as batch.php,
        // prefix-source.php and probe-source.php construct it,
        // because Interwiki's parse reads the 'sites' parse
        // configuration (the only parse-conf key
        // ref_configure_wiki sets) as its standalone-claim gate;
        // an unconfigured wiki here would silently drop every
        // standalone interwiki claim the configured pipeline
        // makes. No other rule in the pipeline reads a parse-conf
        // key that ref_configure_wiki sets (each reads its own
        // class defaults), so earlier stages' slices are
        // unaffected; the stage's regression runs verify that.
        $wiki = ref_configure_wiki(new Text_Wiki($rules));
        // R3.4 disclosed driver change: the per-case page is constructed
        // exactly as harness/batch.php constructs it (the case's "tags"
        // array, always injected, empty when the case has none), because
        // Iftags reads vars['page']->getTagsAsArray(); an empty page
        // object here would silently drop every positively tagged body.
        // Math's equations map is a process-wide static, reset per case
        // exactly as batch.php resets it, so cases cannot leak into
        // each other.
        $caseTags = (isset($case['tags']) && is_array($case['tags'])) ? $case['tags'] : array();
        $wiki->vars['page'] = new RefPage('', 0, $caseTags);
        Text_Wiki_Parse_Math::$equationsArray = array();
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
        // R3.4 disclosed compared-state extension: Math's equations map
        // (label => id pairs, in insertion order) and the math_id
        // counter join the compared state for this stage, serialized
        // identically on the Lean side. Earlier stages' slices carry
        // the same two fields with their empty values (the map empty,
        // the counter null) because Math never runs there.
        $equations = array();
        foreach (Text_Wiki_Parse_Math::$equationsArray as $label => $mid) {
            $equations[] = array((string) $label, $mid);
        }
        // R3.6 disclosed compared-state extension (second in the R3.4
        // pattern): the NOTES family's document state joins the
        // compared state, serialized identically on the Lean side.
        // "footnotes" is vars['footnotes'] in index order (Footnote
        // appends each claimed body; Footnoteblock reads the list);
        // "bibitems" and "bibitemIds" are vars['bibitems'] and
        // vars['bibitemIds'] as (label, value) pairs in insertion
        // order (Bibitem writes both; Bibliography and Bibcite read
        // them). A var the pipeline never touched reads as the empty
        // list, matching the model's per-document initial values.
        // The state lives in the per-case Text_Wiki instance's vars,
        // so no cross-case reset is needed (the R2 NOTES harness
        // audit verified the family's state does not leak).
        $footnotes = array();
        if (isset($wiki->vars['footnotes']) && is_array($wiki->vars['footnotes'])) {
            foreach ($wiki->vars['footnotes'] as $fnBody) {
                $footnotes[] = $fnBody;
            }
        }
        $bibitems = array();
        if (isset($wiki->vars['bibitems']) && is_array($wiki->vars['bibitems'])) {
            foreach ($wiki->vars['bibitems'] as $label => $content) {
                $bibitems[] = array((string) $label, $content);
            }
        }
        $bibitemIds = array();
        if (isset($wiki->vars['bibitemIds']) && is_array($wiki->vars['bibitemIds'])) {
            foreach ($wiki->vars['bibitemIds'] as $label => $bid) {
                $bibitemIds[] = array((string) $label, $bid);
            }
        }
        // R3.17 disclosed compared-state extension (third in the
        // R3.4 pattern): the Anchor rule's scored-anchor registry
        // joins the compared state, serialized identically on the
        // Lean side. "scoredAnchors" is vars['scored_anchors'] as
        // (end placeholder, start placeholder) pairs in insertion
        // order (Anchor's element pass writes one pair per scored
        // anchor it claims in the simple path; Paragraph's process
        // reads the map for its PG-F1 wrapper suppression). A
        // pipeline in which Anchor never runs leaves the var
        // unset or empty, matching the model's per-document
        // initial value (the empty list).
        $scoredAnchors = array();
        if (isset($wiki->vars['scored_anchors']) && is_array($wiki->vars['scored_anchors'])) {
            foreach ($wiki->vars['scored_anchors'] as $endTok => $startTok) {
                $scoredAnchors[] = array($endTok, $startTok);
            }
        }
        // CAPSTONE disclosed compared-state extension (fourth in the
        // R3.4 pattern): the Include rule's registries join the
        // compared state, serialized identically on the Lean side.
        // "inclusions" is vars['inclusions'] as the ordered list of
        // fired includes' page ids (the var is an id => id map in
        // first-insertion order; Include's refFetch writes it), and
        // "inclusionsNotExist" is vars['inclusionsNotExist'] as the
        // ordered list of missing includes' display names (a
        // display => display map in first-insertion order). A
        // pipeline in which Include never runs leaves both vars
        // unset, matching the model's per-document initial values
        // (the empty lists). Before this extension the driver
        // emitted neither key, which made any comparison that
        // forces the inclusion components (the CAPSTONE retirement
        // check's section 3) unsatisfiable against fresh runs.
        $inclusions = array();
        if (isset($wiki->vars['inclusions']) && is_array($wiki->vars['inclusions'])) {
            foreach ($wiki->vars['inclusions'] as $incId) {
                $inclusions[] = $incId;
            }
        }
        $inclusionsNotExist = array();
        if (isset($wiki->vars['inclusionsNotExist']) && is_array($wiki->vars['inclusionsNotExist'])) {
            foreach ($wiki->vars['inclusionsNotExist'] as $incName) {
                $inclusionsNotExist[] = $incName;
            }
        }
        $out = ref_wire_encode(array('id' => $id, 'segments' => $segments,
            'tokens' => $wiki->tokens, 'equations' => $equations,
            'mathId' => isset($wiki->vars['math_id']) ? $wiki->vars['math_id'] : null,
            'footnotes' => $footnotes, 'bibitems' => $bibitems,
            'bibitemIds' => $bibitemIds, 'scoredAnchors' => $scoredAnchors,
            'inclusions' => $inclusions,
            'inclusionsNotExist' => $inclusionsNotExist));
        $json = json_encode($out);
        if ($json === false) {
            echo json_encode(array('id' => $id,
                'error' => 'json_encode failed: ' . json_last_error_msg())), "\n";
        } else {
            echo $json, "\n";
        }
    } catch (ProcessException $e) {
        // R3.4 PARSE-FATAL protocol: Math's guard throws ProcessException
        // ("Invalid LaTeX expression(s) found.") and the whole parse
        // aborts; the case's record is the fatal record, the same shape
        // the full-pipeline fixture files use, and the Lean driver emits
        // the identical record when the mirror's guard predicate fires.
        echo json_encode(array('id' => $id,
            'fatal' => get_class($e) . ': ' . $e->getMessage())), "\n";
    } catch (Throwable $e) {
        echo json_encode(array('id' => $id,
            'error' => get_class($e) . ': ' . $e->getMessage())), "\n";
    }
}
