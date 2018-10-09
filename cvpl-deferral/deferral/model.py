# coding: utf-8
'''
The execution deferral model
'''

import canvas as cv

from datetime import datetime

from .status import Status

@cv.model('deferral_queue', {
	'id': cv.Column('uuid', primary_key=True),
	'callable_name': cv.Column('text', nullable=False),
	'arguments': cv.Column('json', nullable=False),
	'return_value': cv.Column('json'),
	'status': cv.Column('int', default=Status.PENDING.value),
	'schedule': cv.Column('datetime', default=datetime.now),
	'log': cv.Column('text')
})
class Deferral:

	def __init__(self, callable_name, arguments, schedule):
		self.callable_name, self.arguments = callable_name, arguments
		self.schedule = schedule

	@classmethod
	def pop(cls, session):
		query = (cls.schedule <= datetime.now()) & (cls.status == Status.PENDING.value)
		instance = session.query(cls, query, order=cls.schedule.asc, one=True, for_update=True)

		if instance:
			instance.status = Status.IN_PROGRESS.value
			session.commit(instance)
		return instance

	@cv.dictized_property
	def status_label(self):
		return ' '.join(Status(self.status).name.split('_')).title()

	@property
	def started(self):
		return self.status is not Status.PENDING

	@property
	def finished(self):
		return (
			self.status is not Status.PENDING and 
			self.status is not Status.IN_PROGRESS
		)

	@property
	def error(self):
		return self.status is Status.ERROR

	@property
	def success(self):
		return self.status is Status.SUCCESS
	
	def do_return(self, success, return_value, log):
		self.status = Status.SUCCESS.value if success else Status.ERROR.value
		self.return_value = return_value
		self.log = log

		self.__session__.commit(self)
