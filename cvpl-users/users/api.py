# coding: utf-8
'''
Users API.
'''

import canvas as cv
import canvas.ext as cve

from . import User, _edit_approver
from .auth import authorize, flush_auth
from .authz import require_admin, require_anon, require_user

@cv.endpoint('/api/auth')
class AuthEndpoint:

	@require_anon
	def on_post(self, context):
		request, session = context[:2]

		user = session.query(User, User.email == request[('email', str)], one=True)
		if not user or not user.check_password(request[('password', str)]):
			raise cv.ValidationErrors(summary='Incorrect username or password')

		authorize(user, context)
		return cv.create_json('success')

	@require_user
	def on_delete(self, context):
		flush_auth(context)
		
		return cv.create_json('success')

@cv.endpoint('/api/users')
class UsersCollection:

	@require_admin
	def on_get(self, context):
		query = True
		for key, value in context.query.items():
			if not hasattr(User, key):
				raise cv.ValidationErrors({key: 'Invalid key'})
			column = getattr(User, key)
			value = column.cast(value)
			query = (column == value) & query

		users = context.session.query(User, query)

		return cv.create_json('success', cv.dictize(users))

	#	TODO: Auth check.
	def on_put(self, context):
		request, session = context[:2]

		user = User()
		for key, value in context.request.items():
			if key not in User.__table__.columns:
				raise cv.ValidationErrors({key: 'Invalid key.'})
			
			if key == 'password':
				user.set_password(value)
			else:
				setattr(user, key, value)
		
		session.save(user).commit()
		if not context.user:
			authorize(user, context)

		return cv.create_json('success', {
			'created_id': user.id
		})

#	TODO: Use unpacking.
@cv.endpoint('/api/users/<id>')
class UserInstance:
	
	@require_user
	def on_get(self, context):
		if not context.user.is_admin and not context.user.id == context.route.id:
			raise cv.Unauthorized("You don't have access to that user's information")
		
		user = User.get(context.route.id, context.session)
		if not user:
			raise cv.NotFound(context.route)
		
		return cv.create_json('success', user)

	@require_user
	def on_put(self, context):
		if not context.user.is_admin and not context.user.id == context.route.id:
			raise cv.Unauthorized("You don't have permission to edit that user's information")
		
		user = User.get(context.route.id, context.session)
		_edit_approver(user, context)
		
		for key, value in context.request.items():
			if not hasattr(User, key):
				raise cv.ValidationErrors({key: 'Invalid key'})
			column = getattr(User, key)
			value = column.cast(value)

			setattr(user, key, value)

		context.session.commit()

		return cv.create_json('success')
