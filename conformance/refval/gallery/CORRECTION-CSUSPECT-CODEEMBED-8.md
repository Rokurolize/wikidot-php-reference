# CORRECTION C-SUSPECT-CODEEMBED-8 — the Flickr failure message keeps live's literal (id: $s) (REFCORR4 lane, 2026-11-22)

Status: APPLIED in this tree. Both valid, stable and saved-source-matching probes muse-probe-suspect-codeembed-gs-flickr-substring and -gs-flickr-bare show live serving `Error fetching flickr image (id: $s) info. The file does not exist, is private or other problem.` where the reference interpolated an empty id from a failed anchored regex. This is a live-side unsprintf'd template that the reference follows, as the brief directs.

## The correction (reference)

Render/Xhtml/Gallery.php's failure branch now returns the literal template text instead of concatenating the undefined $photoId; the flickr: containment test, id regex and every other Gallery behavior are unchanged. Predecessor Render/Xhtml/Gallery.php.before-refcorr4 (SHA-256 656b462e77c848653469da851d86bd2a746a1b6e8754247834dfb746735d960b); corrected SHA-256 ab443e93f98797c1d302872cec2431031b49c6ceb859dcde5023af7b23bf1fa0. The stock harness lacks FlickrHandler, so the branch cannot be rendered end-to-end here; the correction is verified against the rule source and the two frozen live captures, with the harness limitation disclosed exactly as in the predecessor lane's report. No allowlist pattern is affected and no mirror consequence is owed for a literal failure string.
