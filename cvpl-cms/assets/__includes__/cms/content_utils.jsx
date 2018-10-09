//	TODO: Packaging????

window.contentUtils = (() => {
	class ContentUtils {
		renderInlineStyles(text) {
			return text.replace(
				/`(.*?)`/g, (s, m) => '<span class="theme1">' + m + '</span>'
			).replace(
				/\\{0,1}\*(.*?)\*/, (s, m) => '<em>' + m + '</em>'
			).replace(
				/:\\/g, ':'
			);
		}

		renderGenericContent(content) {
			if (content instanceof Array) {
				return this.renderGenericContent({
					tag: 'div',
					children: content
				});
			}
			if (typeof content == 'string') {
				return cv.element('p', {
					'dangerous-markup': this.renderInlineStyles(content)
				});
			}
			else {
				let el = cv.element(content.tag, {}, []);
				if (content.class) {
					el.attributes.class = content.class;
				}
				if (content.text) {
					el.attributes['dangerous-markup'] = this.renderInlineStyles(content.text);
				}
				
				if (content.tag == 'ul' || content.tag == 'ol') {
					cv.iter(content.items, child => {
						el.children.push(cv.element('li', {
							'dangerous-markup': this.renderInlineStyles(child)
						}));
					});
				}
				else {
					cv.iter(content.children, child => {
						el.children.push(this.renderGenericContent(child))
					});
				}
				return el;
			}
		}
	}
	return new ContentUtils();
})();