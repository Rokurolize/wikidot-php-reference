<?php
/**
 * REFCORR19 F10: [[#expr]] evaluation.
 *
 * The corpus's expression forms are arithmetic over integer literals plus
 * the Wikidot page variables (%%rating%%, {$amt}, ...) that the offline
 * harness cannot resolve. FTML's census driver reports those as
 * `syntax error near \`<token>\``; this evaluator reproduces that form and
 * evaluates the literal arithmetic the live probe battery uses (ordinary
 * precedence, parentheses, abs(), + - * / %).
 *
 * This is a parse-time rule: it replaces the construct with its result in
 * the source, so any markup in an ifexpr branch is still parsed by the
 * rules that follow.
 */

class Text_Wiki_Parse_Expr extends Text_Wiki_Parse {

    public $regex = '/\[\[#expr\s+([^\]]*?)\]\]/i';

    function process($matches)
    {
        return self::evaluate($matches[1]);
    }

    /** Public entry point shared with the Ifexpr rule. */
    public static function evaluate($expression)
    {
        $tokens = self::tokenize($expression);
        if (is_string($tokens)) {
            return $tokens;
        }
        $pos = 0;
        $value = self::parseSum($tokens, $pos);
        if (is_string($value)) {
            return $value;
        }
        if ($pos !== count($tokens)) {
            return 'syntax error near `' . self::near($tokens[$pos]) . '`';
        }
        return (string) $value;
    }

    /** Evaluate a condition; returns array(value_or_error, truth). */
    public static function condition($expression)
    {
        // Comparison operators are evaluated at the top level only.
        foreach (array('==', '!=', '>=', '<=', '>', '<') as $op) {
            $parts = self::splitTop($expression, $op);
            if ($parts !== null) {
                $a = self::evaluate($parts[0]);
                $b = self::evaluate($parts[1]);
                if (!is_numeric($a) || !is_numeric($b)) {
                    return array($a, false);
                }
                $a = (float) $a;
                $b = (float) $b;
                switch ($op) {
                    case '==': $v = $a == $b; break;
                    case '!=': $v = $a != $b; break;
                    case '>=': $v = $a >= $b; break;
                    case '<=': $v = $a <= $b; break;
                    case '>':  $v = $a > $b; break;
                    default:   $v = $a < $b; break;
                }
                return array($v ? '1' : '0', $v);
            }
        }
        $v = self::evaluate($expression);
        return array($v, is_numeric($v) && (float) $v != 0);
    }

    private static function near($token)
    {
        $s = is_array($token) ? (string) $token[1] : (string) $token;
        return substr($s, 0, 10);
    }

    private static function splitTop($text, $op)
    {
        $depth = 0;
        $len = strlen($text);
        $olen = strlen($op);
        for ($i = 0; $i < $len; $i++) {
            $c = $text[$i];
            if ($c === '(' || $c === '[' || $c === '{') {
                $depth++;
            } elseif ($c === ')' || $c === ']' || $c === '}') {
                $depth--;
            } elseif ($depth === 0 && substr($text, $i, $olen) === $op) {
                return array(substr($text, 0, $i), substr($text, $i + $olen));
            }
        }
        return null;
    }

    private static function tokenize($text)
    {
        $out = array();
        $i = 0;
        $len = strlen($text);
        while ($i < $len) {
            $c = $text[$i];
            if (ctype_space($c)) {
                $i++;
                continue;
            }
            if (ctype_digit($c) || ($c === '.' && $i + 1 < $len && ctype_digit($text[$i + 1]))) {
                preg_match('/[0-9]*\.?[0-9]+/', substr($text, $i), $m);
                $out[] = array('num', $m[0]);
                $i += strlen($m[0]);
                continue;
            }
            if (ctype_alpha($c) || $c === '_' || $c === '%' || $c === '$' || $c === '{' || $c === '}') {
                preg_match('/[A-Za-z0-9_%${}\-]+/', substr($text, $i), $m);
                $out[] = array('ident', $m[0]);
                $i += strlen($m[0]);
                continue;
            }
            if (strpos('+-*/%()', $c) !== false) {
                $out[] = array('op', $c);
                $i++;
                continue;
            }
            return 'syntax error near `' . substr($text, $i, 10) . '`';
        }
        return $out;
    }

    private static function parseSum($tokens, &$pos)
    {
        $left = self::parseProduct($tokens, $pos);
        if (is_string($left)) {
            return $left;
        }
        while ($pos < count($tokens) && $tokens[$pos][0] === 'op'
               && ($tokens[$pos][1] === '+' || $tokens[$pos][1] === '-')) {
            $op = $tokens[$pos++][1];
            $right = self::parseProduct($tokens, $pos);
            if (is_string($right)) {
                return $right;
            }
            $left = $op === '+' ? $left + $right : $left - $right;
        }
        return $left;
    }

    private static function parseProduct($tokens, &$pos)
    {
        $left = self::parseUnary($tokens, $pos);
        if (is_string($left)) {
            return $left;
        }
        while ($pos < count($tokens) && $tokens[$pos][0] === 'op'
               && in_array($tokens[$pos][1], array('*', '/', '%'), true)) {
            $op = $tokens[$pos++][1];
            $right = self::parseUnary($tokens, $pos);
            if (is_string($right)) {
                return $right;
            }
            if (($op === '/' || $op === '%') && (float) $right == 0) {
                return 'division by zero';
            }
            $left = $op === '*' ? $left * $right : ($op === '/' ? $left / $right : $left % $right);
        }
        return $left;
    }

    private static function parseUnary($tokens, &$pos)
    {
        if ($pos < count($tokens) && $tokens[$pos][0] === 'op'
            && ($tokens[$pos][1] === '-' || $tokens[$pos][1] === '+')) {
            $sign = $tokens[$pos++][1];
            $v = self::parseUnary($tokens, $pos);
            return is_string($v) ? $v : ($sign === '-' ? -$v : $v);
        }
        if ($pos >= count($tokens)) {
            return 'syntax error';
        }
        $t = $tokens[$pos];
        if ($t[0] === 'num') {
            $pos++;
            return $t[1] + 0;
        }
        if ($t[0] === 'op' && $t[1] === '(') {
            $pos++;
            $v = self::parseSum($tokens, $pos);
            if (is_string($v)) {
                return $v;
            }
            if ($pos >= count($tokens) || $tokens[$pos][1] !== ')') {
                return 'syntax error near `)`';
            }
            $pos++;
            return $v;
        }
        if ($t[0] === 'ident') {
            if (strtolower($t[1]) === 'abs') {
                $pos++;
                if ($pos < count($tokens) && $tokens[$pos][1] === '(') {
                    $pos++;
                    $v = self::parseSum($tokens, $pos);
                    if (is_string($v)) {
                        return $v;
                    }
                    if ($pos < count($tokens) && $tokens[$pos][1] === ')') {
                        $pos++;
                    }
                    return abs($v);
                }
                return 'syntax error near `abs`';
            }
            // Unresolved Wikidot variable: report it the way FTML does.
            return 'syntax error near `' . self::near($t) . '`';
        }
        return 'syntax error near `' . self::near($t) . '`';
    }
}
