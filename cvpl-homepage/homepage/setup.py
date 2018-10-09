# coding: utf-8
'''
First time setup.
'''

import canvas as cv

from canvas.plugins.users import User

@cv.on_post_init
def create_admin():
	session = cv.create_session()

	if session.query(User, User.sys_admin == True, one=True):
		return
	
	#	TODO: Don't expose.
	admin = User('admin', 'admin@localhost.x', 'password101')
	admin.sys_admin = True
	session.save(admin).commit()
