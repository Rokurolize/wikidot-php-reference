<?php
/**
 * Parses @@...@@ raw spans (R2 Form/Raw/Rawold corrected).
 *
 * The fossil used a single lazy regex, which could not express the live
 * Wikidot/ftml run shapes and cross-line closer. The corrected rule is a
 * left-to-right scanner over the source mirroring ftml's
 * parsing/rule/impls/raw.rs special cases, verified against live probes
 * (muse-probe-r2formraw-*, muse-probe-r2formraw2-*) and ftml's raw corpus pins:
 *
 *   @@body@@        -> Raw token with body (markup inside stays literal)
 *   @@@@            -> vanishes (empty raw)
 *   @@@@@           -> literal "@"
 *   @@@@@@          -> literal "@@"
 *   @@@x@@@         -> Raw token with body "@x", plus a literal "@"
 *   @@@@x@@@@       -> plain literal "x" (the two empty raws cancel)
 *   @@@@@x@@@@@     -> literal "@x@"
 *   @@\n@@          -> a single space (cross-line empty raw)
 *   @@x\n@@         -> Raw token with body "x" (cross-line close)
 *   @@x\ny@@        -> no match (a non-empty multi-line body aborts)
 *   unterminated @@ -> literal text
 */
class Text_Wiki_Parse_Raw extends Text_Wiki_Parse {

    public $regex = "/(?<!@)@@(.*[^@]?)@@/U"; // retained for inventory tools

