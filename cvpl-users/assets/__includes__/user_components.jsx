class ConfirmPasswordValidator {
	constructor() {
		this.errorMessage = 'The passwords you supplied do not match';
	}

	validate(value) {
		return this.field.parent.fields.password.value == value;
	}
}