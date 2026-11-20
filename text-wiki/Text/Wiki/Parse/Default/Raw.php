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
                // A run of three or more @ with no separate closer is itself
                // the whole construct (ftml's meta-raw special cases).
                $close = strpos($src, '@@', $j);
                $nl = strpos($src, "\n", $j);
                $lineEnd = $nl === false ? $n : $nl;
                if ($close === false || $close >= $lineEnd) {
                    $out .= str_repeat('@', max(0, $run - 4));
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
            if (substr($body, -1) === "\n" && $closeRun === 2) {
                $trimmed = rtrim($body, "\n");
                if (strpos($trimmed, "\n") === false) {
                    if ($trimmed === '') {
                        $out .= ' ';
                    } else {
                        $out .= $this->wiki->addToken($this->rule, array('text' => $trimmed));
                    }
                    $i = $k;
                    continue;
                }
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
                $out .= str_repeat('@', max(0, $trail - 2));
            } elseif ($trail >= 2) {
                // The closer run is an empty raw plus an opener for whatever
                // follows; the body is still a raw span, and the extra @ are
                // left as literal text (live probe raw-adjacent).
                $out .= $this->wiki->addToken($this->rule, array('text' => $body));
                $out .= str_repeat('@', $trail);
            } else {
                $text = ($lead === 1 ? '@' : '') . $body;
                $out .= $this->wiki->addToken($this->rule, array('text' => $text));
                if ($trail === 1) $out .= '@';
            }
            $i = $k;
        }
        $this->wiki->source = $out;
    }

    function process($matches) {
        $options = array('text' => $matches[1]);
        return $this->wiki->addToken($this->rule, $options);
    }
}
