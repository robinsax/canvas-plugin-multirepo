//	::style code
//	::export Block

const langs = {
	py: [
		['as class if elif else def import pass from return', 'kw'],
		['self __init__ True False', 'cm']
	],
	jsx: [
		['new if else class return', 'kw'],
		['this', 'cm']
	]
};
const highlight = (codeEl, ext) => {
	let code = codeEl.innerHTML;
	let lang = langs[ext];
	for (var i = 0; i < lang.length; i++) {
		let keywords = lang[i][0].split(' '), 
			cls = lang[i][1];
		for (var j = 0; j < keywords.length; j++) {
			let regex = '(\\s|^|\\(|=)(' + keywords[j] + ')(\\s|,|\\.|\\(|\\))';
			code = code.replace(
				new RegExp(regex, 'g'), 
				(m, a, b, c) => a + '$[' + cls + ']' + b + '\\$' + c
			);
		}
	}

	code = code.replace(/((&lt;.*?&gt;))/g, (m, a) => '<span class="cm">' + a + '</span>');
	code = code.replace(
		/\$\[(.*?)\](.*?)\\\$/g, 
		(m, a, b) => '<span class="' + a + '">' + b + '</span>'
	);
	code = code.replace(
		/'(.*?)'/g,
		(m, a) => '<span class="msc">\'' + a + '\'</span>'
	)
	code = code.replace(/(@.*?)\(/g, (m, a) => '<span class="msc">' + a + '</span>(');
	code = '<div>' + code.split('\n').join('</div><div>') + '</div>';
	code = code.replace(/\t/g, '   ');
	codeEl.innerHTML = code;
}

@cv.view({
	data: {},
	template: data =>
		<div class="code-sample">
			<pre><code>{ typeof data == 'string' ? data : 'Loading...' }</code></pre>
		</div>
})
class Block {
	onceConstructed(url) {
		this.url = url;
	}

	onceCreated() {
		this.data = cv.fetch(this.url);
	}

	onceFetched() {
		let urlParts = this.url.split('.');
		highlight(this.element.querySelector('code'), urlParts[urlParts.length - 1]);
	}
}
