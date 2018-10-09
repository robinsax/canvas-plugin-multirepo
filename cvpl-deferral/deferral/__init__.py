# coding: utf-8
'''
Asychronous code execution for canvas.
'''
import canvas as cv

from datetime import datetime, timedelta

config = cv.plugin_config(__name__)
log = cv.logger(__name__)

_deferrables = dict()

from .status import Status
from .model import Deferral
from .logs import get_logger
from .work_handler import on_deferral_init, on_error, handle_until, handle_forever

def enable(func):
	def defer(delay, *args, **kwargs):
		session = cv.create_session()

		unit = Deferral(func.__name__, {
			'args': args,
			'kwargs': kwargs
		}, (datetime.now() + timedelta(seconds=delay)))

		session.save(unit).commit().close()
		return unit.id

	def schedule(invoke_at, *args, **kwargs):
		session = cv.create_session()

		unit = Deferral(func.__name__, {
			'args': args,
			'kwargs': kwargs
		}, invoke_at)

		session.save(unit).commit().close()
		return unit.id

	func.defer = defer
	func.defer_now = lambda *args, **kwargs: defer(0, *args, **kwargs)
	func.schedule = schedule

	_deferrables[func.__name__] = func
	return func

def check(supplied_id, session):
	return session.query(Deferral, Deferral.id == supplied_id, one=True)

def check_all(session):
	return session.query(Deferral, order_by=Deferral.schedule)

@cv.launcher('run-deferred',
	description='Run code deferred by request threads.'
)
def launch_deferred_work(args):
	try:
		handle_forever()
	except KeyboardInterrupt:
		log.info('Caught Ctrl+C, stopping')
	return True
