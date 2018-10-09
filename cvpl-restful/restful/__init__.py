# coding: utf-8
'''
RESTful API integration for canvas models.
'''

__version__ = '0.1a'

import canvas as cv

from .ops import query_to_query, request_to_model, request_to_update
from .decorators import query_classmethod

def _nop(*args, **kwargs): pass

def apply(*args, **kwargs):
	'''Generate an API for `model_cls`'''
	def inner_apply(model_cls):

		#	Process keyword arguments.
		region        = kwargs.get('region', model_cls.__table__.name)
		on_handle     = kwargs.get('on_handle', _nop)
		create        = kwargs.get('create', True)
		on_create     = kwargs.get('on_create', _nop)
		query         = kwargs.get('query', True)
		on_query      = kwargs.get('on_query', _nop)
		update        = kwargs.get('update', True)
		on_update     = kwargs.get('on_update', _nop)
		retrieve      = kwargs.get('retrieve', True)
		on_retrieve   = kwargs.get('retrieve', _nop)
		delete        = kwargs.get('delete', True)
		on_delete_cb  = kwargs.get('on_delete', _nop)
		default_query = kwargs.get('default_query', None)

		region_route = '/'.join((str(), 'api', region))

		if create or query:
			class RESTfulCollectionEndpoint: pass
			
			if query:
				def on_get(self, context):
					on_handle(context)
					on_query(context)

					target, condition, order, offset, count = query_to_query(
						model_cls, context.query, default_query
					)
					result = context.session.query(
						target, condition,
						order=order, offset=offset, count=count
					)

					return cv.create_json('success', cv.dictize(result))
				RESTfulCollectionEndpoint.on_get = on_get

			if create:
				def on_put(self, context):
					on_handle(context)
					on_create(context)

					instance = request_to_model(model_cls, context.request)
					context.session.save(instance).commit()

					return cv.create_json('success', {
						'created_id': model_cls.__table__.primary_key.value_on(instance)
					})
				RESTfulCollectionEndpoint.on_put = on_put

			cv.endpoint(region_route)(RESTfulCollectionEndpoint)

		if update or retrieve or delete:
			class RESTfulResourceEndpoint:

				def rest_get_model(self, context):
					return model_cls.rest_get(
						context.route.resource_id, context.session
					)
			
			if retrieve:
				def on_get(self, context):
					on_handle(context)
					on_retrieve(context)
					#	TODO: Variants.
					return cv.create_json('success', cv.dictize(
						self.rest_get_model(context)
					))
				RESTfulResourceEndpoint.on_get = on_get

			if update:
				def on_put(self, context):
					on_handle(context)
					on_update(context)

					resource = self.rest_get_model(context)
					request_to_update(resource, context.request)
					context.session.commit()

					return cv.create_json('success')
				RESTfulResourceEndpoint.on_put = on_put

			if delete:
				def on_delete(self, context):
					on_handle(context)
					on_delete_cb(context)

					context.session.delete(self.rest_get_model(context)).commit()
					return cv.create_json('success')
				RESTfulResourceEndpoint.on_delete = on_delete

			cv.endpoint('/'.join((region_route, '<resource_id>')))(RESTfulResourceEndpoint)

		return model_cls

	if kwargs:
		return inner_apply
	else:
		return inner_apply(args[0])
