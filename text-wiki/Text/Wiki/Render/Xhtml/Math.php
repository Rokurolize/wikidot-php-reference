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
 * Math equation.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Math extends Text_Wiki_Render {
    
    public $conf = array();

    /**
     *
     * Renders a token into text matching the requested format.
     *
     * @access public
     *
     * @param array $options The "options" portion of the token (second
     * element).
     *
     * @return string The text rendered from the token options.
     *
     */
    
    function token($options) {
        $content = $options['content'];
        $type = $options['type'];
        // REFCORR3 C-SUSPECT-SERVING-1: an empty or upper-case type is
        // rejected on live, with the equation counter already advanced at
        // parse time. This branch needs no LatexRenderer and is reachable
        // in the harness; the probe bytes are
        // muse-probe-suspect-serving-math-types-ids.
        if (! preg_match('/^[a-z][a-z0-9]*$/', (string) $type)) {
            return '<div class="error-block">' . _('Unsupported math environment "' . $type . '"') . '</div>';
        }
        $hashcode = md5($content . '..' . $type);
        $runData = Ozone::getRunData();
        $site = $runData->getTemp('site');
        $dir = $site->getLocalFilesPath() . '/math/eqs';
        if (!file_exists($dir)) {
            mkdirfull($dir);
        }
        
        $tmpDir = WIKIDOT_ROOT . '/tmp/math';
        if (!file_exists($tmpDir)) {
            mkdirfull($tmpDir);
        }
        
        $imgFile = $hashcode . '.png';
        if (!file_exists($dir . '/' . $imgFile)) {
            $renderer = new LatexRenderer();
            $renderer->setTmpDir($tmpDir);
            $renderer->setOutputDir($dir);
            
            // REFCORR3 C-SUSPECT-SERVING-1: the environment is whatever
            // lower-case name the author gave (align, gather, equation,
            // eqnarray, ...) — the PNG-stub scratch copy's latex-env.log
            // records live asking for exactly \begin{TYPE} ... \end{TYPE}.
            // The old whitelist forced eqnarray*/equation* envelopes.
            $content2 = "\\begin{" . $type . "} " . $content . " \\end{" . $type . "}";
            $renderer->render($content2, $hashcode);
        }
        
        if (!file_exists($dir . '/' . $imgFile)) {
            return '<div class="error-block">' . _('The equation has not been processed correctly. Most prabably it has syntax error(s).') . '</div>';
        }
        
        $label = $options['label'];
        $idPrefix = $this->getConf("id_prefix");
        $idString = ' id="equation-' . $idPrefix . $options['id'] . '" ';
        $equationNumberLabel = '<span class="equation-number">(' . $options['id'] . ')</span>';
        $out = '<div class="math-equation"' . $idString . '><img src="/local--math/eqs/' . $imgFile . '" alt="' . htmlentities($content) . '" /></div>';
        
        return $equationNumberLabel . $out;
    }
}
