# coding: utf-8
'''
Pages.
'''

import re
import canvas as cv

from canvas.plugins import users

@cv.alter_root_page_view
def alter_root_page_view(PageView):
	class CustomPageView(PageView):
		def setup(self):
			self.assets = ('site.js', 'site.css', *self.assets, 'decor.js')
			if self.title is None:
				self.title = 'canvas | modern web apps'
			else:
				title = self.title.lower()
				if re.match(r'[0-9]{3}\s', title):
					title = title[3:]
				self.title = ' | '.join((title, 'canvas'))
	return CustomPageView

@cv.page('/', title=None, assets=('home.js', 'home.css'))
class Homepage: pass

@cv.page('/login', title='log in', assets=('login.js',))
class LoginPage: pass

@cv.page('/new-plugin', title='register a plugin', assets=('plugins.js',))
class PluginRegisterPage:

	@users.require_user
	def on_get(self, context):
		return super().on_get(context)

@cv.page('/dashboard', title='my dashboard', assets=('dash.js',))
class DashboardPage:

	@users.require_user
	def on_get(self, context):
		return super().on_get(context)

@cv.page('/plugins', title='plugins', assets=('plugins.js', 'plugins.css'))
class PluginPage: pass
