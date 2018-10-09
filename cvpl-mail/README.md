#	Email dispatch and templating for canvas

[![Build Status](https://travis-ci.org/robinsax/cvpl-mail.svg?branch=master)](https://travis-ci.org/robinsax/cvpl-mail)
[![Coverage Status](https://coveralls.io/repos/github/robinsax/cvpl-mail/badge.svg?branch=master)](https://coveralls.io/github/robinsax/cvpl-mail?branch=master)

*It's that simple, really*. 

Install an SMTP server ([postfix](http://www.postfix.org/), for example) then configure this plugin.

The following code sample defines an email template and an initialization callback that sends it.

```python
# coding: pyxl
import canvas as cv

from canvas.plugins import mail
from datetime import datetime

@mail.email
class BootEmail:

	def subject(self, params):
		return 'Boot Alert'

	def body(self, params):
		return <h1>I booted at { params['time'] }</h1>

@cv.on_init
def send_boot_email():
	BootEmail.send('you@yourmail.com', 'boot.html',
		time=datetime.now().strftime('%-I:%M %p %A, %B %-m')
	)
```
