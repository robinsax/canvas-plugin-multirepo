# coding: pyxl
'''
No-script content rendering API for SEO.
'''

import canvas as cv
import canvas.ext as cve

from pyxl import html

from .content import Content

_noscript_content_renderers = dict()

def noscript_content_renderer(content_typ):
    def noscript_content_renderer_inner(func):
        _noscript_content_renderers[content_typ] = func
        return func
    return noscript_content_renderer_inner

@cv.view()
class NoScriptContentView:

    def __init__(self, func, content):
        self.func, self.content = func, content

    def render(self):
        return <noscript>
            { self.func(self.content) }
        </noscript>

@cv.alter_root_page_view
def alter_root_page_view(PageView):

    class NoScriptPageView(PageView):
        def setup(self):
            context = cve.RequestContext.get()

            content_key = getattr(context.__controller__, '__content__', None)
            if not content_key:
                return

            if not self.page_data:
                self.page_data = dict()
            
            def load_one(key):
                content = Content.get(key)
                if content.type in _noscript_content_renderers:
                    self.top_body_views.append(
                        NoScriptContentView(_noscript_content_renderers[content.type], content.content)
                    )
                if content.page_description:
                    self.description = content.page_description
                return content

            if isinstance(content_key, (list, tuple)):
                content_dict = dict()
                for key in content_key:
                    content_dict[key] = load_one(key).content
            else:
                content_dict = load_one(content_key).content
                
            self.page_data['content'] = content_dict

    return NoScriptPageView
