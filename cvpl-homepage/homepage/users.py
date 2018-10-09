# coding: utf-8
'''
User plugin integration.
'''

import canvas as cv

from canvas.plugins import users

class BaseUser:

	def __init__(self, username=None, email=None, password=None):
		self.username, self.email = username, email
		self.set_password(password)

	@property
	def is_admin(self):
		return self.sys_admin

users.initialize({
	'sys_admin': cv.Column('bool', default=False)
}, user_cls=BaseUser)
