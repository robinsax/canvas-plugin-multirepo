#	coding utf-8
'''
Basic utilities.
'''

import re
import lxml.etree as et

from .exceptions import XMLSyntaxError, ConversionError
from . import plugin_config

element_t = type(et.Element('x'))

def element(tag, *children, **attribs):
	el = et.Element(tag, attribs)
	for child in children:
		if isinstance(child, element_t):
			el.append(child)
		else:
			el.text = str(child)
	return el

def dict_to_tree(source, root_tag=None):
	if not source:
		return element('null')
	
	root = element(root_tag) if root_tag else []

	if isinstance(source, dict):
		for key, value in source.items():
			root.append(dict_to_tree(value, key))
	elif isinstance(source, (list, tuple)):
		for item in source:
			root.append(dict_to_tree(item, 'item'))
	else:
		#	TODO: Leverage JSON serializers in core (rename them too).
		if isinstance(root, list):
			raise ConvertionError('Cannot represent primitive as element: %s'%root)

		root.text = str(source)

	return root

def deserialize(data, encoding=None):
	'''
	Deserialize XML represented as either bytes or a string into an lxml 
	Element.

	Raise a SyntaxError if parsing fails.

	:encoding The encoding to use. By default, will use the configured default
		encoding.
	'''
	if encoding is None:
		encoding = plugin_config.default_encoding
	
	if not isinstance(data, bytes):
		data = data.encode(encoding)
	
	if plugin_config.normalize_whitespace:
		data = re.sub(rb'\s+', b' ', data)
	parser = et.XMLParser(ns_clean=True, remove_blank_text=plugin_config.strip_whitespace, recover=True, encoding=encoding)
	try:
		return et.fromstring(data, parser=parser)
	except et.XMLSyntaxError as ex:
		raise XMLSyntaxError(str(ex)) from None

def serialize(element, pretty=False, as_bytes=False, encoding=None):
	'''
	Serialize an XML element to a string or bytes.

	:pretty Whether to pretty print the output.
	:as_bytes Whether to return a byte representation.
	:encoding The encoding with which to encode the serialization to bytes.
	'''
	if as_bytes and encoding is None:
		encoding = plugin_config.default_encoding
	else:
		encoding = 'unicode'
	
	return et.tostring(element, pretty_print=pretty, encoding=encoding)
