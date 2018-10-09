# coding: utf-8
'''
Site models.
'''

import canvas as cv

@cv.model('plugins', {
	'id': cv.Column('uuid', primary_key=True),
	'name': cv.Column('text', 
		cv.NotNullConstraint(),
		cv.UniquenessConstraint('A plugin with that name already exists.')
	),
	'description': cv.Column('longtext'),
	'repo_url': cv.Column('text', nullable=False)
})
class Plugin:

	def __init__(self, name, description, repo_url):
		self.name, self.description = name, description
		self.repo_url = repo_url

@cv.model('plugin_dependencies', {
	'id': cv.Column('uuid', primary_key=True),
	'dependent_id': cv.Column('fk:plugins.id'),
	'dependency_id': cv.Column('fk:plugins.id')
})
class PluginDependency:

	def __init__(self, dependent, dependency):
		self.dependent_id = dependent.id
		self.dependency_id = dependency.id
