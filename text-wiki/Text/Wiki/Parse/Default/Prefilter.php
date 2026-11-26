<?php

/**
* 
* "Pre-filter" the source text.
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
* "Pre-filter" the source text.
* 
* Convert DOS and Mac line endings to Unix, concat lines ending in a
* backslash \ with the next line, convert tabs to 4-spaces, add newlines
* to the top and end of the source text, compress 3 or more newlines to
* 2 newlines.
*
* @category Text
* 
* @package Text_Wiki
* 
* @author Paul M. Jones <pmjones@php.net>
* 
*/

class Text_Wiki_Parse_Prefilter extends Text_Wiki_Parse {

    /**
    * 
    * Simple parsing method.
    *
    * @access public
    * 
    */
    
    function parse()
    {
        // convert DOS line endings
        $this->wiki->source = str_replace("\r\n", "\n",
            $this->wiki->source);
        
        // convert Macintosh line endings
        $this->wiki->source = str_replace("\r", "\n",
            $this->wiki->source);
        
        // trim "whitespace lines" 
        $this->wiki->source = preg_replace("/^\s+$/m", '', $this->wiki->source);
        
       // // concat lines ending in a backslash
       // $this->wiki->source = str_replace("\\\n", "",
        
        // convert tabs to four-spaces
        $this->wiki->source = str_replace("\t", "    ",
            $this->wiki->source);
           
        // REFCORR37: remember whether the unpadded input ended in an
        // empty center marker. The synthetic end padding would otherwise
        // make that EOF-only shape indistinguishable from a mid-document
        // empty marker line, which live does consume.
        $this->wiki->vars['prefilter_terminal_empty_center'] =
            preg_match('/(?:^|\n)= [ \t]*\z/', $this->wiki->source) === 1;

        // add extra newlines at the top and end; this
        // seems to help many rules.
        $this->wiki->source =  "\n".$this->wiki->source . "\n\n";
        // finally, compress all instances of 3 or more newlines
        // down to two newlines.
        $find = "/(\n[ ]*){3,}/m";
        $replace = "\n\n";
        $this->wiki->source = preg_replace($find, $replace,
            $this->wiki->source);
        
        // R2 CORRECTION (2026-11-20): the fossil's next step
        // stripped the sequence utf8_encode("\xFC") twice
        // ('\u{00fc}\u{00fc}') from the source. Live does NOT
        // strip it: probe muse-probe-r2f-frame1 renders the
        // sequence intact (conformance-refphp/frame/). Removed.
    }

}
