# coding: pyxl
'''
SMTP email dispatch for canvas.
'''

import os
import canvas as cv
import smtplib as smtp
import canvas.ext as cve

from pyxl import html
from email.mime import multipart, text

from .styles import get_styles

plugin_config = cv.plugin_config(__name__)
on_mail = cve.create_callback_registrar()

class Email:

    def subject(self, params):
        raise NotImplementedError()

    def body(self, params):
        raise NotImplementedError()

    def head(self, params):
        return <frag>
            <style type="text/css">{ get_styles() }</style>
        </frag>
    
    def render(self, params):
        return <html lang="en">
            <head>
                { self.head(params) }
            </head>
            <body>
                { self.body(params) }
            </body>
        </html>
    
    @classmethod
    def send(cls, to, important=False, **params):
        inst = cls()
        sender = plugin_config.sender_address
        if isinstance(to, (list, tuple)):
            to = ','.join(to)
    
        message = multipart.MIMEMultipart()
        message['From'] = sender
        message['To'] = to
        if important:
            message['X-Priority'] = '1'

        message['Subject'] = inst.subject(params)
        message.attach(text.MIMEText(str(inst.render(params)), 'html'))

        on_mail.invoke(message)

        smtp_handler = smtp.SMTP(plugin_config.smtp_handler)
        smtp_handler.sendmail(sender, to, message.as_string())
        smtp_handler.quit()

def email(email_cls):
    return type(email_cls.__name__, (email_cls, Email), dict())
