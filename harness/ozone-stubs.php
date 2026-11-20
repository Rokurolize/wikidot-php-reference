<?php
// OZONE environment stubs for the standalone reference implementation.
//
// The vendored Text_Wiki rules reach three environment services:
//   - Ozone::getRunData()->getTemp('site')   (Include rule, Math renders)
//   - DB_PagePeer::instance()->selectByName  (Include rule page fetch)
//   - global helpers _() (gettext) and mkdirfull() (OZONE functions.php)
// In production these are the database and the request runtime. In the
// reference they are an in-memory page map ($GLOBALS['REF_PAGES'], name =>
// source), the exact counterpart of the MapIncluder used by the G1.4
// conformance driver on the ftml side. R2 wires the page map to the
// differential corpora.

if (!function_exists('_')) {
    function _($s) { return $s; }
}
if (!function_exists('mkdirfull')) {
    function mkdirfull($dir) {
        if (!file_exists($dir)) {
            mkdir($dir, 0777, true);
        }
    }
}

class RefPage {
    private $source;
    private $id;
    public function __construct($source, $id) {
        $this->source = $source;
        $this->id = $id;
    }
    public function getSource() { return $this->source; }
    public function getPageId() { return $this->id; }
}

class RefSite {
    public function getSiteId() { return 1; }
    public function getLocalFilesPath() {
        return WIKIDOT_ROOT . '/tmp';
    }
}

class RefRunData {
    public function getTemp($key) {
        if ($key === 'site') {
            return new RefSite();
        }
        return null;
    }
}

class Ozone {
    public static function getRunData() {
        return new RefRunData();
    }
}

class DB_PagePeer {
    private static $inst = null;
    public static function instance() {
        if (self::$inst === null) {
            self::$inst = new DB_PagePeer();
        }
        return self::$inst;
    }
    public function selectByName($siteId, $pageName) {
        $pages = $GLOBALS['REF_PAGES'] ?? array();
        if (array_key_exists($pageName, $pages)) {
            return new RefPage($pages[$pageName], 1000 + crc32($pageName) % 1000);
        }
        return null;
    }
    // Cross-site fetch for the reference's Include resolution
    // layer (R2 class C4): the page map keys site-qualified
    // pages by their Display form ":{site}:{page}", the same
    // key the G1.4 driver's MapIncluder uses.
    public function selectBySiteAndName($site, $pageName) {
        $key = ':' . $site . ':' . $pageName;
        $pages = $GLOBALS['REF_PAGES'] ?? array();
        if (array_key_exists($key, $pages)) {
            return new RefPage($pages[$key], 1000 + crc32($key) % 1000);
        }
        return null;
    }
}

// Math render drives an external LaTeX pipeline (OZONE's LatexRenderer
// writes a PNG per equation). That is image generation, outside the
// reference's parse-semantics scope. This no-op stub makes the render
// rule take its own fossil failure path (the "equation has not been
// processed correctly" error block) instead of fataling; the Math and
// Mathinline PARSE rules are unaffected and run for real.
class LatexRenderer {
    public function setTmpDir($dir) {}
    public function setOutputDir($dir) {}
    public function render($content, $hashcode) {}
}

// Module environment stubs (R2 module stage). The OZONE module classes are
// absent from this fossil snapshot, and module evaluation (what ListPages or
// Rate compute) is a serving-layer concern outside the R2 reference's scope.
// The fossil render rule only asks the environment two questions: can this
// site use the named module, and what is its template name. We model the
// standard-site case: the nine module names ftml recognizes (case-insensitive)
// are "available" and take the fossil's \xFEmodule ... \xFE handoff marker
// (the serving layer would expand that marker, which we do not model); any
// other name takes the render rule's own "does not exist" error-block path.
// This keeps the stage's in-scope comparison on the unknown-name and
// malformed-block display shapes without inventing module output.
class RefWikiSite {
    public function getUnixName() { return 'sandbox'; }
    public function getSiteId() { return 1; }
}
$GLOBALS['site'] = new RefWikiSite();

class ModuleManager {
    private static $inst = null;
    private static $available = array(
        'backlinks', 'categories', 'css', 'join', 'listpages',
        'pagetree', 'rate', 'redirect', 'tagcloud',
    );
    public static function instance() {
        if (self::$inst === null) {
            self::$inst = new ModuleManager();
        }
        return self::$inst;
    }
    public function canWikiUseModule($siteName, $moduleName) {
        return in_array(strtolower($moduleName), self::$available, true);
    }
    public function resolveWikiModuleName($moduleName) {
        return $moduleName;
    }
}
