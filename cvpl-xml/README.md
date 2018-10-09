# XML integration for canvas

[![Build Status](https://travis-ci.org/robinsax/cvpl-xml.svg?branch=master)](https://travis-ci.org/robinsax/cvpl-xml)
[![Coverage Status](https://coveralls.io/repos/github/robinsax/cvpl-xml/badge.svg?branch=master)](https://coveralls.io/github/robinsax/cvpl-xml?branch=master)

XML integration for canvas, leveraging the lxml ElementTree implementation.

Includes:

* The addition of an XML column type.
* Support for XML-based API interfaces.
* An XML creation utility.

## Features

Incoming request bodies with an XML `Content-Type` header will be provided to handler
functions as lxml `Element`s. Note that endpoints expecting XML request bodies should
specify so in their decorator with the `expects='xml'` option.

Model attributes corresponding to XML columns should be assigned lxml `Element`s. When
loaded, those attributes will maintain that type.

The following code sample provides an XML-based re-implementation of the breakfast example 
from the canvas core.

```python
import canvas as cv
from canvas.plugins import xml

#    Define the XML-based breakfast model.
@cv.model('xml_breakfasts', {
    'id': cv.Column('serial', primary_key=True),
    'manifest': cv.Column('xml')
})
class XMLBreakfast:

    def __init__(self, manifest):
        self.manifest = manifest

#    Define an endpoint for creating and retrieving XML-based breakfasts.
@cv.endpoint('/api/xml_breakfast', expects='xml')
class XMLBreakfastEndpoint:

    def on_get(self, context):
        retrieved = context.session.query(XMLBreakfast, one=True)

        return xml.create_xml('success', retrieved.manifest)

    def on_post(self, context):
        instance = XMLBreakfast(context.request)
        context.session.save(instance).commit()

        return xml.create_xml('success', xml.element('created_id', instance.id))
```
