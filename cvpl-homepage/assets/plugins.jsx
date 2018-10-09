@cv.page('/plugins')
@cv.view({
	data: [],
	template: data =>
		<div class="align-center">
			<div class="col-8">
				<div class="top">
					<h1>search plugins</h1>
					<p>
						plugins are cool!
					</p>
				</div>
				<div class="search-field">
					<i class="fa fa-search"/>
					<input type="text" name="search"/>
				</div>
				<div class="results">
					{ cv.comp(data, plugin =>
						<div class="plugin">
							<h3><div class="badge">cvpl-</div>{ plugin.name }</h3>
							<p>{ plugin.description }</p>
						</div>
					) }
				</div>
			</div>
		</div>
})
class PluginPageView {
	@cv.event('input[name="search"]', 'keyup')
	research(context) {
		let term = context.element.value;
		if (!term) {
			this.data = [];
			return;
		}
		cv.request({
			method: 'get',
			url: '/api/plugins?s=' + term,
			success: resp => this.data = resp.data
		});
	}
}