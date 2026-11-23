<?php

/**
* 
* Parse for URLS in the source text.
* 
* @category Text
* 
* @package Text_Wiki
* 
* @author Paul M. Jones <pmjones@php.net>
* 
* @license LGPL
* 
* @version $Id$
* 
*/

/**
* 
* Parse for URLS in the source text.
* 
* Various URL markings are supported: inline (the URL by itself),
* numbered or footnote reference (where the URL is enclosed in square
* brackets), and named reference (where the URL is enclosed in square
* brackets and has a name included inside the brackets).  E.g.:
*
* inline    -- http://example.com or www.example.com
* numbered  -- [http://example.com]
* described -- [http://example.com Example Description]
*
* When rendering a URL token, this will convert URLs pointing to a .gif,
* .jpg, or .png image into an inline <img /> tag (for the 'xhtml'
* format).
*
* Token options are:
* 
* 'type' => ['inline'|'footnote'|'descr'] the type of URL
* 
* 'href' => the URL link href portion
* 
* 'text' => the displayed text of the URL link
* 
* @category Text
* 
* @package Text_Wiki
* 
* @author Paul M. Jones <pmjones@php.net>
* 
*/

class Text_Wiki_Parse_Url extends Text_Wiki_Parse {

    /**
    * 
    * Keeps a running count of numbered-reference URLs.
    * 
    * @access public
    * 
    * @var int
    * 
    */
    
    public $footnoteCount = 0;

    /**
    * 
    * URL schemes recognized by this rule.
    * 
    * @access public
    * 
    * @var array
    * 
    */
    
    public $conf = array(
        'schemes' => array(
            'http://',
            'https://',
            'ftp://',
            'gopher://',
            'news://',
            'mailto:',
            'mms://',
            // R2-inlined: live Wikidot autolinks these additional schemes
            // (ftml URL rule WIKIDOT_ONLY_AUTOLINK_SCHEMES plus the corpus pin
            // test/link/autolink-wikidot-schemes/wikidot.html). The fossil list
            // predates them; this is a fossil-era artifact correction (C1).
            'ssh://',
            'git://',
            'sftp://',
            'svn://',
            'telnet://',
            'cvs://'
        )
    );

    /**
    * 
    * Constructor.
    * 
    * We override the constructor so we can comment the regex nicely.
    * 
    * @access public
    * 
    */
    
    function __construct(&$obj)
    {
        parent::__construct($obj);
        
        // convert the list of recognized schemes to a regex-safe string,
        // where the pattern delim is a slash
        $tmp = array();
        $list = $this->getConf('schemes', array());
        foreach ($list as $val) {
            $tmp[] = preg_quote($val, '/');
        }
        $schemes = implode('|', $tmp);
        
        // build the regex
        $this->regex =
            "(?:(?:$schemes)" . // allowed schemes
            "(?:" . // start pattern
            "[^ \\/\"\'{$this->wiki->delim}]*\\/" . // no spaces, backslashes, slashes, double-quotes, single quotes, or delimiters;
            ")*" . // end pattern
            "[^ \\t\\n\\/\"\'{$this->wiki->delim}]*" .
            "[A-Za-z%0-9\\/?=&~_])";
        $this->regexLiberal =
            "(?:(?:$schemes)" . // allowed schemes
            "(?:" . // start pattern
            "[^ \\/\"\'{$this->wiki->delim}]*\\/" . // no spaces, backslashes, slashes, double-quotes, single quotes, or delimiters;
            ")*" . // end pattern
            "[^ \\t\\n\\/\"{$this->wiki->delim}]*)";
            
    }

    /**
    * 
    * Find three different kinds of URLs in the source text.
    *
    * @access public
    * 
    */
    
    function parse()
    {
        // -------------------------------------------------------------
        // 
        // Described-reference (named) URLs.
        // 
        
        // the regular expression for this kind of URL
        $tmp_regex = '/\[(\*)?((?:' . $this->regexLiberal . ')|(?:#[a-zA-Z0-9_\-%]*)|(?:\/[^ \\t\\n\"\''.$this->wiki->delim.']*)) ([^\]'.$this->wiki->delim.']+)\]/';
        
        // use a custom callback processing method to generate
        // the replacement text for matches.
        $this->wiki->source = preg_replace_callback(
            $tmp_regex,
            array(&$this, 'processDescr'),
            $this->wiki->source
        );
        
        $postVars = $this->getConf("post_vars");
        
        if($postVars){
        		// enable %%foo%% variables to act in described links
        		$tmp_regex = 	'/\[(\*)?(%%[^%]+%%[^ ]*) ([^\]]+)\]/';
        		$this->wiki->source = preg_replace_callback(
	            $tmp_regex,
	            array(&$this, 'processPV'),
	            $this->wiki->source
	        );
        }

        // -------------------------------------------------------------
        // 
        // Normal inline URLs.
        // 
        
        // the regular expression for this kind of URL
        
        $tmp_regex = '/(^|[^A-Za-z])(\*)?(' . $this->regex . ')(.*?)/';
        
        // use the standard callback for inline URLs
        $this->wiki->source = preg_replace_callback(
            $tmp_regex,
            array(&$this, 'process'),
            $this->wiki->source
        );
    }

