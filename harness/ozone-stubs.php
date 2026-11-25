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

// REFCORR13 R13-AGY2 D13: the harness must hand the Freelink/Wikilink
// renderers a page ID (the fossil's `exists` value), and must be able to
// resolve that ID back to a RefPage carrying the authored page title. One
// deterministic ID function is shared by wikiPageExists(), selectByName()
// and selectByPrimaryKey() so the three lookups agree.
if (!function_exists('ref_page_id')) {
    function ref_page_id($page) { return 1000 + crc32($page) % 1000; }
}

// The pre-created live sandbox page whose special-character title minted the
// empty-pipe textFromTitle witnesses (muse-probe-agy-hunt-h06a). The page
// source is registered in ref_page_map(); the title lives here because the
// DB_PagePeer stub owns getTitleOrUnixName().
if (!isset($GLOBALS['REF_PAGE_TITLES'])) {
    $GLOBALS['REF_PAGE_TITLES'] = array(
        'muse-probe-agy-hunt-title-target' => 'Hunt\'s "Title" & <Test>',
    );
}

// Iftags page-context stub (R2-next stage, root-owned, disclosed in
// conformance-refphp/R2-NEXT.md). The harness injects a RefPage into
// $wiki->vars['page'] for cases that declare a "tags" array, so the fossil
// Iftags parse rule reads a deterministic tag set instead of dereferencing
// unset page state. Absent tags means an untagged page.
class RefPage {
    private $source;
    private $id;
    private $tags;
    private $title;
    private $name;
    public function __construct($source, $id, $tags = array(), $title = null, $name = '') {
        $this->source = $source;
        $this->id = $id;
        $this->tags = $tags;
        $this->title = $title;
        $this->name = $name;
    }
    public function getSource() { return $this->source; }
    public function getPageId() { return $this->id; }
    public function getTagsAsArray() { return $this->tags; }
    // REFCORR13 R13-AGY2 D13: the real DB_PagePeer returns the page's title
    // when it has one and its unix name otherwise.
    public function getTitleOrUnixName() {
        return $this->title !== null ? $this->title : $this->name;
    }
    // REFCORR19 F1 repair: the page's unix name is the URL segment the
    // file/image builders need (pageSegment() in Image.php/File.php asks
    // for it by these names). Without the accessors the helper fell back
    // to getTitleOrUnixName() and emitted the page TITLE as the segment.
    public function getUnixName() { return $this->name; }
    public function getName() { return $this->name; }
}

