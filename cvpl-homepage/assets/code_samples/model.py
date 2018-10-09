import canvas as cv

@cv.model({
	'id': cv.Column('uuid', primary_key=True),
	'name': cv.Column('text', nullable=False)
})
class Breakfast:

	def __init__(self, name):
		self.name = name