    /**
    * 
    * Process inline URLs.
    * 
    * @param array &$matches
    * 
    * @param array $matches An array of matches from the parse() method
    * as generated by preg_replace_callback.  $matches[0] is the full
    * matched string, $matches[1] is the first matched pattern,
    * $matches[2] is the second matched pattern, and so on.
    * 
    * @return string The processed text replacement.
    * 
    */ 
    
    function process($matches)
    {
        // R2-inline1: the fossil's bare-URL matching is preserved here. An
        // earlier owner attempt split a double-bracket URL target at a pipe,
        // following ftml; the coordinator's live probe
        // muse-probe-r2in1-x-x04 shows live keeps the pipe inside the target,
        // reproducing the PRE-correction reference byte-for-byte and confirming
        // the standing F-R2-44 finding. That split was therefore reverted; the
        // pipe-in-target mismatch is a candidate ftml divergence, not a
        // reference correction.
        // C4 (reference bug, live-settled by muse-probe-r2in1-x-x45): an
        // inline-math opener is a boundary for a bare URL, as ftml's
        // wikidot_automatic_url_end stops at '[['. Stop the automatic URL
        // there and leave the opener for the Mathinline rule rather than
        // swallowing it into the href. This does not touch pipe handling.
        $url = $matches[3];
        $trailing = isset($matches[6]) ? $matches[6] : '';
        $math = strpos($url, '[[');
        if ($math !== false) {
            // A pipe immediately before the opener belongs to the label
            // surface, not the target, when the opener follows it.
            if ($math > 0 && $url[$math - 1] === '|') {
                $math -= 1;
            }
            $trailing = substr($url, $math) . $trailing;
            $url = substr($url, 0, $math);
        }
        // set options
        $options = array(
            'type' => 'inline',
            'href' => $url,
            'text' => $url
        );

        if($matches[2] == '*'){
        		$options['target']='_blank';
        }
        // tokenize
        // REFCORR6: the token claims only the URL bytes (and a leading
        // star), while $matches[1] and $trailing are returned outside it.
        $claimed = ((isset($matches[2]) && $matches[2] === '*') ? '*' : '') . $url;
        return $matches[1] . $this->wiki->addToken($this->rule, $options, false, $claimed) . $trailing;
    }

    /**
    * 
    * Process described-reference (named-reference) URLs.
    * 
    * Token options are:
    *     'type' => ['inline'|'footnote'|'descr'] the type of URL
    *     'href' => the URL link href portion
    *     'text' => the displayed text of the URL link
    * 
    * @param array &$matches
    * 
    * @param array $matches An array of matches from the parse() method
    * as generated by preg_replace_callback.  $matches[0] is the full
    * matched string, $matches[1] is the first matched pattern,
    * $matches[2] is the second matched pattern, and so on.
    * 
    * @return string The processed text replacement.
    * 
    */ 
    
    function processDescr(&$matches)
    {
        // C5 (reference bug, live-settled by muse-probe-r2in1-x-x02): a
        // described URL whose label contains an inline-math opener is not
        // claimed by Url; ftml and live leave the described form to be split
        // into a bare autolink plus a Mathinline span. Yield the whole match
        // so the later rules can claim their shapes.
        if (isset($matches[3]) && strpos($matches[3], '[[$') !== false) {
            return $matches[0];
        }
        // REFCORR6 C-SUSPECT3-1 (m1-code): a described match that has
        // swallowed the math closer's `$]` fragment must yield, so
        // Mathinline can claim the whole `[[$ ... $]]` body live
        // preserves. Narrowed deliberately to the math surface: a
        // generic `]]` guard would also stop unrelated described URLs
        // from being claimed and move cases outside this correction.
        // REFCORR13 D05: the REFCORR6 `$]` yield is a math-surface
        // guard. It fires only when the described match has swallowed
        // the math closer's `$]]` tail (the doubled `]]` before `$]`),
        // as in the m1-code pin. A plain described link ending in `$`
        // has no doubled closer and must be claimed normally.
        if (strpos($matches[0], '$]') !== false &&
                strpos($matches[0], ']]') !== false) {
            return $matches[0];
        }
        // set options
        $options = array(
            'type' => 'descr',
            'href' => $matches[2],
            'text' => $matches[3]
        );
        
        if($matches[1] == '*'){
        		$options['target']='_blank';
        }
        
        // tokenize; the described form is claimed whole (REFCORR6).
        return $this->wiki->addToken($this->rule, $options, false, $matches[0]);
    }
    
     function processPV(&$matches)
    {
        // set options
        $options = array(
            'type' => 'descr',
            'href' => $matches[2],
            'text' => $matches[3]
        );
        
        if($matches[1] == '*'){
        		$options['target']='_blank';
        }
        
        // tokenize; the %%var%% described form is claimed whole (REFCORR6).
        return $this->wiki->addToken($this->rule, $options, false, $matches[0]);
    }
}
