# coding: pyxl
'''
Authentication hooks and helpers.
'''

import canvas as cv
import canvas.ext as cve

from pyxl import html

from . import User, plugin_config

api_key_param, api_key_header = plugin_config.api_key_param, plugin_config.api_key_header

def authorize(user, context=None):
    if not context:
        context = cve.RequestContext.get()
    context.cookie['user_id'] = user.id

def flush_auth(context=None):
    if not context:
        context = cve.RequestContext.get()
    del context.cookie['user_id']

@cv.on_request_received
def auth_user_in_context(context):
    user_query = False
    if 'user_id' in context.cookie:
        user_query = User.id == context.cookie['user_id']
    elif api_key_param in context.query:
        user_query = User.api_key == context.query[api_key_param]
        del context.query[api_key_param]
    elif api_key_header in context.headers:
        user_query = User.api_key == context.headers[api_key_header]
    elif context.request and isinstance(context.request, cve.RequestParameters) and api_key_param in context.request:
        user_query = User.api_key == context.request[(api_key_param, str)]
        del context.request[api_key_param]
    
    context.user = context.session.query(User, user_query, one=True)

@cv.alter_root_page_view
def inject_user_onto_page(PageView):
    class UserInjectedPageView(PageView):
        def asset_fragment(self):
            fragment = super().asset_fragment()
            context = cve.RequestContext.get()

            if context and 'user' in context and context.user:
                user_serialization = cv.serialize_json(cv.dictize(context.user))
            else:
                user_serialization = 'null'
            
            fragment.append(
                <script type="text/javascript">
                    { html.rawhtml(''.join((
                        'window.user = ', user_serialization, ';'
                    ))) }
                </script>
            )
            return fragment
    return UserInjectedPageView
