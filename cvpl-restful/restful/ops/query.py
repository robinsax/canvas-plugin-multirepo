# coding: utf-8
'''
Query string to database query conversion.
'''

import re
import canvas as cv

_query_string_operators = list()
def query_string_operator(regex):
	def register_operator(meth):
		_query_string_operators.append((regex, meth))
		return meth
	return register_operator

@query_string_operator(r'^not\(([\w\s]+)\)$')
def invert_operator(match, column, parse):
	return column != parse(match.group(1))

@query_string_operator(r'^in\((.*?),(.*?)\)$')
def range_operator(match, column, parse):
	return (
		(column >= parse(match.group(1))) & 
		(column < parse(match.group(2)))
	).grouped

def query_to_query(model_cls, query_string, default_variant=None):
	'''Convert a query string to a canvas ORM query, distrusting the client.'''
	table = model_cls.__table__

	def protect_key(key):
		while key in table.columns:
			key = ''.join(('_', key))
		return key
	#	Define the query modifier keys without namespace conflict.
	count_key     = protect_key('count')
	offset_key    = protect_key('offset')
	order_key     = protect_key('order')
	variant_key   = protect_key('variant')

	#	Prepare default values.
	query_condition = True
	query_target = model_cls if not default_variant else default_variant(model_cls)
	count = offset = None
	order = list()

	#	Iterate the query string, inspecting each item.
	for key, value in query_string.items():
		#	Check query modifiers.
		if key == count_key:
			try:
				count = int(value)
			except:
				raise cv.BadRequest('"%s" must be an integer'%count_key)
		elif key == offset_key:
			try:
				offset = int(value)
			except:
				raise cv.BadRequest('"%s" must be an integer'%offset_key)
		elif key == order_key:
			attr, desc = value, True
			match = re.match(r'^(\w+)(?:\((asc|desc)(?:ending){0,1}\)){0,1}$', value)
			if match:
				attr = match.group(1)
				descending = match.group(2) == 'desc'

			if attr not in table.columns:
				raise cv.BadRequest('Invalid order "%s"'%attr)

			order.append(getattr(table.columns[attr], 'desc' if descending else 'asc'))
		elif key == variant_key:
			query_target = getattr(model_cls, value, None)
			if not query_target or not getattr(query_target, '__restquery__', False):
				raise cv.BadRequest('No query variant "%s"'%value)
			query_target = query_target()
		else:
			column = table.columns.get(key)
			if not column:
				raise cv.BadRequest('Invalid key "%s"'%key)
			
			def parse_value(one):
				if one == 'null':
					return None
				return column.cast(one)
			
			def parse_one(one):
				for operator in _query_string_operators:
					match = re.match(operator[0], one)
					if match:
						return operator[1](match, column, parse_value)
				return column == parse_value(one)

			query_condition = query_condition & parse_one(value)

	return query_target, query_condition, order, offset, count