# coding: utf-8
'''
Enumerable deferral status.
'''

import canvas.ext as cve

from enum import Enum

class Status(Enum):
    PENDING = 0
    IN_PROGRESS = 1
    SUCCESS = 2
    ERROR = 3

@cve.json_serializer(Status)
def serialize_status(status):
	return status.name
