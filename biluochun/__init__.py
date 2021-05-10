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
from .webhook import init_webhook_config

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
    init_webhook_config(app)

    @app.route('/')
    def index():
        return {"version": "1"}

    return app
