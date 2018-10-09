#	coding utf-8
'''
Cache management machinery. Decaching priority is based off the 
`persistance_weight` of `CachedFile` objects.
'''

import sys
import psutil
import canvas as cv

from threading import Lock

from .exceptions import CacheSizeError
from . import config

#	Create a log.
log = cv.logger(__name__)

class CachedFile:
	'''An in-memory cache of a file.'''

	def __init__(self, key, contents, load_time):
		'''
		::key The cache key, generally the filename.
		::contents The file content.
		::load_time The time it took to load the file.
		'''
		self.key, self.contents = key, contents
		
		self.content_size = sys.getsizeof(contents)
		self.load_time, self.hits = load_time, 0

	@property
	def persistance_weight(self):
		return (
			self.load_time * 
			(self.hits/config.tuning.hit_threshold) * 
			(self.content_size/config.tuning.filesize_threshold_mb)
		)

	def hit(self):
		self.hits += 1

class Cache:
	'''
	The set of currently cached files. Manages decaching to make room implicitly.
	'''

	def __init__(self, max_size):
		'''::max_size The maximum in-memory cache size.'''
		self.max_size, self.size = max_size, 0
		self.map, self.lock = dict(), Lock()
	
		self.assert_configuration()
		log.debug('Created cache (capacity %sMB)'%self.max_size)

	def assert_configuration(self):
		'''Assert the maximum size is supported.'''
		available = psutil.virtual_memory().available/1000000

		if available < self.max_size:
			raise CacheSizeError('Only ~%sMB available (of configured %sMB)'%(
				available, self.max_size
			))

	def __contains__(self, key):
		return key in self.map

	def __getitem__(self, key):
		with self.lock:
			item = self.map[key]
			item.hit()
		
		return item

	def __setitem__(self, key, item):
		if (self.size + item.content_size) > self.max_size:
			with self.lock:
				ordered = sorted(self.map.values(), key=lambda k: -k.persistance_weight)
				
				while self.size > self.max_size:
					to_remove = ordered.pop()

					log.debug('Decached %s (weight %s) to make room'%(
						to_remove.key, to_remove.persistance_weight
					))
					
					del self.map[to_remove.key]
					self.size -= to_remove.content_size

				self.map[key] = item
		else:
			self.map[key] = item

		log.debug('Cached %s (state %.2f/%.2fMB)', key, self.size, self.max_size)
	