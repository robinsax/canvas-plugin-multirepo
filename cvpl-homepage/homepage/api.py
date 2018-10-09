# coding: utf-8
'''
API.
'''

import os
import canvas as cv

from io import BytesIO
from zipfile import ZipFile
from canvas.plugins import users

from .model import Plugin, PluginDependency
from . import plugin_config

@cv.endpoint('/api/plugins', expects='form-data')
class PluginCollectionEndpoint:

	def on_get(self, context):
		'''
		Retrieve a list of plugins.
		'''
		query, session = context[:2]

		condition = True
		if 's' in query:
			condition = Plugin.name.matches(query.s) | Plugin.description.matches(query.s)
		plugins = session.query(Plugin, condition)

		return cv.create_json('success', cv.dictize(plugins))

	@users.require_user
	def on_post(self, context):
		'''
		Upload a plugin.
		'''
		# TODO: Authz.
		request, session = context[:2]

		zip_file = ZipFile(BytesIO(request.data))
		try:
			meta_json = cv.deserialize_json(zip_file.open('.canvas/meta.json').read())
			name, description = meta_json['name'], meta_json['description']
			repo_url = meta_json['repo_url']
			dependencies = meta_json['dependencies']
		except KeyError:
			raise cv.BadRequest('Invalid plugin package (bad meta info)')

		plugin = Plugin(name, description, repo_url)
		session.save(plugin)
		for dependency_name in dependencies:
			dependency = session.query(Plugin, Plugin.name == dependency_name, one=True)
			if not dependency:
				raise cv.UnprocessableEntity('Invalid dependency "%s"'%dependency_name)
			session.save(PluginDependency(plugin, dependency))
		session.commit()

		return cv.create_json('success', {
			'created_id': plugin.id
		})