    function parse()
    {
        $src = $this->wiki->source;
        $n = strlen($src);
        $out = '';
        $i = 0;
        while ($i < $n) {
            if ($src[$i] !== '@' || $i + 1 >= $n || $src[$i + 1] !== '@'
                || ($i > 0 && $src[$i - 1] === '@')) {
                $out .= $src[$i];
                $i++;
                continue;
            }
            $j = $i;
            while ($j < $n && $src[$j] === '@') $j++;
            $run = $j - $i;
            if ($run > 2) {
                // A run of four or more @ with no closer on its own line is
                // itself the whole construct (ftml's meta-raw special cases).
                // C-SUSPECT-RAWHEAD-1/4: a bare run of exactly three is NOT
                // consumed here — live keeps all three @ (bare-at3) and a
                // three-run still forms a cross-line raw when a closer exists
                // (xline-open3, xline-open3b). Only run>=4 keeps the
                // line-confined early exit. The kept count is $run for a bare
                // three-run and $run-4 otherwise (bare-at5/6/7).
                $close = strpos($src, '@@', $j);
                $nl = strpos($src, "\n", $j);
                $lineEnd = $nl === false ? $n : $nl;
                // REFCORR5 Batch 6, threshold corrected by REFCORR14: a 4+
                // run is its own empty-Raw construct even when a later @@
                // sits on the same line, provided that later run is itself
                // 2+ (the p22 forge shape @@@@@@123@@@@@@ and the W-EQ shape
                // @@@@a@@@b@@). A lone short closer with no later run stays
                // the scanner's literal trailing-@ shaping (trail-4).
                $closeRun = 0;
                if ($close !== false) {
                    $cr = $close;
                    while ($cr < $n && $src[$cr] === '@') { $closeRun++; $cr++; }
                }
                // REFCORR10, threshold corrected by REFCORR14: a closer run
                // of two or three bytes is only a final closer when no later
                // 2+ run follows on the same line. With a later run, the ftml
                // finish_double_at_raw re-association claims that later run
                // as the real closer and leaves the intervening text in a Raw
                // span (C-R5C-S1-2), so this opener must take the empty-Raw
                // early exit and be re-scanned rather than emitting the
                // short-run surplus here. Live W-EQ (`@@@@a@@@b@@`,
                // `<p>a<span style="white-space: pre-wrap;">@b</span></p>`)
                // shows the later run need only be two bytes; the old
                // `$q - $p >= 4` and the mirror's `4 <= n` were both too
                // strict and are lowered to two symmetrically.
                $laterQuad = false;
                if ($close !== false && $closeRun <= 3) {
                    $scan = $close + $closeRun;
                    while (($p = strpos($src, '@@', $scan)) !== false && $p < $lineEnd) {
                        $q = $p;
                        while ($q < $n && $src[$q] === '@') $q++;
                        if ($q - $p >= 2) { $laterQuad = true; break; }
                        $scan = $q;
                    }
                }
                if ($close === false || ($run >= 4 && ($close >= $lineEnd || $closeRun >= 4 || $laterQuad))) {
                    // REFCORR5 Batch 6 (C-RAW-COMPOSITE-1): a run of four or
                    // more @ is one empty Raw token (elided at render)
                    // followed by run-4 literal @ bytes, exactly once per
                    // run. A bare three-run stays literal with no token.
                    if ($run === 3) {
                        $out .= '@@@';
                    } else {
                        // REFCORR6: this empty Raw claims four @ bytes;
                        // the run's surplus is returned outside the token.
                        $out .= $this->wiki->addToken($this->rule, array('text' => ''), false, str_repeat('@', 4));
                        $out .= str_repeat('@', $run - 4);
                    }
                    $i = $j;
                    continue;
                }
            }
            // Find the closer: next @@ after the opener run. It may be on the
            // following line only if the body is empty (cross-line close).
            $close = strpos($src, '@@', $j);
            $k = $close === false ? $n : $close;
            while ($k < $n && $src[$k] === '@') $k++;
            $closeRun = $k - $close;
            $body = $close === false ? '' : substr($src, $j, $close - $j);
            if ($close === false) {
                $out .= substr($src, $i, $run);
                $i = $j;
                continue;
            }
            // Cross-line forms: @@\n@@ -> " ", @@x\n@@ -> Raw(x).
            // C-SUSPECT-RAWHEAD-2: a closer run of two or more on the next
            // line is a close; bytes beyond the first two are literal @
            // (xline-close3 -> one, xline-close4 -> two).
            // C-SUSPECT-RAWHEAD-3: the body must contain exactly one newline,
            // its trailing one; rtrim of several newlines is not live
            // (xline-two-nl and xline-empty2 abort instead of matching).
            // C-SUSPECT-RAWHEAD-4: a three-run opener's extra @ belongs to the
            // body (xline-open3/3b -> Raw("@x")); run>=4 never reaches here.
            if (substr($body, -1) === "\n" && substr_count($body, "\n") === 1
                && $closeRun >= 2) {
                $trimmed = substr($body, 0, -1);
                if ($trimmed === '') {
                    $out .= ' ';
                } else {
                    // $lead is assigned below the cross-line branch in the
                    // original scanner; recompute the opener's extra @ here.
                    $text = (($run - 2) === 1 ? '@' : '') . $trimmed;
                    // REFCORR6: exact consumed source span of the scanner.
                    $out .= $this->wiki->addToken($this->rule, array('text' => $text), false, substr($src, $i, $k - $i));
                }
                if ($closeRun > 2) {
                    // The consumed cross-line newline surfaces as one space
                    // before the literal extra @ (xline-close3/3b/4 and
                    // xline-close3-nospace: the space is present even with no
                    // source space after the closer run).
                    $out .= ' ';
                    $out .= str_repeat('@', $closeRun - 2);
                }
                $i = $k;
                continue;
            }
            // A newline anywhere else in the body aborts the construct.
            if (strpos($body, "\n") !== false) {
                $out .= substr($src, $i, $run);
                $i = $j;
                continue;
            }
            $lead = $run - 2;
            $trail = $closeRun - 2;
            if ($body === '') {
                $total = $run + $closeRun;
                if ($total <= 4) {
                    // @@@@ -> nothing
                } elseif ($total === 5) {
                    $out .= '@';
                } else {
                    $out .= str_repeat('@', $total - 4);
                }
                $i = $k;
                continue;
            }
            if ($lead >= 2) {
                // An empty raw immediately before the body cancels it: the
                // body becomes plain text, with extra @ emitted literally.
                $out .= str_repeat('@', max(0, $lead - 2));
                $out .= $body;
                // REFCORR8 C-R5-P3-1: a bare three-run closer after a
                // 4+ opener and plain body stays literal (the opener run
                // is already its own empty Raw); @@@@ZQ@@@ surfaces ZQ@@@.
                // REFCORR9 C-R5B-P3-1: the two-run closer sibling keeps both
                // of its bytes literal as well; @@@@ZQ@@ surfaces ZQ@@.
                // For a closer run of two or three bytes the literal count
                // equals the closer run length (trail + 2); longer runs keep
                // the established shed-four shaping.
                // REFCORR10 general surplus formula: a final closer run of
                // length c emits c literal bytes when c is two or three and
                // c-4 when c is four or more. In terms of trail = c-2 this
                // is trail<=1 ? trail+2 : trail-2, unchanged on every cached
                // bare case; it is factored out so the general rule is
                // explicit and shared with the mirror.
                $out .= str_repeat('@', $this->surplusCloser($closeRun));
            } elseif ($trail >= 2) {
                // The closer run is an empty raw plus an opener for whatever
                // follows; the body is still a raw span, and the extra @ are
                // left as literal text (live probe raw-adjacent).
                // REFCORR10: a three-run opener's extra @ belongs to the span
                // body in every branch, not just the plain-claim branch. With
                // a later 4+ run, lead=1 here (the short run re-scanned as the
                // opener) and the leading @ is body, giving @ B + two literal
                // @ after the later closer, exactly as live (C-R5C-S1-2).
                $text = ($lead === 1 ? '@' : '') . $body;
                $out .= $this->wiki->addToken($this->rule, array('text' => $text), false, substr($src, $i, $k - $i));
                $out .= str_repeat('@', $trail);
            } else {
                $text = ($lead === 1 ? '@' : '') . $body;
                $out .= $this->wiki->addToken($this->rule, array('text' => $text), false, substr($src, $i, $k - $i));
                if ($trail === 1) $out .= '@';
            }
            $i = $k;
        }
        $this->wiki->source = $out;
    }

    function process($matches) {
        $options = array('text' => $matches[1]);
        return $this->wiki->addToken($this->rule, $options, false, $matches[0]);
    }

    // REFCORR10: the general surplus-closer formula for a FINAL closer run of
    // length c after a 4+-opener body. Two- and three-byte runs stay fully
    // literal (the opener is already its own empty Raw); runs of four or more
    // shed four bytes as an empty Raw and leave c-4 literal. Derived from the
    // cached bare cases c=2 (ZQ@@), c=3 (ZQ@@@), c=4 (ZQ) and c=5 (@ZQ@).
    private function surplusCloser($closeRun) {
        $c = $closeRun;
        return $c <= 3 ? $c : max(0, $c - 4);
    }
}
