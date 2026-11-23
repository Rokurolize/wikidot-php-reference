<?php
// The reference harness page map: name => source, the counterpart of
// the page set in the G1.4/G1.4b conformance drivers on the ftml side
// (MapIncluder). Keys are the names the Include rule looks up AFTER
// WDStringUtils::toUnixName normalization; see R2-INCLUDE.md for the
// site-ref key once observed.
function ref_page_map() {
    return array(
        'muse-probe-g14-target' =>
            "TARGET-CONTENT-START\nValue is {\$marker}.\nTARGET-CONTENT-END",
        'other-page' =>
            "OTHER-PAGE-CONTENT\nSecond value is {\$marker}.\nOTHER-END",
        'empty-page' => "",
        ':sandbox:other-page' => "SITE-PAGE-CONTENT",
        'muse-probe-g14b-target' =>
            "A is {\$a}.\nB is {\$b}.\nM is {\$marker}.\nTARGET-END",
        // R2-link stage: the two sandbox pages created under the Freelink
        // prefix muse-probe-r2link-free- whose existence the reference's
        // wikiPageExists() callback must mirror. Adding them to this map
        // also makes them includable, which is harmless; the map keys are
        // already unix-normalized (verified with WDStringUtils::toUnixName).
        // Root-owned stub, disclosed in conformance-refphp/R2-LINK.md.
        'muse-probe-r2link-free-exists' => "FREELINK TARGET ONE",
        'muse-probe-r2link-free-exists2' => "FREELINK TARGET TWO",
        // REFCORR13 R13-AGY2 D13: the pre-created live sandbox target used by
        // muse-probe-agy-hunt-h06a; its authored title is registered in
        // ozone-stubs.php's REF_PAGE_TITLES so a textFromTitle freelink
        // resolves it instead of falling back to `newpage` + slug.
        'muse-probe-agy-hunt-title-target' => "Title target",
        // R2-notes stage: the run-owned include target used by root's focused
        // include-content probe (muse-probe-r2notes-x-inc-holder). Its source is
        // byte-identical to the live sandbox page muse-probe-r2notes-x-inc-src,
        // so the reference's Include rule sees the same footnote body live does
        // and the document-order numbering seam can be compared. Root-owned
        // stub, disclosed in conformance-refphp/R2-NOTES.md.
        'muse-probe-r2notes-x-inc-src' =>
            "included [[footnote]]from include[[/footnote]] text",
    );
}
