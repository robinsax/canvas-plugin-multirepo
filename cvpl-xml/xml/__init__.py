#	coding utf-8
'''
Encoding-aware XML integration for canvas.
'''

import canvas as cv

plugin_config = cv.plugin_config(__name__)

from .exceptions import XMLSyntaxError
from .utils import element_t, element, serialize, deserialize, dict_to_tree
from .model_ext import XMLAdapter
from .xml_io import create_xml
from . import json_ext
