<?php
// Minimal PEAR shim for the standalone reference implementation.
//
// The fossil stack ran against a system PEAR installation. The
// vendored code in this reference uses exactly two PEAR entry
// points: PEAR::isError (Text_Highlighter's offline Generator,
// not on the render path) and PEAR::raiseError (Text_Highlighter
// factory, unknown-language branch only). Nothing extends PEAR.
// This shim reproduces those two behaviors; it is environment
// scaffolding, not parser semantics.

class PEAR_Error {
    public $message;
    public function __construct($message = '') {
        $this->message = $message;
    }
    public function getMessage() {
        return $this->message;
    }
}

class PEAR {
    public static function isError($data) {
        return $data instanceof PEAR_Error;
    }
    public static function raiseError($message = null) {
        return new PEAR_Error($message === null ? '' : $message);
    }
}
