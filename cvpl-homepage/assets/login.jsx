//	::load_model User

@cv.page('/login')
@cv.view({
	formModel: model.User,
	template: () =>
		<div class="align-center">
			<div class="col-6 max-600 align-left">
				<h1>log in to canvas</h1>
				{ new cv.ErrorSummary() }
				<div class="form">
					{ new cv.Field('email', {
						placeholder: 'e.g. Jane.Smith@email.com'
					}) }
					{ new cv.Field('password', {
						placeholder: 'Enter your password...',
						type: 'password'
					}) }
				</div>
				<div class="align-right">
					<button>Log in</button>
				</div>
			</div>
		</div>
})
class LoginView {
	@cv.event('button')
	submitForm() {
		super.submitForm('post', '/api/auth')
			.success(() => window.location = '/dashboard');
	}
}