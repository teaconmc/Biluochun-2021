# -*- coding: utf-8 -*-

'''
Biluochun is the self-help admission system used by TeaCon to assist management.
'''

from flask import Flask
from flask_cors import CORS

from .authz import init_authz
from .dashboard import init_dashboard
from .image import init_image
from .model import init_db
from .team import init_team_api
from .user import init_users_api

class ReverseProxied():
    '''
    Wrapper class to enforce HTTPS.
    Adapted from https://stackoverflow.com/a/37842465
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['wsgi.url_scheme'] = 'https'
        return self.app(environ, start_response)

def create_app():
    '''
    Entry point to initialize the Flask application.
    '''
    app = Flask(__name__)
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    app.config.from_envvar('BILUOCHUN_CONFIG_PATH')
    # Wrapped with CORS
    CORS(app, supports_credentials = True, vary_header = True)

    init_db(app)
    init_authz(app)
    init_dashboard(app)
    init_image(app)
    init_team_api(app)
    init_users_api(app)

    @app.route('/')
    def index():
        return {} # Empty json, implying "it is at least running"

    @app.after_request
    def cdn_please_stop(r):
        r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        r.headers['Pragma'] = 'no-cache'
        r.headers['Expires'] = '0'
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r

    @app.after_request
    def cdn_please_do_this_for_images(r):
        r.headers['Cache-Control'] = 'immutable'

    app.after_request_funcs = {
        'image': [ cdn_please_do_this_for_images ],
        'azure': [ cdn_please_stop ],
        'dashboard': [ cdn_please_stop ],
        'team': [ cdn_please_stop ],
        'users': [ cdn_please_stop ]
    }
    return app
