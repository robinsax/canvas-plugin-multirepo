#	coding utf-8
'''
API stuff.
'''

import canvas as cv
import canvas.ext as cve

from .exceptions import XMLSyntaxError
from .utils import (
	element, 
	dict_to_tree,
	element_t, 
	serialize, 
	deserialize
)
from . import plugin_config

def create_xml(status, tree=None, code=200, headers=None, mimetype=None):
	pretty = plugin_config.pretty_responses
	if mimetype is None:
		mimetype = 'text/xml' if pretty else 'application/xml'
	
	root = element('response', element('status', status))
	if tree is not None:
		data = element('data')
		if isinstance(tree, (list, tuple)):
			for item in tree:
				data.append(item)
		else:
			data.append(tree)
		
		root.append(data)

	return serialize(root, pretty), code, headers, mimetype

@cve.request_body_parser('text/xml', 'application/xml')
def parse_xml(body):
	try:
		return deserialize(body)
	except XMLSyntaxError:
		raise cv.BadRequest('Invalid body syntax') from None

@cv.on_error
def inspect_error(error_data):
	should_respond = False
	if error_data.in_api_realm:
		if plugin_config.prefer_xml:
			should_respond = True
		else:
			controller = getattr(error_data.context, '__controller__', None)
			if controller:
				should_respond = getattr(controller, '__xml__', None)
	
	if should_respond:
		error_dict = error_data.error_dict
		code = error_dict['code']

		error_data.response = create_xml('error', dict_to_tree(error_dict), code=code)
