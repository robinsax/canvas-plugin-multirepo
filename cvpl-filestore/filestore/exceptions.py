#	coding utf-8
'''
Exceptions.
'''

class CacheSizeError(Exception):
	'''
	Raised when the configured cache size exceeds the available memory.
	'''
	pass

class NoSuchFileError(Exception):
	'''Raised when a non-existant file is `retrieve`d.'''
	pass
