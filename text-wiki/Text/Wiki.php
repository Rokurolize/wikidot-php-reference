<?php
// vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
/**
 * Parse structured wiki text and render into arbitrary formats such as XHTML.
 *
 * PHP versions 4 and 5
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @author Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    $Id$
 * @link       http://pear.php.net/package/Text_Wiki
 */

/**
 * The baseline abstract parser class.
 */
require_once __DIR__.'/Wiki/Parse.php';
/**
 * The baseline abstract render class.
 */
require_once __DIR__.'/Wiki/Render.php';

/**
 * Parse structured wiki text and render into arbitrary formats such as XHTML.
 *
 * This is the "master" class for handling the management and convenience
 * functions to transform Wiki-formatted text.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @author Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki {

    /**
    *
    * The default list of rules, in order, to apply to the source text.
    *
    * @access public
    *
    * @var array
    *
    */

    public $rules = array(
    		'Include',
        'Prefilter',
        'Delimiter',
       // 'Moduledelimiter',
        'Code',
        'Form',
        'Raw',
        'Rawold',
        'Html',
        'Modulepre',
        'Module',
        'Module654',
       
    	'Iftags',
    
        'Comment',
        // REFCORR19 F10: evaluate [[#expr]] / [[#ifexpr]] before the inline
        // rules so branch text is still parsed as wikitext.
        'Expr',
        'Ifexpr',
        'Iframe',
    	'Date',
        'Math',
        
        'Concatlines',
        
        'Freelink',
        'Equationreference',
        'Footnote',
        'Footnoteitem',
        'Footnoteblock',
        'Bibitem',
        'Bibliography',
        'Bibcite',
 //       'Function',
        'Divprefilter',
 //       'Embed',
        'Anchor',
        'User',
        'Blockquote',
        'Heading',
        'Toc',
        'Horiz',
        'Separator',
        'Clearfloat',
        'Break',
        'Span',
        'Size',
        'Div',
        'Divalign',
        'Collapsible',
        'Tabview',
        'Note',
        'Gallery',
        'List',
        'Deflist',
        'Table',
        'Tableadv',
        'Button',
        'Image',
        'Embed',
        'Social',
        'File',
 //       'Phplookup',
        'Center',
        'Newline',
        'Paragraph' ,
        'Url',
        'Email',
        'Mathinline',
        'Interwiki',
      //  'Wikilink',
        'Colortext',
        'Strong',
       // 'Bold',
        'Emphasis',
        //'Italic',
        'Underline',
        'Strikethrough',
        'Tt',
        'Superscript',
        'Subscript',
        'Typography',
        'Tighten'
    );

    /**
    *
    * The list of rules to not-apply to the source text.
    *
    * @access public
    *
    * @var array
    *
    */

    // REFCORR19 F2: the Html rule is active again so [[html]] blocks can be
    // modeled as live's html-block-iframe instead of literal source text.
    public $disable = array(
    );

    /**
    *
    * Custom configuration for rules at the parsing stage.
    *
    * In this array, the key is the parsing rule name, and the value is
    * an array of key-value configuration pairs corresponding to the $conf
    * property in the target parsing rule.
    *
    * For example:
    *
    * <code>
    * $parseConf = array(
    *     'Include' => array(
    *         'base' => '/path/to/scripts/'
    *     )
    * );
    * </code>
    *
    * Note that most default rules do not need any parsing configuration.
    *
    * @access public
    *
    * @var array
    *
    */

    public $parseConf = array();

    /**
    *
    * Custom configuration for rules at the rendering stage.
    *
    * Because rendering may be different for each target format, the
    * first-level element in this array is always a format name (e.g.,
    * 'Xhtml').
    *
    * Within that first level element, the subsequent elements match the
    * $parseConf format. That is, the sub-key is the rendering rule name,
    * and the sub-value is an array of key-value configuration pairs
    * corresponding to the $conf property in the target rendering rule.
    *
    * @access public
    *
    * @var array
    *
    */

    public $renderConf = array(
        'Docbook' => array(),
        'Latex' => array(),
        'Pdf' => array(),
        'Plain' => array(),
        'Rtf' => array(),
        'Xhtml' => array(),
        'Xhtmleditable' => array()
    );

    /**
    *
    * Custom configuration for the output format itself.
    *
    * Even though Text_Wiki will render the tokens from parsed text,
    * the format itself may require some configuration.  For example,
    * RTF needs to know font names and sizes, PDF requires page layout
    * information, and DocBook needs a section hierarchy.  This array
    * matches the $conf property of the the format-level renderer
    * (e.g., Text_Wiki_Render_Xhtml).
    *
    * In this array, the key is the rendering format name, and the value is
    * an array of key-value configuration pairs corresponding to the $conf
    * property in the rendering format rule.
    *
    * @access public
    *
    * @var array
    *
    */

    public $formatConf = array(
        'Docbook' => array(),
        'Latex' => array(),
        'Pdf' => array(),
        'Plain' => array(),
        'Rtf' => array(),
        'Xhtml' => array(),
        'Xhtmleditable' => array()
    );

    /**
    *
    * The delimiter for token numbers of parsed elements in source text.
    *
    * @access public
    *
    * @var string
    *
    */

    public $delim = "\xFF";

    /**
    *
    * The tokens generated by rules as the source text is parsed.
    *
    * As Text_Wiki applies rule classes to the source text, it will
    * replace portions of the text with a delimited token number.  This
    * is the array of those tokens, representing the replaced text and
    * any options set by the parser for that replaced text.
    *
    * The tokens array is sequential; each element is itself a sequential
    * array where element 0 is the name of the rule that generated the
    * token, and element 1 is an associative array where the key is an
    * option name and the value is an option value.
    *
    * @access private
    *
    * @var array
    *
    */

    public $tokens = array();

    /**
    *
    * The next token id for this document. Token numbering is document-local:
    * a fresh parse starts at one even when several independent documents are
    * rendered in one PHP process. The fossil kept this counter in a function
    * static, which leaked numbering across batch cases and made placeholder
    * digits visible in Email and Date output diverge from live.
    *
    * @access public
    *
    * @var int
    *
    */

    public $nextTokenId = 1;

    /**
    *
    * REFCORR6 C-SUSPECT3-1: the exact authored source span each token
    * claimed, keyed by the same id as $tokens, as passed by the
    * claiming rule's addToken call. Kept parallel to $tokens rather
    * than stored inside a token entry so the compared [rule, options]
    * wire shape stays byte-identical for every stage and CAPSTONE.
    * Only Mathinline reads it, when it expands placeholders back to
    * their original source text. A rule that does not supply a span
    * has no entry here and Mathinline falls back to option values.
    *
    * @access public
    *
    * @var array
    *
    */

    public $tokenSource = array();

    /**
    *
    * The source text to which rules will be applied.
    *
    * This text will be transformed in-place, which means that it will
    * change as the rules are applied.
    *
    * @access private
    *
    * @var string
    *
    */

    public $source = '';

    /**
    *
    * Array of rule parsers.
    *
    * Text_Wiki creates one instance of every rule that is applied to
    * the source text; this array holds those instances.  The array key
    * is the rule name, and the array value is an instance of the rule
    * class.
    *
    * @access private
    *
    * @var array
    *
    */

    public $parseObj = array();

    /**
    *
    * Array of rule renderers.
    *
    * Text_Wiki creates one instance of every rule that is applied to
    * the source text; this array holds those instances.  The array key
    * is the rule name, and the array value is an instance of the rule
    * class.
    *
    * @access private
    *
    * @var array
    *
    */

    public $renderObj = array();

    /**
    *
    * Array of format renderers.
    *
    * @access private
    *
    * @var array
    *
    */

    public $formatObj = array();

    /**
    *
    * Array of paths to search, in order, for parsing and rendering rules.
    *
    * @access private
    *
    * @var array
    *
    */

    public $path = array(
        'parse' => array(),
        'render' => array()
    );

	/**
	 * Storage for temporary variables.
	 */
	public $store = array();

	public $vars = array();
	
	/**
	 * Stores format while processing the source.
	 */
	public $currentFormat;

    /**
    *
    * The directory separator character.
    *
    * @access private
    *
    * @var string
    *
    */

    public $_dirSep = DIRECTORY_SEPARATOR;

    /**
    *
    * Constructor.
    *
    * @access public
    *
    * @param array $rules The set of rules to load for this object.
    *
    */

    function __construct($rules = null)
    {
        if (is_array($rules)) {
            $this->rules = $rules;
        }

        $this->addPath(
            'parse',
            $this->fixPath(dirname(__FILE__)) . 'Wiki/Parse/Default/'
        );

        $this->addPath(
            'render',
            $this->fixPath(dirname(__FILE__)) . 'Wiki/Render/'
        );

    }

    /**
    *
    * Set parser configuration for a specific rule and key.
    *
    * @access public
    *
    * @param string $rule The parse rule to set config for.
    *
    * @param array|string $arg1 The full config array to use for the
    * parse rule, or a conf key in that array.
    *
    * @param string $arg2 The config value for the key.
    *
    * @return void
    *
    */

    function setParseConf($rule, $arg1, $arg2 = null)
    {
        $rule = ucwords(strtolower($rule));

        if (! isset($this->parseConf[$rule])) {
            $this->parseConf[$rule] = array();
        }

        // if first arg is an array, use it as the entire
        // conf array for the rule.  otherwise, treat arg1
        // as a key and arg2 as a value for the rule conf.
        if (is_array($arg1)) {
            $this->parseConf[$rule] = $arg1;
        } else {
            $this->parseConf[$rule][$arg1] = $arg2;
        }
    }

    /**
    *
    * Get parser configuration for a specific rule and key.
    *
    * @access public
    *
    * @param string $rule The parse rule to get config for.
    *
    * @param string $key A key in the conf array; if null,
    * returns the entire conf array.
    *
    * @return mixed The whole conf array if no key is specified,
    * or the specific conf key value.
    *
    */

    function getParseConf($rule, $key = null)
    {
        $rule = ucwords(strtolower($rule));

        // the rule does not exist
        if (! isset($this->parseConf[$rule])) {
            return null;
        }

        // no key requested, return the whole array
        if (is_null($key)) {
            return $this->parseConf[$rule];
        }

        // does the requested key exist?
        if (isset($this->parseConf[$rule][$key])) {
            // yes, return that value
            return $this->parseConf[$rule][$key];
        } else {
            // no
            return null;
        }
    }

    /**
    *
    * Set renderer configuration for a specific format, rule, and key.
    *
    * @access public
    *
    * @param string $format The render format to set config for.
    *
    * @param string $rule The render rule to set config for in the format.
    *
    * @param array|string $arg1 The config array, or the config key
    * within the render rule.
    *
    * @param string $arg2 The config value for the key.
    *
    * @return void
    *
    */

    function setRenderConf($format, $rule, $arg1, $arg2 = null)
    {
        $format = ucwords(strtolower($format));
        $rule = ucwords(strtolower($rule));

        if (! isset($this->renderConf[$format])) {
            $this->renderConf[$format] = array();
        }

        if (! isset($this->renderConf[$format][$rule])) {
            $this->renderConf[$format][$rule] = array();
        }

        // if first arg is an array, use it as the entire
        // conf array for the render rule.  otherwise, treat arg1
        // as a key and arg2 as a value for the render rule conf.
        if (is_array($arg1)) {
            $this->renderConf[$format][$rule] = $arg1;
        } else {
            $this->renderConf[$format][$rule][$arg1] = $arg2;
        }
    }

    /**
    *
    * Get renderer configuration for a specific format, rule, and key.
    *
    * @access public
    *
    * @param string $format The render format to get config for.
    *
    * @param string $rule The render format rule to get config for.
    *
    * @param string $key A key in the conf array; if null,
    * returns the entire conf array.
    *
    * @return mixed The whole conf array if no key is specified,
    * or the specific conf key value.
    *
    */

    function getRenderConf($format, $rule, $key = null)
    {
        $format = ucwords(strtolower($format));
        $rule = ucwords(strtolower($rule));

        if (! isset($this->renderConf[$format]) ||
            ! isset($this->renderConf[$format][$rule])) {
            return null;
        }

        // no key requested, return the whole array
        if (is_null($key)) {
            return $this->renderConf[$format][$rule];
        }

        // does the requested key exist?
        if (isset($this->renderConf[$format][$rule][$key])) {
            // yes, return that value
            return $this->renderConf[$format][$rule][$key];
        } else {
            // no
            return null;
        }

    }

    /**
    *
    * Set format configuration for a specific rule and key.
    *
    * @access public
    *
    * @param string $format The format to set config for.
    *
    * @param string $key The config key within the format.
    *
    * @param string $val The config value for the key.
    *
    * @return void
    *
    */

    function setFormatConf($format, $arg1, $arg2 = null)
    {
        if (! is_array($this->formatConf[$format])) {
            $this->formatConf[$format] = array();
        }

        // if first arg is an array, use it as the entire
        // conf array for the format.  otherwise, treat arg1
        // as a key and arg2 as a value for the format conf.
        if (is_array($arg1)) {
            $this->formatConf[$format] = $arg1;
        } else {
            $this->formatConf[$format][$arg1] = $arg2;
        }
    }

    /**
    *
    * Get configuration for a specific format and key.
    *
    * @access public
    *
    * @param string $format The format to get config for.
    *
    * @param mixed $key A key in the conf array; if null,
    * returns the entire conf array.
    *
    * @return mixed The whole conf array if no key is specified,
    * or the specific conf key value.
    *
    */

    function getFormatConf($format, $key = null)
    {
        // the format does not exist
        if (! isset($this->formatConf[$format])) {
            return null;
        }

        // no key requested, return the whole array
        if (is_null($key)) {
            return $this->formatConf[$format];
        }

        // does the requested key exist?
        if (isset($this->formatConf[$format][$key])) {
            // yes, return that value
            return $this->formatConf[$format][$key];
        } else {
            // no
            return null;
        }
    }

    /**
    *
    * Inserts a rule into to the rule set.
    *
    * @access public
    *
    * @param string $name The name of the rule.  Should be different from
    * all other keys in the rule set.
    *
    * @param string $tgt The rule after which to insert this new rule.  By
    * default (null) the rule is inserted at the end; if set to '', inserts
    * at the beginning.
    *
    * @return void
    *
    */

    function insertRule($name, $tgt = null)
    {
        $name = ucwords(strtolower($name));
        if (! is_null($tgt)) {
            $tgt = ucwords(strtolower($tgt));
        }

        // does the rule name to be inserted already exist?
        if (in_array($name, $this->rules)) {
            // yes, return
            return null;
        }

        // the target name is not null, and not '', but does not exist
        // in the list of rules. this means we're trying to insert after
        // a target key, but the target key isn't there.
        if (! is_null($tgt) && $tgt != '' &&
            ! in_array($tgt, $this->rules)) {
            return false;
        }

        // if $tgt is null, insert at the end.  We know this is at the
        // end (instead of resetting an existing rule) becuase we exited
        // at the top of this method if the rule was already in place.
        if (is_null($tgt)) {
            $this->rules[] = $name;
            return true;
        }

        // save a copy of the current rules, then reset the rule set
        // so we can insert in the proper place later.
        // where to insert the rule?
        if ($tgt == '') {
            // insert at the beginning
            array_unshift($this->rules, $name);
            return true;
        }

        // insert after the named rule
        $tmp = $this->rules;
        $this->rules = array();

        foreach ($tmp as $val) {
            $this->rules[] = $val;
            if ($val == $tgt) {
                $this->rules[] = $name;
            }
        }

        return true;

    }

    /**
    *
    * Delete (remove or unset) a rule from the $rules property.
    *
    * @access public
    *
    * @param string $rule The name of the rule to remove.
    *
    * @return void
    *
    */

    function deleteRule($name)
    {
        $name = ucwords(strtolower($name));
        $key = array_search($name, $this->rules);
        if ($key !== false) {
            unset($this->rules[$key]);
        }
    }

    /**
    *
    * Change from one rule to another in-place.
    *
    * @access public
    *
    * @param string $old The name of the rule to change from.
    *
    * @param string $new The name of the rule to change to.
    *
    * @return void
    *
    */

    function changeRule($old, $new)
    {
        $old = ucwords(strtolower($old));
        $new = ucwords(strtolower($new));
        $key = array_search($old, $this->rules);
        if ($key !== false) {
            $this->rules[$old] = $new;
        }
    }

    /**
    *
    * Enables a rule so that it is applied when parsing.
    *
    * @access public
    *
    * @param string $rule The name of the rule to enable.
    *
    * @return void
    *
    */

    function enableRule($name)
    {
        $name = ucwords(strtolower($name));
        $key = array_search($name, $this->disable);
        if ($key !== false) {
            unset($this->disable[$key]);
        }
    }

    /**
    *
    * Disables a rule so that it is not applied when parsing.
    *
    * @access public
    *
    * @param string $rule The name of the rule to disable.
    *
    * @return void
    *
    */

    function disableRule($name)
    {
        $name = ucwords(strtolower($name));
        $key = array_search($name, $this->disable);
        if ($key === false) {
            $this->disable[] = $name;
        }
    }

    /**
    *
    * Parses and renders the text passed to it, and returns the results.
    *
    * First, the method parses the source text, applying rules to the
    * text as it goes.  These rules will modify the source text
    * in-place, replacing some text with delimited tokens (and
    * populating the $this->tokens array as it goes).
    *
    * Next, the method renders the in-place tokens into the requested
    * output format.
    *
    * Finally, the method returns the transformed text.  Note that the
    * source text is transformed in place; once it is transformed, it is
    * no longer the same as the original source text.
    *
    * @access public
    *
    * @param string $text The source text to which wiki rules should be
    * applied, both for parsing and for rendering.
    *
    * @param string $format The target output format, typically 'xhtml'.
    *  If a rule does not support a given format, the output from that
    * rule is rule-specific.
    *
    * @return string The transformed wiki text.
    *
    */

    function transform($text, $format = 'Xhtml')
    {
    	$this->currentFormat = $format;
        $this->parse($text);
        $out = $this->render($format);
        $this->currentFormat = null;
        return $out;
    }

    /**
    *
    * Sets the $_source text property, then parses it in place and
    * retains tokens in the $_tokens array property.
    *
    * @access public
    *
    * @param string $text The source text to which wiki rules should be
    * applied, both for parsing and for rendering.
    *
    * @return void
    *
    */

    function parse($text)
    {
        // set the object property for the source text
        $this->source = $text;

        // reset the tokens and their REFCORR6 source spans.
        $this->tokens = array();
        $this->tokenSource = array();
        $this->nextTokenId = 1;

        // apply the parse() method of each requested rule to the source
        // text.
        foreach ($this->rules as $name) {
            // do not parse the rules listed in $disable
            if (! in_array($name, $this->disable)) {

                // load the parsing object
                $this->loadParseObj($name);

                // load may have failed; only parse if
                // an object is in the array now
                if (is_object($this->parseObj[$name])) {
                    $this->parseObj[$name]->parse();
                }
            }
            
        }
    }

    /**
    *
    * Render a document whose post-parse text contains a literal U+FFFD.
    *
    * pre() turns every U+FFFD into the delimiter byte, so a literal
    * character is indistinguishable from a placeholder afterwards. This
    * path escapes the same way pre() does, but remembers which delimiter
    * bytes were original placeholders and which were literal characters.
    * A real placeholder is still rendered. One literal delimiter sitting
    * immediately in front of a placeholder leaks that token's fresh-
    * document index (the in-document id minus the document's first id,
    * plus one: live's counter presents the paragraph-end token as 2
    * where a fresh reference document numbers it 1) and does not render
    * the placeholder; every further placeholder with nothing between it
    * and the previous one is swallowed the same way and its index is
    * leaked too, which is how an entire adjacent run merges. The walk
    * stops at the first gap or non-placeholder byte. Any other literal delimiter is dropped.
    * Two or more literal delimiters in a row are dropped without a leak,
    * and the following placeholder still renders. The resulting HTML is
    * the input live's purifyHtml tidy pass repairs: it closes open
    * blocks, drops an empty paragraph, removes a stray end tag, collapses
    * the space a dropped character left behind, and turns a paragraph end
    * trapped inside a heading into the break sequence live serves.
    *
    * @access private
    *
    * @param string $format The already-normalized format name.
    *
    * @return string The repaired XHTML, trimmed the way a page-content
    * capture is stripped.
    *
    */

    function renderLiteralUfffdRecovery($format)
    {
        foreach (array_keys($this->parseObj) as $rule) {
            $this->loadRenderObj($format, $rule);
        }

        $type = HTML_SPECIALCHARS;
        $quotes = ENT_COMPAT | ENT_SUBSTITUTE;
        if (is_object($this->formatObj[$format])) {
            $type = $this->formatObj[$format]->getConf('translate', HTML_ENTITIES);
            $quotes = $this->formatObj[$format]->getConf('quotes', ENT_COMPAT) | ENT_SUBSTITUTE;
            $charset = $this->formatObj[$format]->getConf('charset', 'UTF-8');
        }
        if ($type === HTML_ENTITIES) {
            $src = @htmlentities($this->source, $quotes, $charset);
        } else {
            $src = @htmlspecialchars($this->source, $quotes);
        }
        $src = str_replace("\xEF\xBF\xBD", $this->delim, $src);

        // Rebuild the escaped stream while remembering whether every
        // converted U+FFFD came from an original placeholder delimiter or
        // from authored text. htmlspecialchars() substitutes the invalid
        // 0xFF bytes of real placeholders as U+FFFD, so position arithmetic
        // after escaping cannot recover the distinction.
        $bytes = '';
        $origin = '';
        $raw = $this->source;
        $appendChunk = function ($chunk) use (&$bytes, &$origin, $type, $quotes, $charset) {
            $off = 0;
            $len = strlen($chunk);
            while (($at = strpos($chunk, "\xEF\xBF\xBD", $off)) !== false) {
                $part = substr($chunk, $off, $at - $off);
                $esc = $type === HTML_ENTITIES
                    ? @htmlentities($part, $quotes, $charset)
                    : @htmlspecialchars($part, $quotes);
                $bytes .= $esc;
                $origin .= str_repeat('T', strlen($esc));
                $bytes .= "\xFF";
                $origin .= 'L';
                $off = $at + 3;
            }
            $part = substr($chunk, $off);
            $esc = $type === HTML_ENTITIES
                ? @htmlentities($part, $quotes, $charset)
                : @htmlspecialchars($part, $quotes);
            $bytes .= $esc;
            $origin .= str_repeat('T', strlen($esc));
        };
        $pos = 0;
        while (preg_match('/\xFF([0-9]+)\xFF/', $raw, $pm, PREG_OFFSET_CAPTURE, $pos)) {
            $at = $pm[0][1];
            if ($at > $pos) {
                $appendChunk(substr($raw, $pos, $at - $pos));
            }
            $id = $pm[1][0];
            $bytes .= "\xFF" . $id . "\xFF";
            $origin .= 'O' . str_repeat('D', strlen($id)) . 'O';
            $pos = $at + strlen($pm[0][0]);
        }
        if ($pos < strlen($raw)) {
            $appendChunk(substr($raw, $pos));
        }

        $tokenIds = array_keys($this->tokens);
        $firstTokenId = $tokenIds ? min($tokenIds) : 1;
        $freshIndex = function ($id) use ($firstTokenId) {
            return $id - $firstTokenId + 1;
        };

        $html = '';
        $n = strlen($bytes);
        $i = 0;
        while ($i < $n) {
            if ($bytes[$i] !== "\xFF") {
                $j = $i;
                while ($j < $n && $bytes[$j] !== "\xFF") {
                    $j++;
                }
                $html .= substr($bytes, $i, $j - $i);
                $i = $j;
                continue;
            }

            if ($origin[$i] === 'O') {
                $match = $this->matchOriginalToken($bytes, $origin, $i, $this->tokens);
                if ($match !== null) {
                    $html .= $this->renderTokenId($match['id']);
                    $i = $match['next'];
                } else {
                    $i++;
                }
                continue;
            }

            // A literal followed by digits leading into a real placeholder
            // starts the fossil pair scan: the authored digits become the
            // first corrupted key, and malformed later keys remain visible
            // instead of identifying tokens. This is the sentinel-cascade
            // shape; an immediately adjacent placeholder follows the narrower
            // swallowed-index path below.
            if ($i + 1 < $n && ctype_digit($bytes[$i + 1])) {
                $digitEnd = $i + 1;
                while ($digitEnd < $n && ctype_digit($bytes[$digitEnd])) {
                    $digitEnd++;
                }
                if ($digitEnd < $n && $bytes[$digitEnd] === "\xFF" && $origin[$digitEnd] === 'O') {
                    while ($i < $n) {
                        if ($bytes[$i] !== "\xFF") {
                            $j = $i;
                            while ($j < $n && $bytes[$j] !== "\xFF") {
                                $j++;
                            }
                            $html .= substr($bytes, $i, $j - $i);
                            $i = $j;
                            continue;
                        }
                        $close = strpos($bytes, "\xFF", $i + 1);
                        if ($close === false) {
                            $html .= substr($bytes, $i + 1);
                            $i = $n;
                            break;
                        }
                        $key = substr($bytes, $i + 1, $close - $i - 1);
                        if ($key !== '' && ctype_digit($key) && isset($this->tokens[(int)$key])) {
                            $html .= $this->renderTokenId((int)$key);
                        } else {
                            $html .= $key;
                        }
                        $i = $close + 1;
                    }
                    continue;
                }
            }

            // A literal delimiter is dropped. When it sits immediately before
            // a real placeholder, live's corrupted scan consumes that
            // placeholder and exposes its document-local index; adjacent real
            // placeholders are consumed into the same run. Two adjacent
            // literal delimiters break the run before it starts.
            if ($i + 1 < $n && $bytes[$i + 1] === "\xFF" && $origin[$i + 1] === 'L') {
                while ($i < $n && $bytes[$i] === "\xFF" && $origin[$i] === 'L') {
                    $i++;
                }
                continue;
            }
            $i++;
            if ($i < $n && $bytes[$i] === "\xFF" && $origin[$i] === 'O') {
                while ($i < $n && $bytes[$i] === "\xFF" && $origin[$i] === 'O') {
                    $match = $this->matchOriginalToken($bytes, $origin, $i, $this->tokens);
                    if ($match === null) {
                        break;
                    }
                    $html .= (string)$freshIndex($match['id']);
                    $i = $match['next'];
                }
            }
        }
        $src = $bytes;

        $this->source = $src;
        return $this->purifyRecoveredHtml($html);
    }

    /**
    *
    * A real placeholder is an original delimiter, digits, and an original
    * delimiter, naming a token this document actually created.
    *
    * @access private
    *
    * @return array|null id and the index just past the closing delimiter.
    *
    */

    function matchOriginalToken($bytes, $origin, $i, $tokens)
    {
        $n = strlen($bytes);
        if ($i >= $n || $bytes[$i] !== $this->delim || $origin[$i] !== 'O') {
            return null;
        }
        $j = $i + 1;
        if ($j >= $n || !ctype_digit($bytes[$j])) {
            return null;
        }
        $k = $j;
        while ($k < $n && ctype_digit($bytes[$k])) {
            $k++;
        }
        if ($k >= $n || $bytes[$k] !== $this->delim || $origin[$k] !== 'O') {
            return null;
        }
        $id = (int)substr($bytes, $j, $k - $j);
        if (!isset($tokens[$id])) {
            return null;
        }
        return array('id' => $id, 'next' => $k + 1);
    }

    /**
    *
    * Render one token id, or nothing when that rule has no renderer.
    *
    * @access private
    *
    * @param int $id The token id.
    *
    * @return string
    *
    */

    function renderTokenId($id)
    {
        $rule = $this->tokens[$id][0];
        $opts = $this->tokens[$id][1];
        if (!isset($this->renderObj[$rule]) || !is_object($this->renderObj[$rule])) {
            return '';
        }
        return $this->renderObj[$rule]->token($opts);
    }

    /**
    *
    * Live's purifyHtml: wrap the fragment, run tidy as XHTML with no
    * indent and no wrap, and return the body. The capture extractor
    * strips the page-content text, so the body is trimmed.
    *
    * @access private
    *
    * @param string $code The unrepaired fragment.
    *
    * @return string
    *
    */

    function purifyRecoveredHtml($code)
    {
        if (!class_exists('FFI')) {
            return $code;
        }
        static $ffi = null;
        static $ffiFailed = false;
        if ($ffiFailed) {
            return $code;
        }
        if ($ffi === null) {
            $def = '
typedef unsigned int uint;
typedef unsigned char byte;
typedef struct _TidyBuffer { void* allocator; byte* bp; uint size; uint allocated; uint next; } TidyBuffer;
typedef void* TidyDoc;
TidyDoc tidyCreate(void);
void tidyRelease(TidyDoc tdoc);
int tidySetCharEncoding(TidyDoc tdoc, const char* encnam);
int tidyOptSetInt(TidyDoc tdoc, int optid, unsigned long val);
int tidyOptSetBool(TidyDoc tdoc, int optid, int val);
int tidyOptGetIdForName(const char* optnam);
void tidyBufInit(TidyBuffer* buf);
void tidyBufFree(TidyBuffer* buf);
void tidyBufAppend(TidyBuffer* buf, void* vp, uint size);
int tidyParseBuffer(TidyDoc tdoc, TidyBuffer* buf);
int tidySaveBuffer(TidyDoc tdoc, TidyBuffer* buf);
';
            $lib = is_file('/usr/lib/x86_64-linux-gnu/libtidy.so.58')
                ? '/usr/lib/x86_64-linux-gnu/libtidy.so.58'
                : 'libtidy.so.58';
            try {
                $ffi = FFI::cdef($def, $lib);
            } catch (Throwable $e) {
                $ffiFailed = true;
                return $code;
            }
        }

        $head = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">  <head>    <title>Just A Wrapper</title><meta http-equiv="content-type" content="text/html;charset=UTF-8"/>  </head> <!--wrapdelimiter--><body>';
        $tail = ' </body><!--wrapdelimiter--></html>';
        $wrapped = $head . $code . $tail;
        $len = strlen($wrapped);

        try {
            $doc = $ffi->tidyCreate();
            $ffi->tidySetCharEncoding($doc, 'UTF8');
            $ffi->tidyOptSetInt($doc, $ffi->tidyOptGetIdForName('indent'), 0);
            $ffi->tidyOptSetBool($doc, $ffi->tidyOptGetIdForName('output-xhtml'), 1);
            $ffi->tidyOptSetInt($doc, $ffi->tidyOptGetIdForName('wrap'), 0);
            $ffi->tidyOptSetBool($doc, $ffi->tidyOptGetIdForName('preserve-entities'), 1);
            $ffi->tidyOptSetBool($doc, $ffi->tidyOptGetIdForName('show-warnings'), 0);
            $ffi->tidyOptSetInt($doc, $ffi->tidyOptGetIdForName('show-errors'), 0);

            $inbuf = $ffi->new('TidyBuffer');
            $ffi->tidyBufInit(FFI::addr($inbuf));
            $input = $ffi->new('char[' . $len . ']');
            FFI::memcpy($input, $wrapped, $len);
            $ffi->tidyBufAppend(FFI::addr($inbuf), $input, $len);
            $ffi->tidyParseBuffer($doc, FFI::addr($inbuf));

            $save1 = $ffi->new('TidyBuffer');
            $save2 = $ffi->new('TidyBuffer');
            $ffi->tidyBufInit(FFI::addr($save1));
            $ffi->tidyBufInit(FFI::addr($save2));
            // The two saves mirror ext/tidy's update-properties pass and the
            // later cast to string. In particular there is deliberately no
            // tidyCleanAndRepair call; the CLI performs one and is not the
            // live oracle.
            $ffi->tidySaveBuffer($doc, FFI::addr($save1));
            $ffi->tidySaveBuffer($doc, FFI::addr($save2));
            $cleaned = FFI::string($save2->bp, $save2->size);
            $ffi->tidyBufFree(FFI::addr($inbuf));
            $ffi->tidyBufFree(FFI::addr($save1));
            $ffi->tidyBufFree(FFI::addr($save2));
            $ffi->tidyRelease($doc);
        } catch (Throwable $e) {
            return $code;
        }

        if (!is_string($cleaned) || strpos($cleaned, '<!--wrapdelimiter-->') === false) {
            return $code;
        }
        $parts = explode('<!--wrapdelimiter-->', $cleaned);
        $out = $parts[1];
        $out = str_replace(array('<body>', '</body>'), '', $out);
        return trim($out);
    }

    /**
     * Whether a rendered TOC title still carries whitespace that live's
     * purifyHtml pass would collapse. Toc titles are produced at render time
     * from an attribute, so Tighten's residual-text whitespace fold never
     * reaches them.
     */
    function outputHasUnpurifiedTocTitleWhitespace($html)
    {
        if (! preg_match_all('/<div id="toc"(?:\s[^>]*)?>\s*<div id="toc-action-bar">.*?<\/div>\s*<div class="title">(.*?)<\/div>/s', $html, $matches)) {
            return false;
        }
        foreach ($matches[1] as $title) {
            if (trim(preg_replace('/\s+/', ' ', $title)) !== $title) {
                return true;
            }
        }
        return false;
    }

    /**
     * Whether any span element is still open at a paragraph end. Span-like
     * inline constructs can pair across a blank line in Stage 1; live's
     * purifyHtml repair closes and reopens the span in the separate
     * paragraphs instead of emitting crossing tags.
     */
    function outputHasSpanParagraphCrossing($html)
    {
        if (! preg_match_all('/<(\/?)(span|p)\b([^>]*)>/i', $html, $matches, PREG_SET_ORDER)) {
            return false;
        }
        $stack = array();
        foreach ($matches as $m) {
            $closing = $m[1] === '/';
            $tag = strtolower($m[2]);
            if (! $closing) {
                $stack[] = $tag;
                continue;
            }
            if ($tag === 'p') {
                if (in_array('span', $stack, true)) {
                    return true;
                }
                while ($stack) {
                    if (array_pop($stack) === 'p') {
                        break;
                    }
                }
                continue;
            }
            // closing span: pop it when well-formed, otherwise leave the
            // stack intact so a following block boundary still reports the
            // crossing that made it malformed.
            if ($stack && end($stack) === 'span') {
                array_pop($stack);
            }
        }
        return false;
    }

    /**
     * Whether a collapsible is caught in a centered paragraph or list-item
     * boundary that live's purifyHtml pass repairs.
     */
    function outputHasCollapsibleStructuralCrossing($html)
    {
        if (preg_match('/<p\b[^>]*style="text-align:\s*center;?"[^>]*>(?:(?!<\/p>).)*<div class="collapsible-block">/s', $html)) {
            return true;
        }
        return strpos($html, '<div class="collapsible-block-content"></li>') !== false;
    }

    /**
     * Whether a paired-token inline element crosses a block-element boundary or
     * another inline element emitted by the pair rules. Well-formed documents are
     * left in the reference frame.
     */
    function outputHasInlineCrossing($html)
    {
        $scan = preg_replace('/<(script|style)\b[^>]*>.*?<\/\1\s*>/is', '', $html);
        if (! preg_match_all('/<(\/?)([a-z][a-z0-9]*)\b([^>]*)>/i', $scan, $matches, PREG_SET_ORDER)) {
            return false;
        }
        $inline = array_flip(array(
            'a', 'em', 'span', 'strong', 'sub', 'sup', 'tt'
        ));
        $block = array_flip(array(
            'address', 'article', 'aside', 'blockquote', 'dd', 'details', 'div',
            'dl', 'dt', 'fieldset', 'figcaption', 'figure', 'footer', 'form',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'li', 'main', 'nav',
            'ol', 'p', 'pre', 'section', 'table', 'tbody', 'td', 'tfoot', 'th',
            'thead', 'tr', 'ul'
        ));
        $void = array_flip(array(
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
            'meta', 'param', 'source', 'track', 'wbr'
        ));
        $stack = array();
        foreach ($matches as $m) {
            $closing = $m[1] === '/';
            $tag = strtolower($m[2]);
            if (isset($void[$tag]) || preg_match('/\/\s*$/', $m[3])) {
                continue;
            }
            if (! $closing) {
                if (isset($block[$tag])) {
                    foreach ($stack as $open) {
                        if (isset($inline[$open])) {
                            return true;
                        }
                    }
                }
                $stack[] = $tag;
                continue;
            }
            $pos = -1;
            for ($i = count($stack) - 1; $i >= 0; $i--) {
                if ($stack[$i] === $tag) {
                    $pos = $i;
                    break;
                }
            }
            if ($pos < 0) {
                continue;
            }
            if (isset($block[$tag])) {
                for ($i = count($stack) - 1; $i > $pos; $i--) {
                    if (isset($inline[$stack[$i]])) {
                        return true;
                    }
                }
            }
            if (isset($inline[$tag])) {
                for ($i = count($stack) - 1; $i > $pos; $i--) {
                    if (isset($inline[$stack[$i]])) {
                        return true;
                    }
                }
            }
            array_splice($stack, $pos);
        }
        return false;
    }

    function outputHasListParagraphCrossing($html)
    {
        if (!preg_match_all('/<(\/?)(ul|ol|li|p)\b([^>]*)>/i', $html, $matches, PREG_SET_ORDER)) {
            return false;
        }
        $stack = array();
        foreach ($matches as $m) {
            $closing = $m[1] === '/';
            $tag = strtolower($m[2]);
            if (!$closing) {
                $stack[] = $tag;
                continue;
            }
            if (($tag === 'li' || $tag === 'ul' || $tag === 'ol') && in_array('p', $stack, true)) {
                return true;
            }
            $pos = -1;
            for ($i = count($stack) - 1; $i >= 0; $i--) {
                if ($stack[$i] === $tag) {
                    $pos = $i;
                    break;
                }
            }
            if ($pos >= 0) {
                array_splice($stack, $pos);
            }
        }
        return false;
    }

    /**
     * Whether a blockquote participates in a container crossing rather than
     * nesting cleanly. Inline-scope crossings have their own narrower test
     * above; this scan is for the blockquote/div/alignment class of malformed
     * token assembly, where the first mismatched close is exactly the input
     * live's purifyHtml repair receives.
     */
    function outputHasQuoteStructuralCrossing($html)
    {
        $scan = preg_replace('/<(script|style)\b[^>]*>.*?<\/\1\s*>/is', '', $html);
        if (! preg_match_all('/<(\/?)([a-z][a-z0-9]*)\b([^>]*)>/i', $scan, $matches, PREG_SET_ORDER)) {
            return false;
        }
        $void = array_flip(array(
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
            'meta', 'param', 'source', 'track', 'wbr'
        ));
        $stack = array();
        foreach ($matches as $m) {
            $closing = $m[1] === '/';
            $tag = strtolower($m[2]);
            if (isset($void[$tag]) || preg_match('/\/\s*$/', $m[3])) {
                continue;
            }
            if (! $closing) {
                $stack[] = $tag;
                continue;
            }
            $pos = -1;
            for ($i = count($stack) - 1; $i >= 0; $i--) {
                if ($stack[$i] === $tag) {
                    $pos = $i;
                    break;
                }
            }
            if ($pos < 0) {
                continue;
            }
            if ($pos !== count($stack) - 1) {
                $crossed = array_slice($stack, $pos + 1);
                if ($tag === 'blockquote' || in_array('blockquote', $crossed, true)) {
                    return true;
                }
            }
            array_splice($stack, $pos);
        }
        return false;
    }

    /**
     * Whether a blockquote shell has no rendered content. Quote parsing emits
     * the shell before later block rules can vanish their empty contents;
     * live's purifyHtml pass removes the resulting empty shell.
     */
    function outputHasEmptyBlockquote($html)
    {
        return preg_match('/<blockquote(?:\s[^>]*)?>\s*<\/blockquote>/i', $html) === 1;
    }

    /**
     * Whether the output assembled so far ends in bare non-whitespace text
     * rather than at an element boundary. Used only when a Div-rule start is
     * about to render and the trailing source characters are literal inline
     * text: generated module/error text is harness output, not the authored
     * inline boundary whose byte live's purifyHtml pass owns. Synthetic
     * offline-include error blocks are excluded as Div targets for the same
     * reason.
     */
    function outputEndsWithBareInlineText($html)
    {
        $tagEnd = strrpos($html, '>');
        $text = substr($html, $tagEnd === false ? 0 : $tagEnd + 1);
        return trim($text) !== '';
    }

    function outputHasParagraphBlockCrossing($html)
    {
        $scan = preg_replace('/<(script|style)\b[^>]*>.*?<\/\1\s*>/is', '', $html);
        if (! preg_match_all('/<(\/?)([a-z][a-z0-9]*)\b([^>]*)>/i', $scan, $matches, PREG_SET_ORDER)) {
            return false;
        }
        $void = array_flip(array(
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
            'meta', 'param', 'source', 'track', 'wbr'
        ));
        $stack = array();
        foreach ($matches as $m) {
            $closing = $m[1] === '/';
            $tag = strtolower($m[2]);
            if (isset($void[$tag]) || preg_match('/\/\s*$/', $m[3])) {
                continue;
            }
            if (! $closing) {
                if ($tag === 'div' && in_array('p', $stack, true)
                    && strpos($m[3], 'text-align: center') !== false) {
                    return true;
                }
                $stack[] = $tag;
                continue;
            }
            $pos = -1;
            for ($i = count($stack) - 1; $i >= 0; $i--) {
                if ($stack[$i] === $tag) {
                    $pos = $i;
                    break;
                }
            }
            if ($pos >= 0) {
                array_splice($stack, $pos);
            }
        }
        return false;
    }

    /**
    *
    * Renders tokens back into the source text, based on the requested format.
    *
    * @access public
    *
    * @param string $format The target output format, typically 'xhtml'.
    * If a rule does not support a given format, the output from that
    * rule is rule-specific.
    *
    * @return string The transformed wiki text.
    *
    */

    function render($format = 'Xhtml')
    {
        // the rendering method we're going to use from each rule
        $format = ucwords(strtolower($format));

        // the eventual output text
        $output = '';

        // when passing through the parsed source text, keep track of when
        // we are in a delimited section
        $in_delim = false;

        // when in a delimited section, capture the token key number
        $key = '';

        // load the format object, or crap out if we can't find it
        $result = $this->loadFormatObj($format);
        if ($this->isError($result)) {
        	return $result;
        }

        // A literal U+FFFD in post-parse text collides with the delimiter
        // bytes once pre() runs (R-UFFFD-1). Live recovers that stream and
        // then tidy-repairs it (WikiTransformation::purifyHtml). Documents
        // with no literal U+FFFD take the original loop unchanged.
        $sawCollapsible = false;
        $sawTableadvFoster = false;
        $sawBareInlineBeforeDiv = false;
        $sawFootnoteBlock = false;
        $inFootnoteItem = false;
        $trailingLiteral = '';
        if (strpos($this->source, "\xEF\xBF\xBD") !== false) {
            $output .= $this->renderLiteralUfffdRecovery($format);
        } else {
        // pre-rendering activity
        if (is_object($this->formatObj[$format])) {
            $output .= $this->formatObj[$format]->pre();
        }

        // load the render objects
        foreach (array_keys($this->parseObj) as $rule) {
            $this->loadRenderObj($format, $rule);
        }

        // pass through the parsed source text character by character
        $k = strlen($this->source);
        for ($i = 0; $i < $k; $i++) {

            // the current character
            $char = $this->source[$i];

            // are alredy in a delimited section?
            if ($in_delim) {

                // yes; are we ending the section?
                if ($char == $this->delim) {

                    // yes, get the replacement text for the delimited
                    // token number and unset the flag.
                    $key = (int)$key;
                    $rule = $this->tokens[$key][0];
                    $opts = $this->tokens[$key][1];
                    if ($rule === 'Collapsible'
                        && isset($opts['type']) && $opts['type'] === 'start'
                        && isset($opts['leading_size_newline'])) {
                        $size = $opts['leading_size_newline'];
                        $sizeOpen = '<span style="font-size:' . $size . ';">';
                        if (substr($output, -strlen($sizeOpen)) === $sizeOpen) {
                            $output = substr($output, 0, -strlen($sizeOpen))
                                . $sizeOpen . '<br />' . "\n"
                                . '<br /></span>' . "\n"
                                . $sizeOpen;
                        }
                    }
                    if ($rule === 'Horiz' && isset($opts['loose_scope_breaks'])) {
                        $output .= '<br />' . "\n" . '<br />' . "\n";
                    }
                    if ($rule === 'Collapsible') {
                        $sawCollapsible = true;
                    }
                    if ($rule === 'Tableadv' && isset($opts['type'])
                        && $opts['type'] === 'start' && !empty($opts['foster_content'])) {
                        $sawTableadvFoster = true;
                    }
                    if ($rule === 'Div' && isset($opts['type']) && $opts['type'] === 'start'
                        && empty($opts['vanished'])
                        && (!isset($opts['args']['class']) || $opts['args']['class'] !== 'error-block')
                        && trim($trailingLiteral) !== ''
                        && $this->outputEndsWithBareInlineText($output)) {
                        $sawBareInlineBeforeDiv = true;
                    }
                    if ($inFootnoteItem && in_array($rule, array(
                        'List', 'Deflist', 'Blockquote', 'Heading', 'Center',
                        'Code', 'Bibliography', 'Math'
                    ), true)) {
                        $sawFootnoteBlock = true;
                    }
                    if ($rule === 'Footnoteitem' && isset($opts['type'])) {
                        if ($opts['type'] === 'start') {
                            $inFootnoteItem = true;
                        } elseif ($opts['type'] === 'end') {
                            $inFootnoteItem = false;
                        }
                    }
                    $renderedToken = $this->renderObj[$rule]->token($opts);
                    $startsMeasuredBlockBoundary = ($rule === 'Paragraph' && isset($opts['type']) && $opts['type'] === 'start')
                        || $rule === 'Horiz'
                        || (in_array($rule, array('Div', 'Divalign', 'Center', 'Blockquote'), true)
                            && isset($opts['type']) && ($opts['type'] === 'start' || substr($opts['type'], -6) === '_start'));
                    if ($startsMeasuredBlockBoundary && $output !== '' && ! ctype_space(substr($output, -1))
                        && trim($trailingLiteral) !== ''
                        && $this->outputEndsWithBareInlineText($output)) {
                        $output .= "\n";
                    }
                    $output .= $renderedToken;
                    $trailingLiteral = '';
                    $in_delim = false;

                } else {

                    // no, add to the dlimited token key number
                    $key .= $char;

                }

            } else {

                // not currently in a delimited section.
                // are we starting into a delimited section?
                if ($char == $this->delim) {
                    // yes, reset the previous key and
                    // set the flag.
                    $key = '';
                    $in_delim = true;
                } else {
                    // no, add to the output as-is
                    $output .= $char;
                    $trailingLiteral .= $char;
                }
            }
        }
        }

        // post-rendering activity
        if (is_object($this->formatObj[$format])) {
            $output .= $this->formatObj[$format]->post();
        }

        // REFCORR22 R3: live's purifyHtml/tidy pass cannot keep a block-level
        // error div inside a paragraph. When the paragraph consists solely of
        // the Embed no-match block, tidy drops the paragraph wrapper. The
        // generic div-splitting problem is much wider and remains a frame
        // concern; this exact pure-paragraph repair is the measured Embed
        // boundary and does not alter mixed inline runs.
        $embedNoMatch = '<div class="error-block">Sorry, no match for the embedded content.</div>';
        $output = str_replace('<p>' . $embedNoMatch . '</p>', $embedNoMatch, $output);
        $output = preg_replace('/<dl>\s*<\/dl>\s*/', '', $output);
        $output = preg_replace_callback('/(<div class="yui-content">)(.*?)(<\/div><\/div><script)/s',
            function ($m) {
                return $m[1] . preg_replace('/<p>\s*<\/p>\s*/', '', $m[2]) . $m[3];
            }, $output);
        $output = preg_replace('/<\/div>(?=[^<\s])/', "</div>\n", $output);

		// this is a nasty hack... should be put somewhere else, e.g. Postfilter?
		
		// fix TOC tags within entries
		// C-SUSPECT-XRULE-4: NUL pair matches Render/Xhtml/Toc.php's sentinel.
		$d = "\x00";
		$output = preg_replace_callback("/$d$d(.*?)$d$d/s", array($this, 'strip'), $output);

        // REFCORR30: live passes every rendered fragment through
        // WikiTransformation::purifyHtml. The reference models the common
        // whitespace consequences in Tighten, but some render-time surfaces
        // still need the real repair pass: whitespace inside a TOC title
        // (generated from an attribute after Tighten has run), any span
        // scope left open across a paragraph boundary, a collapsible
        // caught in a centered or list-item boundary, a blockquote caught in
        // a div/alignment crossing, an empty quote shell left after vanished
        // content, or bare inline text directly joining a Div-rule block.
        // Apply the existing tidy-backed purifier only when one of those
        // unrepaired shapes is present, so other well-formed documents keep
        // their established frame.
        if (($sawCollapsible && $this->outputHasCollapsibleStructuralCrossing($output))
            || $sawTableadvFoster
            || $this->outputHasUnpurifiedTocTitleWhitespace($output)
            || $this->outputHasSpanParagraphCrossing($output)
            || $this->outputHasInlineCrossing($output)
            || $this->outputHasParagraphBlockCrossing($output)
            || $this->outputHasQuoteStructuralCrossing($output)
            || $this->outputHasListParagraphCrossing($output)
            || $sawBareInlineBeforeDiv
            || $sawFootnoteBlock
            || $this->outputHasEmptyBlockquote($output)) {
            $output = $this->purifyRecoveredHtml($output);
        }

        // return the rendered source text.
        return $output;
    }
    
    public function strip($matches){
    	return strip_tags($matches[1]);	
    }

    /**
    *
    * Returns the parsed source text with delimited token placeholders.
    *
    * @access public
    *
    * @return string The parsed source text.
    *
    */

    function getSource()
    {
        return $this->source;
    }

    /**
    *
    * Returns tokens that have been parsed out of the source text.
    *
    * @access public
    *
    * @param array $rules If an array of rule names is passed, only return
    * tokens matching these rule names.  If no array is passed, return all
    * tokens.
    *
    * @return array An array of tokens.
    *
    */

    function getTokens($rules = null)
    {
        if (is_null($rules)) {
            return $this->tokens;
        } else {
            settype($rules, 'array');
            $result = array();
            foreach ($this->tokens as $key => $val) {
                if (in_array($val[0], $rules)) {
                    $result[$key] = $val;
                }
            }
            return $result;
        }
    }

    /**
    *
    * Add a token to the Text_Wiki tokens array, and return a delimited
    * token number.
    *
    * @access public
    *
    * @param array $options An associative array of options for the new
    * token array element.  The keys and values are specific to the
    * rule, and may or may not be common to other rule options.  Typical
    * options keys are 'text' and 'type' but may include others.
    *
    * @param boolean $id_only If true, return only the token number, not
    * a delimited token string.
    *
    * @param string|null $sourceText REFCORR6: the exact authored source
    * span this token replaces, supplied by the claiming rule from the
    * $matches groups its callback received. Stored in $tokenSource, not
    * in $tokens, and read only by Mathinline's recursive expansion.
    *
    * @return string|int By default, return the number of the
    * newly-created token array element with a delimiter prefix and
    * suffix; however, if $id_only is set to true, return only the token
    * number (no delimiters).
    *
    */

    function addToken($rule, $options = array(), $id_only = false, $sourceText = null)
    {
        // Increment this document's token id. parse() resets it with the
        // token array, so independent renders in one PHP process number their
        // placeholders independently as live does.
        $id = $this->nextTokenId++;

        // force the options to be an array
        settype($options, 'array');

        // add the token
        $this->tokens[$id] = array(
            0 => $rule,
            1 => $options
        );

        // REFCORR6: remember the exact source span the claiming rule
        // replaced. Null means the call site did not supply one; the
        // compared token entry above is deliberately unchanged.
        if ($sourceText !== null) {
            $this->tokenSource[$id] = $sourceText;
        }

        // return a value
        if ($id_only) {
            // return the last token number
            return $id;
        } else {
            // return the token number with delimiters
            return $this->delim . $id . $this->delim;
        }
    }

    /**
    *
    * Set or re-set a token with specific information, overwriting any
    * previous rule name and rule options.
    *
    * @access public
    *
    * @param int $id The token number to reset.
    *
    * @param int $rule The rule name to use.
    *
    * @param array $options An associative array of options for the
    * token array element.  The keys and values are specific to the
    * rule, and may or may not be common to other rule options.  Typical
    * options keys are 'text' and 'type' but may include others.
    *
    * @return void
    *
    */

    function setToken($id, $rule, $options = array())
    {
        // reset the token
        $this->tokens[$id] = array(
            0 => $rule,
            1 => $options
        );
    }

    /**
    *
    * Load a rule parser class file.
    *
    * @access public
    *
    * @return bool True if loaded, false if not.
    *
    */

    function loadParseObj($rule)
    {
        $rule = ucwords(strtolower($rule));
        $file = $rule . '.php';
        $class = "Text_Wiki_Parse_$rule";
		
            $loc = $this->findFile('parse', $file);
         
            if ($loc) {
                // found the class
                include_once $loc;
            } else {
                // can't find the class
                $this->parseObj[$rule] = null;
                // can't find the class
                return $this->error(
                	"Parse rule '$rule' not found"
                );
            }

        $this->parseObj[$rule] = new $class($this);

    }

    /**
    *
    * Load a rule-render class file.
    *
    * @access public
    *
    * @return bool True if loaded, false if not.
    *
    */

    function loadRenderObj($format, $rule)
    {
        $format = ucwords(strtolower($format));
        $rule = ucwords(strtolower($rule));
        $file = "$format/$rule.php";
        $class = "Text_Wiki_Render_$format" . "_$rule";

            // load the class
            $loc = $this->findFile('render', $file);
            if ($loc) {
                // found the class
                include_once $loc;
            } else {
                // can't find the class
                return $this->error(
                	"Render rule '$rule' in format '$format' not found"
                );
            }

        $this->renderObj[$rule] = new $class($this);
    }

    /**
    *
    * Load a format-render class file.
    *
    * @access public
    *
    * @return bool True if loaded, false if not.
    *
    */

    function loadFormatObj($format)
    {
        $format = ucwords(strtolower($format));
        $file = $format . '.php';
        $class = "Text_Wiki_Render_$format";

            $loc = $this->findFile('render', $file);
            if ($loc) {
                // found the class
                include_once $loc;
            } else {
                // can't find the class
                return $this->error(
                	"Rendering format class '$class' not found"
                );
            }

        $this->formatObj[$format] = new $class($this);
    }

    /**
    *
    * Add a path to a path array.
    *
    * @access public
    *
    * @param string $type The path-type to add (parse or render).
    *
    * @param string $dir The directory to add to the path-type.
    *
    * @return void
    *
    */

    function addPath($type, $dir)
    {
        $dir = $this->fixPath($dir);
        if (! isset($this->path[$type])) {
            $this->path[$type] = array($dir);
        } else {
            array_unshift($this->path[$type], $dir);
        }
    }

    /**
    *
    * Get the current path array for a path-type.
    *
    * @access public
    *
    * @param string $type The path-type to look up (plugin, filter, or
    * template).  If not set, returns all path types.
    *
    * @return array The array of paths for the requested type.
    *
    */

    function getPath($type = null)
    {
        if (is_null($type)) {
            return $this->path;
        } elseif (! isset($this->path[$type])) {
            return array();
        } else {
            return $this->path[$type];
        }
    }

    /**
    *
    * Searches a series of paths for a given file.
    *
    * @param array $type The type of paths to search (template, plugin,
    * or filter).
    *
    * @param string $file The file name to look for.
    *
    * @return string|bool The full path and file name for the target file,
    * or boolean false if the file is not found in any of the paths.
    *
    */

    function findFile($type, $file)
    {
        // get the set of paths
        $set = $this->getPath($type);

        // start looping through them
        foreach ($set as $path) {
            $fullname = $path . $file;
            if (file_exists($fullname) && is_readable($fullname)) {
                return $fullname;
            }
        }

        // could not find the file in the set of paths
        return false;
    }

    /**
    *
    * Append a trailing '/' to paths, unless the path is empty.
    *
    * @access private
    *
    * @param string $path The file path to fix
    *
    * @return string The fixed file path
    *
    */

    function fixPath($path)
    {
        $len = strlen($this->_dirSep);

        if (! empty($path) &&
            substr($path, -1 * $len, $len) != $this->_dirSep)    {
            return $path . $this->_dirSep;
        } else {
            return $path;
        }
    }

    /**
    *
    * Simple error-object generator.
    *
    * @access public
    *
    * @param string $message The error message.
    *
    * @return object PEAR_Error
    *
    */

    function &error($message)
    {
    	throw new ProcessException($message);
    	// FIX?
    	if (! class_exists('PEAR_Error')) {
    		include_once 'PEAR.php';
    	}
    	return PEAR::throwError($message);
    }

    /**
    *
    * Simple error checker.
    *
    * @access public
    *
    * @param mixed $obj Check if this is a PEAR_Error object or not.
    *
    * @return bool True if a PEAR_Error, false if not.
    *
    */

    function isError(&$obj)
    {
    	return is_a($obj, 'PEAR_Error');
    }
}
