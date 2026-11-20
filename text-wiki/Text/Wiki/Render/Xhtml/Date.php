<?php
/**
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    $Id$
 * @link       http://pear.php.net/package/Text_Wiki
 */

/**
 * Iframe element.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Date extends Text_Wiki_Render {

    // The live Wikidot odate span carries a canonical timestamp class, an optional percent-encoded format class, and the statically formatted date text. The authored format never changes the visible text in live's Wikidot layout; it only changes the class.
    function token($options){
        $raw = isset($options['timestamp']) ? (string)$options['timestamp'] : '';
        if ($raw === '') return '';
        $timestamp = $this->canonicalTimestamp($raw);
        $format = isset($options['format']) ? (string)$options['format'] : '';
        $class = 'odate time_' . $timestamp;
        if ($format !== '') {
            $class .= ' format_' . $this->encodeFormat(str_replace('%g', 'ago', $format));
        }
        $text = $this->formatTimestamp($timestamp);
        return '<span class="' . $class . '">' . $text . '</span>';
     }

    // Live clamps an integer outside the signed 64-bit range to the nearest bound and drops leading zeros in the class, so the token timestamp is normalized before it is emitted or formatted.
    function canonicalTimestamp($raw){
        $negative = (strncmp($raw, '-', 1) === 0);
        if ($negative) $raw = substr($raw, 1);
        $digits = ltrim($raw, '0');
        if ($digits === '') $digits = '0';
        $bound = $negative ? '9223372036854775808' : '9223372036854775807';
        if (strlen($digits) > strlen($bound) || (strlen($digits) === strlen($bound) && strcmp($digits, $bound) > 0)) $digits = $bound;
        return ($negative && $digits !== '0' ? '-' : '') . $digits;
     }

    // The format class keeps only unreserved ASCII bytes and percent-encodes every other byte, with live's raw-escape placeholders represented as %FF<number>%FF.
    function encodeFormat($format){
        $out = '';
        $len = strlen($format);
        for ($i = 0; $i < $len; $i++) {
            $byte = $format[$i];
            if ($byte === '@' && $i + 1 < $len && $format[$i + 1] === '@') {
                $j = $i + 2;
                $digits = '';
                while ($j < $len && $format[$j] >= '0' && $format[$j] <= '9') { $digits .= $format[$j]; $j++; }
                if ($digits !== '' && $j + 1 < $len && $format[$j] === '@' && $format[$j + 1] === '@') {
                    $out .= '%FF' . $digits . '%FF';
                    $i = $j + 1;
                    continue;
                }
            }
            if (($byte >= 'A' && $byte <= 'Z') || ($byte >= 'a' && $byte <= 'z') || ($byte >= '0' && $byte <= '9') || $byte === '-' || $byte === '_' || $byte === '.' || $byte === '~') {
                $out .= $byte;
            } else {
                $out .= sprintf('%%%02X', ord($byte));
            }
        }
        return $out;
     }

    // Euclidean division and modulo keep the proleptic-Gregorian conversion exact at the signed 64-bit bounds, where PHP's ordinary arithmetic would overflow to a float.
    function floorDiv($a, $b){
        $quotient = intdiv($a, $b);
        return ($a % $b) < 0 ? $quotient - 1 : $quotient;
     }

    function floorMod($a, $b){
        $remainder = $a % $b;
        return $remainder < 0 ? $remainder + $b : $remainder;
     }

    // Live renders the default "%d %b %Y %H:%M" text in UTC even for timestamps outside the calendar range, using a proleptic Gregorian calendar for the extremes.
    function formatTimestamp($timestamp){
        $months = array('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec');
        $value = (int)$timestamp;
        $days = $this->floorDiv($value, 86400);
        $seconds = $this->floorMod($value, 86400);
        $z = $days + 719468;
        $era = $this->floorDiv($z, 146097);
        $dayOfEra = $z - $era * 146097;
        $yearOfEra = $this->floorDiv($dayOfEra - $this->floorDiv($dayOfEra, 1460) + $this->floorDiv($dayOfEra, 36524) - $this->floorDiv($dayOfEra, 146096), 365);
        $year = $yearOfEra + $era * 400;
        $dayOfYear = $dayOfEra - (365 * $yearOfEra + $this->floorDiv($yearOfEra, 4) - $this->floorDiv($yearOfEra, 100));
        $monthPrime = $this->floorDiv(5 * $dayOfYear + 2, 153);
        $day = $dayOfYear - $this->floorDiv(153 * $monthPrime + 2, 5) + 1;
        $month = $monthPrime < 10 ? $monthPrime + 3 : $monthPrime - 9;
        if ($month <= 2) $year += 1;
        $yearText = $year < 0 ? '-' . str_pad((string)(-$year), 4, '0', STR_PAD_LEFT) : str_pad((string)$year, 4, '0', STR_PAD_LEFT);
        return sprintf('%02d %s %s %02d:%02d', $day, $months[$month - 1], $yearText, $this->floorDiv($seconds, 3600), $this->floorDiv($this->floorMod($seconds, 3600), 60));
     }
 }
