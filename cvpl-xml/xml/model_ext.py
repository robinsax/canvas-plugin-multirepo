#	coding utf-8
'''
Type adapter and column type definitions.
'''

import canvas as cv
import canvas.ext as cve
import lxml.etree as et

from .utils import element_t, serialize, deserialize
from . import plugin_config

XML_OID = 142

@cve.type_adapter('xml', XML_OID, element_t)
class XMLAdapter:

	def adapt(self, element):
		if element is None:
			return None
		#	Adapt as bytes, removing type postfix.
		return self.existing_adaption(et.tostring(element).decode()) + b'::xml'
	
	def cast(self, serialization):
		if serialization is None:
			return None
		return deserialize(serialization)

cve.update_column_types({
	'xml': cve.BasicColumnType('XML', lazy=True)
})
