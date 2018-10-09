# coding: utf-8
'''
Email stylesheet provision and management.
'''

import canvas as cv
import canvas.ext as cve

base_styles = '''
body {
	background-color: @background;
	color: @text;
}

h1, h2, h3, h4 { color: @title; }
.subtext { color: @subtext; }
a { color: @link; }
'''
compiled_styles = None

def get_styles():
	global compiled_styles
	if not compiled_styles:
		compiled_styles = cve.compile_less(base_styles)
	return compiled_styles