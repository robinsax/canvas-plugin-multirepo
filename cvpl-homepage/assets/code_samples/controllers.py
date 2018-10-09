import canvas as cv
from .model import Breakfast

@cv.endpoint('/api/breakfasts')
class BreakfastEndpoint:

	def on_get(self, context):
		breakfasts = context.session.query(Breakfast)
		return cv.create_json('success', cv.dictize(breakfasts))

	def on_put(self, context):
		request, cookie, session = context[:3]
		session.save(Breakfast(request.name)).commit()
		return cv.create_json('success')

@cv.page('/', title='Breakfasts', assets=('view.js',))
class BreakfastPage: pass
