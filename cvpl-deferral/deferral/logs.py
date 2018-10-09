# coding: utf-8
'''
Log provision.
'''

import canvas as cv

from threading import Lock, get_ident
from logging import StreamHandler

_active_logs = dict()
_active_logs_lock = Lock()

def create_log(target):
    ident = get_ident()
    log = cv.logger('uow_defer@%s'%ident)
    log.addHandler(StreamHandler(target))
    with _active_logs_lock:
        _active_logs[ident] = log
    return log

def get_logger():
    log = None
    with _active_logs_lock:
        log = _active_logs[get_ident()]
    return log
