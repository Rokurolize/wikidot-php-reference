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
        // REFCORR13 R13-AGY2 D08: this SUPERSEDES the R13-MATHNOTES
        // `^[a-z]+$` acceptance rule (which fixed the round-5f `align2`
        // witness but was wrong in the other direction). Live strips every
        // `*` from the authored name FIRST, then checks a fixed AMS/LaTeX
        // allowlist measured on live: equation, align, gather, eqnarray,
        // multline and split. Cached witnesses: `align*`, `gather*` and
        // `equation*` are accepted with the star removed in the envelope;
        // `eqnarray`, `multline` and `split` are accepted; `foobar`,
        // `flalign` and the round-5f `align2` are rejected; `a*b` is
        // rejected with the stripped name `ab` in the error block. No trim
        // and no case folding happen: `align ` and `ALIGN` stay unsupported.
        // The counter and the verbatim stored token value are untouched.
        $env = str_replace('*', '', (string) $type);
        $amsEnvironments = array('equation', 'align', 'gather', 'eqnarray',
            'multline', 'split');
        if (! in_array($env, $amsEnvironments, true)) {
            return '<div class="error-block">' . _('Unsupported math environment "' . $env . '"') . '</div>';
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
            
            // REFCORR13 R13-AGY2 D08: the envelope uses the star-stripped
            // allowlist name (`align*` -> `align`), exactly the live value.
            // The MathJax/PNG wrapper shape itself remains the known external
            // LatexRenderer serving boundary and is deliberately NOT changed.
            $content2 = "\\begin{" . $env . "} " . $content . " \\end{" . $env . "}";
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
