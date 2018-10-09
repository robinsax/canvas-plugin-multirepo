#	coding utf-8
'''
XML value serialization and deserialization for JSON.
'''

import canvas as cv
import canvas.ext as cve

from .exceptions import XMLSyntaxError
from .utils import element_t, serialize, deserialize
from . import plugin_config

@cve.json_serializer(element_t)
def serialize_xml_as_json_value(element):
	if plugin_config.xml_placeholder_values_in_json:
		return '<XML: %s>'%element.tag
	else:
		return serialize(element)
