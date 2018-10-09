@cv.page('/')
@cv.view({
	data: cv.fetch('/api/breakfasts'),
	template: data =>
		<div class="col-6">
			<h1>Breakfasts</h1>
			{ !data ? <span>Loading breakfasts...</span> :
				<ul>{ cv.comp(data, breakfast => 
					<li>{ breakfast.item }</li>
				)}</ul> 
			}
			<div class="align-right">
				{ new cv.Field('name', {label: 'Breakfast Name'}) }
				<button id="add">Add</button>
			</div>
		</div>
})
class HelloWorldView {
	@cv.event('#add')
	submitForm() {
		super.submitForm('put', '/api/breakfasts')
			.success(this.fetch.bind(this));
	}
}
