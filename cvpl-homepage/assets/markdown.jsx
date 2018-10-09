//	::import !lib/markdown.min
//	::export Markdown

const _markdown = markdown;

@cv.view({
	template: () => <div/>
})
class Markdown {
	onceConstructed(markdownFile) {
		this.markdownFile = markdownFile;
	}

	onceCreated() {
		cv.request({
			method: 'get',
			url: '/assets/markdown/' + this.markdownFile,
			success: markdownContent => {
				this.element.innerHTML = _markdown.toHTML(markdownContent);
			}
		});
	}
}