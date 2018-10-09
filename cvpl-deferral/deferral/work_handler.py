# coding: utf-8
'''
Deferred execution management.
'''

import time
import canvas as cv
import canvas.ext as cve

from io import StringIO
from queue import Queue, Empty
from threading import Thread

from .model import Deferral
from .logs import create_log
from . import config, _deferrables

log = cv.logger(__name__)
on_deferral_init = cve.create_callback_registrar()
on_error = cve.create_callback_registrar()

_stop = False

def _worker(queue):
	while not _stop:
		try:
			deferral, session = queue.get(timeout=config.poll_time)
		except Empty:
			time.sleep(config.poll_time)
			continue
		
		callable_ = _deferrables[deferral.callable_name]
		target = StringIO()
		callable_log = create_log(target)

		log.debug('Invoking %s: %s'%(
			deferral.callable_name,
			deferral.arguments
		))
		callable_log.info('Invoked')

		args = deferral.arguments['args']
		kwargs = deferral.arguments['kwargs']
		try:
			return_value = callable_(*args, **kwargs)
			deferral.do_return(True, {'value': return_value}, target.getvalue())
		except BaseException as ex:
			ex_format = cve.format_exception(ex)
			callable_log.error(ex_format)
			log.error(ex_format)

			deferral.do_return(False, {'error': str(ex)}, target.getvalue())
			deferral.crashed_by = ex
			on_error.invoke(deferral)

		session.close()
		time.sleep(config.poll_time)

def handle_until(condition_generator):
	global _stop

	on_deferral_init.invoke()

	queue = Queue(config.max_queue_size)
	threads = []

	for i in range(config.worker_count):
		thread = Thread(target=_worker, args=(queue,), daemon=False)
		threads.append(thread)
		thread.start()

	log.info('Beginning deferred execution')
	session = None
	try:
		while not condition_generator():
			session = cv.create_session()
			unit_of_work = Deferral.pop(session)
			
			if unit_of_work:
				#	Worker will close the session once it's done.
				queue.put((unit_of_work, session))
			else:
				session.close()
				time.sleep(config.poll_time)
	except BaseException as ex:
		log.warning(cve.format_exception(ex))
		if session:
			session.close()

	log.info('Stopping workers...')
	_stop = True
	for thread in threads:
		thread.join()

def handle_forever():
	handle_until(lambda: False)
