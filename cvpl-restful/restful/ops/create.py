# coding: utf-8
'''
Backdoor model creation.
'''

from .update import request_to_update

def request_to_model(model_cls, request):
	'''Create a new model instance based on the contents of request.'''
	instance = model_cls.__new__(model_cls)

	#	TODO: canvas should support better.
	instance.__dirty__ = dict()
	for column in model_cls.__table__.columns.values():
		column.apply_to_model(instance)
	
	request_to_update(instance, request)
	return instance
