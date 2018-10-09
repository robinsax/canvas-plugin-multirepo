#	coding utf-8
'''
File storage and in-memory caching of files for canvas. Files are stored in the
configured directory to which the serving user must have read and write access.
'''

import os
import time
import mimetypes
import canvas as cv

#	Load the plugin config and create a log.
config = cv.plugin_config(__name__)
log = cv.logger(__name__)

from .exceptions import NoSuchFileError
from .cache import Cache, CachedFile

#	Create the cache.
_cache = Cache(config.cache_size_mb)

def store(filename, contents):
	'''Store a file as `filename`'''
	#	Decide mode and path.
	mode = 'wb' if isinstance(contents, bytes) else 'w'
	full_path = os.path.join(cv.__home__, config.storage_dir, filename)

	#	Write the file.
	with open(full_path, mode) as output_file:
		output_file.write(contents)

def retrieve(filename, is_bytes=True):
	'''Retrieve a file.'''
	#	Check the cache.
	if filename in _cache:
		return _cache[filename].contents

	#	Decide on mode an path.
	mode = 'rb' if is_bytes else 'b'
	full_path = os.path.join(cv.__home__, config.storage_dir, filename)
	#	Assert a file exists.
	if not os.path.exists(full_path):
		raise NoSuchFileError(full_path)

	#	Load and cache.
	start = time.time()
	with open(full_path, mode) as input_file:
		contents = input_file.read()
	load_time = time.time() - start

	log.debug('Loaded %s in %.2fs', full_path, load_time)
	_cache[filename] = CachedFile(filename, contents, load_time)

	return contents

def serve(filename, code=200, headers=None, mimetype=None, as_bytes=True):
	'''
	Return a response containing the file called `filename` or raise a 404.
	'''
	if mimetype is None:
		mimetype, *other = mimetypes.guess_type(filename)

	try:
		contents = retrieve(filename, is_bytes=as_bytes)
	except NoSuchFileError:
		raise cv.NotFound(filename)

	return contents, code, headers, mimetype
