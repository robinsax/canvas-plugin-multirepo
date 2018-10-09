//	::import code, markdown

@cv.page('/')
@cv.view({
	state: {currentCodeI: 0},
	data: {
		codeSamples: [
			['model.py', '/assets/code_samples/model.py'],
			['controllers.py', '/assets/code_samples/controllers.py'],
			['view.jsx', '/assets/code_samples/view.jsx']
		]
	},
	template: (data, state) =>
		<div class="home">
			<div class="landing">
				<div class="col-6 vertical-center align-right brand">
					{ new cv.SVG('/assets/media/canvas_logo.svg') }
				</div>
				<div class="col-6 vertical-center align-left textual">
					<div class="subtext">
						A full stack framework in Python and JavaScript that takes a 
						modern approach to web application development
					</div>
					<ul>
						<li>Plug and play setup</li>
						<li>Solid plugin environment</li>
						<li>Maintainable, extensible codebases</li>
						<li>Great ergonomics</li>
					</ul>
					<button class="next" title="Learn more">. . .</button>
				</div>
			</div>
			<div class="more">
				<div class="col-6 align-left">
					<div class="textual">
						{ new markdown.Markdown('front_example.md') }
					</div>
					<div class="tabs">
						{ cv.comp(data.codeSamples, (item, i) =>
							<div class={ "tab" + (state.currentCodeI == i ? " current" : "") }>
								{ item[0] }
							</div>
						)}
					</div>
					<div class="code-samples">
						{ cv.comp(data.codeSamples, (item, i) =>
							<div class={ "item" + (state.currentCodeI != i ? " hidden" : "") }>
								<span>{ new code.Block(item[1]) }</span>
							</div>
						)}
					</div>
				</div>
				<div class="sep"/>
				<div class="col-6 align-center finale">
					<h1>Like what you see?</h1>
					<p class="background">
						Try it out and let us know what you think.
					</p>
					<a class="clear" href="/start"><button class="big">Get started</button></a>
				</div>
			</div>
		</div>
})
class HomepageView {
	@cv.event('.next')
	scrollToNext() {
		let target = document.querySelector('.more');
		let interval = setInterval(() => {
			if (target.getBoundingClientRect().top <= 0) {
				clearInterval(interval);
			}
			else {
				window.scrollTo(0, window.scrollY + 10);
			}
		}, 5);
	}

	@cv.event('.tab')
	reTabCode(context) {
		this.state.currentCodeI = context.index;
	}
}
