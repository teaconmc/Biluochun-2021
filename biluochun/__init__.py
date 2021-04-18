# -*- coding: utf-8 -*-

'''
Biluochun is the self-help admission system used by TeaCon to assist management.
'''

from flask import Flask
from flask_cors import CORS

from .authz import init_authz
from .dashboard import init_dashboard
from .model import init_db
from .team import init_team_api
from .user import init_users_api

def create_app():
    '''
    Entry point to initialize the Flask application.
    '''
    app = Flask(__name__)
    app.config.from_envvar('BILUOCHUN_CONFIG_PATH')
    # Wrapped with CORS
    CORS(app, supports_credentials = True)

    init_db(app)
    init_authz(app)
    init_dashboard(app)
    init_team_api(app)
    init_users_api(app)

    @app.route('/')
    def index():
        return {} # Empty json, implying "it is at least running"

    return app
