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
 * Button.
 *
 * @category   Text
 * @package    Text_Wiki
 * @author     Michal Frackowiak
 * @license    http://www.gnu.org/copyleft/lesser.html  LGPL License 2.1
 * @version    Release: @package_version@
 * @link       http://pear.php.net/package/Text_Wiki
 */
class Text_Wiki_Render_Xhtml_Button extends Text_Wiki_Render {

    public $conf = array();

	function token($options){
    	
    	$type = strtolower($options['type']);
    	$text = $options['text'];
    	$style = $options['style'];
    	$class = $options['class'];

    	$allowedTypes = array(
    		'edit',
    		'edit-append',
    		'edit-sections',
    		'history',
    		'print',
    		'files',
    		'tags',
    		'source',
    		'talk',
    		'backlinks',
    		'rename',
    		'delete',
    		'parent',
    		'edit-meta',
    		'watchers',
    		'set-tags'

    	);
    	
    	$defaultText = array(
    		'edit' => _('edit'),
    		'edit-append' => _('append'),
    		'edit-sections' => _('edit sections'),
    		'history' => _('history'),
    		'print' => _('print'),
    		'files' => _('files'),
    		'tags' => _('tags'),
    		'source' => _('view source'),
    		'talk' => _('talk'),
    		'backlinks' => _('backlinks'),
    		'rename' => _('rename'),
    		'delete' => _('delete'),
    		'parent' => _('parent'),
    		'edit-meta' => _('edit meta'),
    		'watchers' => _('watchers')
    		
    	);
    	
    	$jsOnclick = array(
    		'edit' => 'WIKIDOT.page.listeners.editClick(event)',
    		'edit-append' => 'WIKIDOT.page.listeners.append(event)',
    		'edit-sections' => 'WIKIDOT.page.listeners.toggleEditSections(event)',
    		'history' => 'WIKIDOT.page.listeners.historyClick(event)',
    		'print' => 'WIKIDOT.page.listeners.printClick(event)',
    		'files' => 'WIKIDOT.page.listeners.filesClick(event)',
    		'tags' => 'WIKIDOT.page.listeners.editTags(event)',
    		'source' => 'WIKIDOT.page.listeners.viewSourceClick(event)',
    		'talk' => "window.location.href='/talk:'+WIKIREQUEST.info.pageUnixName",
    		'backlinks' => 'WIKIDOT.page.listeners.backlinksClick(event)',
    		'rename' => 'WIKIDOT.page.listeners.renamePage(event)',
    		'delete' => 'WIKIDOT.page.listeners.deletePage(event)',
    		'parent' => 'WIKIDOT.page.listeners.parentClick(event)',
    		'edit-meta' => 'WIKIDOT.page.listeners.editMetaClick(event)',
    		'watchers' => 'WIKIDOT.page.listeners.watchersClick(event)',
    		'set-tags' => "WIKIDOT.page.listeners.updateTagsByButton(event, '')"

    	);
    	
    	//$jsOnload = array(
    	//	'talk' => "this.href='/talk:'+WIKIREQUEST.info.pageUnixName; alert(this.href);"
    	
    	$hrefs = array();
    	
    	if(!in_array($type, $allowedTypes)){
    		return '<div class="error-block"><em>'.$type.'</em> is not a valid button type</div>';	
    	}
    	
    	// REFCORR13 R13-AGY2 D10: live guards only an ABSENT `text` attribute
    	// (a null/isset test), not a falsy one. `text="0"` and `text=""` pass
    	// here, then the falsy default at line 110 finds no `set-tags` entry in
    	// $defaultText and leaves an empty label, yielding `<a></a>` on live.
    	// Cached witnesses: muse-probe-agy-hunt-m08a/m08b.
    	if($type === 'set-tags' && !isset($text)){
    		return '<div class="error-block">You need to set text for set-tags button.</div>';	
    	}
    	
    	// ok, fine
    	
    	if(!$class){
    		$class = "wiki-standalone-button";
    	}
    	
    	if(!$text){
    		$text = $defaultText[$type];
    	}

    	$out = '<a class="'.htmlspecialchars($class, ENT_COMPAT, 'UTF-8').'" ';
    	if($style){
    		$out .= 'style="'.htmlspecialchars($style, ENT_COMPAT, 'UTF-8').'" ';	
    	} 
    	$out .= 'href="'.($hrefs[$type]?$hrefs[$type]:'javascript:;').'" ';
    	$out .= ($jsOnclick[$type]?'onclick="'.$jsOnclick[$type].'" ':' ');
    	
    	$out .= '>';
    	$out .= htmlspecialchars($text, ENT_COMPAT, 'UTF-8');
    	$out .= '</a>';
    	
    	return $out;

    }
}
