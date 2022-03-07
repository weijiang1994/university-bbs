/**
 * Copyright (c) 2003-2022, CKSource Holding sp. z o.o. All rights reserved.
 * For licensing, see LICENSE.md or https://ckeditor.com/legal/ckeditor-oss-license
 */

/* exported initSample */

CKEDITOR.replace('editor1', {
	extraPlugins: 'embed,autoembed,image2',
	height: 500,

	// Load the default contents.css file plus customizations for this sample.
	contentsCss: [
		'http://cdn.ckeditor.com/4.17.2/full-all/contents.css',
		'https://ckeditor.com/docs/ckeditor4/4.17.2/examples/assets/css/widgetstyles.css'
	],
	// Setup content provider. See https://ckeditor.com/docs/ckeditor4/latest/features/media_embed
	embed_provider: '//ckeditor.iframe.ly/api/oembed?url={url}&callback={callback}',

	// Configure the Enhanced Image plugin to use classes instead of styles and to disable the
	// resizer (because image size is controlled by widget styles or the image takes maximum
	// 100% of the editor width).
	image2_alignClasses: ['image-align-left', 'image-align-center', 'image-align-right'],
	image2_disableResizer: true,
	removeButtons: 'PasteFromWord'
});
if ( CKEDITOR.env.ie && CKEDITOR.env.version < 9 )
	CKEDITOR.tools.enableHtml5Elements( document );

// The trick to keep the editor in the sample quite small
// unless user specified own height.
CKEDITOR.config.height = 150;
CKEDITOR.config.width = 'auto';

var initSample = ( function() {
	var wysiwygareaAvailable = isWysiwygareaAvailable(),
		isBBCodeBuiltIn = !!CKEDITOR.plugins.get( 'bbcode' );

	return function() {
		var editorElement = CKEDITOR.document.getById( 'editor' );

		// :(((
		if ( isBBCodeBuiltIn ) {
			editorElement.setHtml(
				'Hello world!\n\n' +
				'I\'m an instance of [url=https://ckeditor.com]CKEditor[/url].'
			);
		}

		// Depending on the wysiwygarea plugin availability initialize classic or inline editor.
		if ( wysiwygareaAvailable ) {
			CKEDITOR.replace( 'editor' );
		} else {
			editorElement.setAttribute( 'contenteditable', 'true' );
			CKEDITOR.inline( 'editor' );

			// TODO we can consider displaying some info box that
			// without wysiwygarea the classic editor may not work.
		}
	};

	function isWysiwygareaAvailable() {
		// If in development mode, then the wysiwygarea must be available.
		// Split REV into two strings so builder does not replace it :D.
		if ( CKEDITOR.revision == ( '%RE' + 'V%' ) ) {
			return true;
		}

		return !!CKEDITOR.plugins.get( 'wysiwygarea' );
	}
} )();

