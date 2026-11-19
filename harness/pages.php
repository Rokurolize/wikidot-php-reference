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
    );
}
