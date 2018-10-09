# coding: utf-8
'''
The canvas's homepage and plugin repository.
'''

import canvas as cv

plugin_config = cv.plugin_config(__name__)

from . import users, setup, model, api, site
