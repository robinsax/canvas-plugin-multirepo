# coding: utf-8
'''
Users and authorization faculties for canvas.
'''

#	TODO: Clean pkging.

import canvas as cv

from werkzeug.security import check_password_hash, generate_password_hash

plugin_config = cv.plugin_config(__name__)

AuthCheck = require_admin = require_anon = require_user = None
User = _edit_approver = None

def composite_authz(*checks):
	def composite_check(context):
		for check in checks:
			if check.check_fn(context):
				return True
		return False
	
	#	TODO: Improve msg.
	return AuthCheck("You aren't authorized to do that", composite_check)

get_email_format_constraint = lambda: cv.RegexConstraint('Invalid email address', r'[\w\.\-]+@[\-\w]+(?:\.[\-\w]+)+')

def initialize(schema_update=dict(), user_cls=object, 
		edit_approver=lambda *a: True):
	global User, AuthCheck, require_admin, require_anon, require_user, \
		_edit_approver
	
	user_schema = {
		'id': cv.Column('uuid',
			cv.PrimaryKeyConstraint()
		),
		'api_key': cv.Column('uuid'),
		'username': cv.Column('text',
			cv.NotNullConstraint(),
			cv.UniquenessConstraint('That username is already taken')
		),
		'email': cv.Column('text', 
			cv.NotNullConstraint(),
			get_email_format_constraint(),
			cv.UniquenessConstraint('That email is already registered')
		),
		'password': cv.Column('text',
			cv.NotNullConstraint(),
			dictized=False
		)
	}

	#	Allow plugins to update the schema, removing unwanted fields.
	for key, value in schema_update.items():
		if value is None:
			del user_schema[key]
			continue
		user_schema[key] = value

	@cv.model('users', user_schema)
	class User(user_cls):

		def set_password(self, password):
			if not password:
				self.password = None
			else:
				self.password = generate_password_hash(password)

		def check_password(self, password):
			return check_password_hash(self.password, password)

	_edit_approver = edit_approver

	from .authz import AuthCheck as a, require_admin as b, require_anon as c, \
		require_user as d

	AuthCheck = a
	require_admin, require_anon, require_user = b, c, d

	from . import auth, api

	return User
