# coding: utf-8
'''
Model updates.
'''

def request_to_update(model, request):
	'''Update a model to reflect the contents of request.'''
	table = model.__class__.__table__
	
	for key, value in request.items():
		#	Assert the key is specifying an existing attribute.
		column = table.columns.get(key)
		if not column:
			raise cv.ValidationErrors({key: 'Invalid key'})
		
		#	Inspect, maybe cast, and assign the value onto the model.
		print(key)
		setattr(model, key, column.cast(value))

	if hasattr(model, '__restupdated__'):
		model.__restupdated__()