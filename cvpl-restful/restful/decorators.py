# coding: utf-8
'''
Decorator definitions.
'''

def query_classmethod(meth):
	meth.__restquery__ = True
	return classmethod(meth)