// Math parse rule throws this on \include / \input in an equation body; the
// fossil OZONE class is absent from the vendored snapshot, so the stub lets
// that branch be observed as a caught reference error rather than a fatal.
if (!class_exists('ProcessException')) {
    class ProcessException extends Exception {}
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
            $titles = $GLOBALS['REF_PAGE_TITLES'] ?? array();
            return new RefPage($pages[$pageName], ref_page_id($pageName), array(),
                $titles[$pageName] ?? null, $pageName);
        }
        return null;
    }
    // REFCORR13 R13-AGY2 D13: previously missing. The render rules call
    // selectByPrimaryKey($exists) for a textFromTitle freelink/wikilink.
    // REFCORR19 F9: the census's existence view is the full corpus set
    // (CENSUS_EXISTING_JSON -> REF_EXISTING_PAGES) and its titles are the
    // authored titles (CENSUS_TITLES_JSON -> REF_PAGE_TITLES), while REF_PAGES
    // holds only the ~10-page include/title closure. wikiPageExists() now
    // hands the render rules the page NAME as the existence value, so resolve
    // by name here and return a RefPage carrying that page's title. Never
    // return null for a page the existence callback declared: the render
    // rules dereference getTitleOrUnixName() unconditionally on that path,
    // and a null was the KO/JP/CN fatal (91/32/15 per 1000).
    public function selectByPrimaryKey($id) {
        $pages = $GLOBALS['REF_PAGES'] ?? array();
        $titles = $GLOBALS['REF_PAGE_TITLES'] ?? array();
        if (is_string($id)) {
            if (array_key_exists($id, $pages)) {
                return new RefPage($pages[$id], ref_page_id($id), array(),
                    $titles[$id] ?? null, $id);
            }
            $existing = $GLOBALS['REF_EXISTING_PAGES'] ?? array();
            if (in_array($id, $existing, true)) {
                return new RefPage('', ref_page_id($id), array(),
                    $titles[$id] ?? null, $id);
            }
            return null;
        }
        foreach ($pages as $name => $source) {
            if (ref_page_id($name) === (int) $id) {
                return new RefPage($source, (int) $id, array(),
                    $titles[$name] ?? null, $name);
            }
        }
        // Best-effort fallback for any caller still supplying a legacy
        // small-integer id for a corpus page outside REF_PAGES: the id is
        // lossy but a resolved name/title is still better than a fatal.
        $existing = $GLOBALS['REF_EXISTING_PAGES'] ?? array();
        foreach ($existing as $name) {
            if (ref_page_id((string) $name) === (int) $id) {
                return new RefPage('', (int) $id, array(),
                    $titles[$name] ?? null, (string) $name);
            }
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
            $titles = $GLOBALS['REF_PAGE_TITLES'] ?? array();
            return new RefPage($pages[$key], ref_page_id($key), array(),
                $titles[$key] ?? null, $key);
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
    public function setDensity($density) {}
    public function render($content, $hashcode) {}
}

// Module environment stubs (R2 module stage). The OZONE module classes are
// absent from this fossil snapshot, and module evaluation (what ListPages or
// Rate compute) is a serving-layer concern outside the R2 reference's scope.
// The fossil render rule only asks the environment two questions: can this
// site use the named module, and what is its template name. We model the
// standard-site case: available names (case-insensitive) take the fossil's
// \xFEmodule ... \xFE handoff marker (the serving layer would expand that
// marker, which we do not model); any other name takes the render rule's
// "does not exist" error-block path. REFCORR13 R13-AGY2 D14 extends the
// original nine-name allowlist by the nine additional standard modules
// measured live in REPORT-AGY-HUNT.md D14 (NewPage, ChildPages,
// PageCalendar, WantedPages, OrphanedPages, CountPages, Search, Members,
// Files). A name's real rendered body remains the external serving boundary;
// only the false "No such module" classification is corrected here.
// Genuinely absent names (PageTags, HelloWorld) still take the error path.
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
        // REFCORR13 R13-AGY2 D14: nine measured standard live modules.
        'newpage', 'childpages', 'pagecalendar', 'wantedpages',
        'orphanedpages', 'countpages', 'search', 'members', 'files',
        // REFCORR19 F3: the standing unregistered set. Their content is
        // produced at Wikidot's caller-runtime module layer; offline the
        // census driver emits no module body for them either, so registering
        // them removes the spurious "No such module" error block.
        'listusers', 'mailform', 'comments', 'themepreviewer',
        'whoinvited', 'recentthreads', 'recentposts', 'managesite',
        'forumcategory', 'forumnewthread', 'forumstart', 'forumthread',
        'frontforum', 'membershipapply', 'sitechanges', 'userinfo',
        'listdrafts', 'watchers', 'miniactivethreads', 'minirecentposts',
        'minirecentthreads',
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

// ============================================================================
// Criteria-drain harness stub package: user-dependent and external-media
// services (User/Image/Gallery render paths) + per-case stub-mediation log.
// Behavior matches live-observed Wikidot captures in conformance-agy-hunt and
// scp-wiki-translation; every case hitting any of these stubs is flagged via
// $GLOBALS['REF_STUBS_HIT'] so stub-mediated runs never mix silently with
// direct agreement.
// ============================================================================

$GLOBALS['REF_STUBS_HIT'] = array();

if (!function_exists('ref_reset_stubs')) {
    function ref_reset_stubs() {
        $GLOBALS['REF_STUBS_HIT'] = array();
    }
}

if (!function_exists('ref_record_stub')) {
    function ref_record_stub($name) {
        if (!isset($GLOBALS['REF_STUBS_HIT']) || !is_array($GLOBALS['REF_STUBS_HIT'])) {
            $GLOBALS['REF_STUBS_HIT'] = array();
        }
        if (!in_array($name, $GLOBALS['REF_STUBS_HIT'], true)) {
            $GLOBALS['REF_STUBS_HIT'][] = $name;
        }
    }
}

if (!function_exists('ref_stubs_hit')) {
    function ref_stubs_hit() {
        return $GLOBALS['REF_STUBS_HIT'] ?? array();
    }
}

if (!function_exists('ref_user_id')) {
    function ref_user_id($unixName) {
        return 100000 + (crc32((string) $unixName) & 0x7fffffff) % 9000000;
    }
}

class Criteria {
    private $conditions = array();
    private $orders = array();

    public function add($column, $value = null, $comparison = '=') {
        $this->conditions[$column] = array(
            'value' => $value,
            'comparison' => $comparison,
        );
    }

    public function addOrderAscending($column) {
        $this->orders[] = array('asc', $column);
    }

    public function addOrderDescending($column) {
        $this->orders[] = array('desc', $column);
    }

    public function getCondition($column, $default = null) {
        if (array_key_exists($column, $this->conditions)) {
            return $this->conditions[$column]['value'];
        }
        return $default;
    }
}

class RefOzoneUser {
    private $id;
    private $name;
    private $unixName;

    public function __construct($id, $name, $unixName) {
        $this->id = (int) $id;
        $this->name = (string) $name;
        $this->unixName = (string) $unixName;
    }

    public function getUserId() { return $this->id; }
    public function getName() { return $this->name; }
    public function getUnixName() { return $this->unixName; }
}

class DB_OzoneUserPeer {
    private static $inst = null;

    public static function instance() {
        if (self::$inst === null) {
            self::$inst = new DB_OzoneUserPeer();
        }
        return self::$inst;
    }

    public function selectOne($criteria) {
        ref_record_stub('user');
        $unixName = ($criteria instanceof Criteria)
            ? (string) $criteria->getCondition('unix_name', '')
            : '';
        if (isset($GLOBALS['REF_USERS']) && is_array($GLOBALS['REF_USERS'])
            && array_key_exists($unixName, $GLOBALS['REF_USERS'])) {
            $u = $GLOBALS['REF_USERS'][$unixName];
            if ($u === null || $u === false) {
                return null;
            }
            if ($u instanceof RefOzoneUser) {
                return $u;
            }
            if (is_array($u)) {
                return new RefOzoneUser(
                    $u['id'] ?? ref_user_id($unixName),
                    $u['name'] ?? $unixName,
                    $u['unix_name'] ?? $unixName
                );
            }
        }
        if ($unixName === '') {
            return null;
        }
        return new RefOzoneUser(ref_user_id($unixName), $unixName, $unixName);
    }
}

class WDRenderUtils {
    public static function renderUser($user, $options = array()) {
        $id = (int) $user->getUserId();
        $unix = htmlspecialchars((string) $user->getUnixName(), ENT_COMPAT, 'UTF-8');
        $name = htmlspecialchars((string) $user->getName(), ENT_COMPAT, 'UTF-8');
        $href = 'https://www.wikidot.com/user:info/' . $unix;
        $onclick = 'WIKIDOT.page.listeners.userInfo(' . $id . '); return false;';
        if (!empty($options['image'])) {
            return '<span class="printuser avatarhover"><a href="' . $href
                . '" onclick="' . $onclick . '"><img class="small" src="https://www.wikidot.com/avatar.php?userid='
                . $id . '&amp;amp;size=small&amp;amp;timestamp=0" alt="' . $name
                . '" style="background-image:url(https://www.wikidot.com/userkarma.php?u='
                . $id . ')" /></a><a href="' . $href . '" onclick="' . $onclick
                . '">' . $name . '</a></span>';
        }
        return '<span class="printuser"><a href="' . $href . '" onclick="'
            . $onclick . '">' . $name . '</a></span>';
    }
}

class RefFile {
    private $filename;

    public function __construct($filename) {
        $this->filename = (string) $filename;
    }

    public function getFilename() { return $this->filename; }
}

class DB_FilePeer {
    private static $inst = null;

    public static function instance() {
        if (self::$inst === null) {
            self::$inst = new DB_FilePeer();
        }
        return self::$inst;
    }

    private function lookupFiles($criteria) {
        $pageId = ($criteria instanceof Criteria) ? $criteria->getCondition('page_id', null) : null;
        if ($pageId !== null && isset($GLOBALS['REF_FILES']) && is_array($GLOBALS['REF_FILES'])
            && array_key_exists($pageId, $GLOBALS['REF_FILES'])) {
            $out = array();
            foreach ((array) $GLOBALS['REF_FILES'][$pageId] as $item) {
                $out[] = ($item instanceof RefFile) ? $item : new RefFile($item);
            }
            return $out;
        }
        return array();
    }

    public function selectOne($criteria) {
        ref_record_stub('file:first');
        $files = $this->lookupFiles($criteria);
        return empty($files) ? null : $files[0];
    }

    public function select($criteria) {
        ref_record_stub('file:gallery');
        return $this->lookupFiles($criteria);
    }
}

class FlickrHandler {
    private static $inst = null;

    public static function instance() {
        if (self::$inst === null) {
            self::$inst = new FlickrHandler();
        }
        return self::$inst;
    }

    public function photos_getInfo($photoId, $secret = null) {
        ref_record_stub('flickr');
        if (isset($GLOBALS['REF_FLICKR']) && is_array($GLOBALS['REF_FLICKR'])
            && array_key_exists($photoId, $GLOBALS['REF_FLICKR'])) {
            return $GLOBALS['REF_FLICKR'][$photoId];
        }
        return null;
    }

    public function buildPhotoURL($photo, $size = null) {
        if (is_array($photo) && isset($photo['_attributes']['server'], $photo['_attributes']['id'], $photo['_attributes']['secret'])) {
            return 'http://static.flickr.com/' . $photo['_attributes']['server'] . '/'
                . $photo['_attributes']['id'] . '_' . $photo['_attributes']['secret'] . '.jpg';
        }
        return '';
    }
}
