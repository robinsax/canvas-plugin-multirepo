# coding: utf-8
'''
Authorization API.
'''

import canvas as cv

class AuthCheck:

	def __init__(self, error_message, check_fn):
		self.error_message, self.check_fn = error_message, check_fn

	def __call__(self, context_or_meth):
		def check(context):
			if not self.check_fn(context):
				raise cv.Unauthorized(self.error_message)
		
		if callable(context_or_meth):
			def check_dec(self_, context, *args, **kwargs):
				self(context)
				return context_or_meth(self_, context, *args, **kwargs)
			
			check_dec.__name__ = context_or_meth.__name__
			return check_dec
		else:
			check(context_or_meth)

require_admin = AuthCheck('Only administrators can do that', lambda ctx: ctx.user and ctx.user.is_admin)
require_anon = AuthCheck("You can't do that while logged in", lambda ctx: not ctx.user)
require_user = AuthCheck('You must be logged in to do that', lambda ctx: ctx.user is not None)
