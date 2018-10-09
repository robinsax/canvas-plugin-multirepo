#	File storage and retrieval for canvas

[![Build Status](https://travis-ci.org/robinsax/cvpl-filestore.svg?branch=master)](https://travis-ci.org/robinsax/cvpl-filestore)
[![Coverage Status](https://coveralls.io/repos/github/robinsax/cvpl-filestore/badge.svg?branch=master)](https://coveralls.io/github/robinsax/cvpl-filestore?branch=master)

This plugin exposes an interface for storing, retrieving, and serving files of arbitrary
type.

It transparently implements an in-memory cache.

The following code sample defines a controller to which files can be stored and retrieved.

```python
import canvas as cv

from canvas.plugin import filestore

@cv.controller('/files/<filename>', expects='*')
class FilesController:

	def on_put(self, context):
		filestore.store(context.route.filename, context.request)
		return cv.create_json('success')
	
	def on_get(self, context):
		return filestore.serve(context.route.filename)
```
