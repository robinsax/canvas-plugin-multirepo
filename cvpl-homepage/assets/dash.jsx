@cv.page('/dashboard')
@cv.view({
	template: () =>
		<div class="col-6">
			<h3>Hello, { user.username }</h3>
		</div>
})
class DashboardPage {}