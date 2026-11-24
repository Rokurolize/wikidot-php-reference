<?php
/** REFCORR19 F10: the Expr rule resolves at parse time; render is a stub. */
class Text_Wiki_Render_Xhtml_Expr extends Text_Wiki_Render {
    function token($options) { return isset($options['text']) ? $options['text'] : ''; }
}
