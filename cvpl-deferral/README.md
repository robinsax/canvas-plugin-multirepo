# Code execution deferral for canvas

[![Build Status](https://travis-ci.org/robinsax/cvpl-deferral.svg?branch=master)](https://travis-ci.org/robinsax/cvpl-deferral)
[![Coverage Status](https://coveralls.io/repos/github/robinsax/cvpl-deferral/badge.svg?branch=master)](https://coveralls.io/github/robinsax/cvpl-deferral?branch=master)

This plugin exposes an interface for code scheduling and asynchronous invocation.

The following code sample defines a deferrable function and a controller that triggers it.

```python
import canvas as cv

from datetime import datetime, timedelta
from canvas.plugins import deferral

log = cv.logger(__name__)

@deferral.enable
def audit_async(message):
    log.info(message)

@cv.controller('/audited-url')
class AuditedURLController:

    def on_get(self, context):
        audit_async.defer_now('This URL was visited now')
        audit_async.defer(60, 'This URL was visited 60 seconds ago')
        audit_async.schedule(
            datetime.now() + timedelta(days=1),
            'This URL was visited at this time yesterday'
        )

        return 'Thanks from Big Brother'
```

## Usage

Deferred execution occurs in a seperate interpreter instance. This instance is invoked with

```bash
python canvas -i --run-deferred
```

It should be configured to run as a service in production environments.

Any parameters passed into a deferred execution must be JSON serializable and deserializable.
