# coding: utf-8
'''
Content discovery and provision.
'''

import os
import yaml
import json
import canvas as cv
import canvas.ext as cve

from json import JSONDecodeError as JSONParserError
from yaml.parser import ParserError as YAMLParserError

from .exceptions import NoSuchContent, ContentSyntaxError

log = cv.logger(__name__)

class ParserError(JSONParserError, YAMLParserError): pass

class Content:
	instances = dict()

	def __init__(self, typ, content, page_description):
		self.type, self.content = typ, content
		self.page_description = page_description

	@classmethod
	def create(cls, name, content_data):
		def attributize(item):
			if isinstance(item, dict):
				for key, value in item.items():
					item[key] = attributize(value)
				item = cve.AttributedDict(item)
			elif isinstance(item, (list, tuple)):
				for i, value in enumerate(item):
					item[i] = attributize(value)
			return item

		instance = Content(
			content_data.get('type'), 
			attributize(content_data['content']),
			content_data.get('page_description')
		)
		cls.instances[name] = instance
		return instance

	@classmethod
	def get(cls, name):
		if cv.config.development.debug:
			occur = cv.get_path('content', '%s.yaml'%name)
			parser = yaml.load
			if not occur:
				occur = cv.get_path('content', '%s.json'%name)
				parser = json.load
				if not occur:
					raise NoSuchContent(name)

			with open(occur) as content_file:
				return Content.create(name, parser(content_file))

		if name not in cls.instances:
			raise NoSuchContent(name)

		return cls.instances[name]

	@classmethod
	def items(cls):
		return cls.instances.items()

def get_content(content_key):
	return Content.get(content_key).content

@cv.on_init
def load_contents():
	log.info('Finding static content...')
	for content_dir in cve.get_path_occurrences('content', is_dir=True):
		for filename in os.listdir(content_dir):
			content_name, ext = filename.split('.')
			if ext == 'yaml':
				parser = yaml.load
			elif ext == 'json':
				parser = json.load
			else:
				continue

			with open(os.path.join(content_dir, filename)) as content_file:
				try:
					loaded_content = parser(content_file)
				except ParserError as ex:
					raise ContentSyntaxError(str(ex)) from None
				Content.create(content_name, loaded_content)

	log.info('\n'.join((
		'Loaded content:', *(item[0] for item in Content.items())
	)))
