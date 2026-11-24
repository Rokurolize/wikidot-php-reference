<?php
/**
 * REFCORR19 F10: [[#ifexpr]] evaluation. Shares Expr's evaluator and
 * splices the selected branch back into the source at parse time.
 */
require_once dirname(__FILE__) . '/Expr.php';

class Text_Wiki_Parse_Ifexpr extends Text_Wiki_Parse {

    public $regex = '/\[\[#ifexpr\s+([^\]]*?)\]\]/i';

    function process($matches)
    {
        $body = $matches[1];
        // Split on top-level pipes: condition | true | false.
        $fields = array();
        $depth = 0;
        $cur = '';
        $len = strlen($body);
        for ($i = 0; $i < $len; $i++) {
            $c = $body[$i];
            if ($c === '(' || $c === '[' || $c === '{') {
                $depth++;
            } elseif ($c === ')' || $c === ']' || $c === '}') {
                $depth--;
            }
            if ($c === '|' && $depth === 0) {
                $fields[] = $cur;
                $cur = '';
            } else {
                $cur .= $c;
            }
        }
        $fields[] = $cur;
        $condition = isset($fields[0]) ? trim($fields[0]) : '';
        list($value, $truth) = Text_Wiki_Parse_Expr::condition($condition);
        if (!is_numeric($value) && strpos($value, 'syntax error') === 0) {
            return $value;
        }
        if ($truth) {
            return isset($fields[1]) ? trim($fields[1]) : '';
        }
        return isset($fields[2]) ? trim($fields[2]) : '';
    }
}
