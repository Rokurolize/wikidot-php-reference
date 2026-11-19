<?php
// vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4:
/**
 * Format class for the Xhtml rendering
 *
 * PHP versions 4 and 5
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    $Id$
 * @link       http://pear.php.net/package/Text_Wiki
 */

/**
 * Format class for the Xhtml rendering
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Paul M. Jones <pmjones@php.net>
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml extends Text_Wiki_Render {

    public $conf = array(
    	'translate' => HTML_SPECIALCHARS,
    	'quotes'    => ENT_COMPAT,
    	'charset'   => 'UTF-8'
    );

    function pre()
    {
        // attempt to translate HTML entities in the source.
        // get the config options.
        $type = $this->getConf('translate', HTML_ENTITIES);
        // Reference-implementation era bridge (PHP >= 5.4): without
        // ENT_SUBSTITUTE, htmlentities/htmlspecialchars return an empty
        // string for input containing invalid UTF-8 bytes, and the parsed
        // source always contains the \xFF token delimiter. The fossil era
        // passed such bytes through. ENT_SUBSTITUTE keeps the delimiter
        // re-conversion below working; how invalid bytes in user text are
        // treated is an R2 adjudication item (see ref-php/INVENTORY.md).
        $quotes = $this->getConf('quotes', ENT_COMPAT) | ENT_SUBSTITUTE;
        $charset = $this->getConf('charset', 'UTF-8');

        // have to check null and false because HTML_ENTITIES is a zero
        if ($type === HTML_ENTITIES) {

			// keep a copy of the translated version of the delimiter
			// so we can convert it back.
			$new_delim = htmlentities($this->wiki->delim, $quotes, $charset);

			// convert the entities.  we silence the call here so that
			// errors about charsets don't pop up, per counsel from
			// Jan at Horde.  (http://pear.php.net/bugs/bug.php?id=4474)
			$this->wiki->source = @htmlentities(
				$this->wiki->source,
				$quotes,
				$charset
			);

			// re-convert the delimiter
			$this->wiki->source = str_replace(
				$new_delim, $this->wiki->delim, $this->wiki->source
			);

		} elseif ($type === HTML_SPECIALCHARS) {

			// keep a copy of the translated version of the delimiter
			// so we can convert it back.
			$new_delim = htmlspecialchars($this->wiki->delim, $quotes);

			// convert the entities.  we silence the call here so that
			// errors about charsets don't pop up, per counsel from
			// Jan at Horde.  (http://pear.php.net/bugs/bug.php?id=4474)
			$this->wiki->source = @htmlspecialchars(
				$this->wiki->source,
				$quotes
			);

			// re-convert the delimiter
			$this->wiki->source = str_replace(
				$new_delim, $this->wiki->delim, $this->wiki->source
			);
		}
    }

    function post()
    {
        return;
    }

}
