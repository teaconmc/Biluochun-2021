# -*- coding: utf-8 -*-

from .api import init_api
from .authz import init_authz
from .dashboard import init_dashboard
from .model import init_db
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_envvar('BILUOCHUN_CONFIG_PATH')
    # Wrapped with CORS
    CORS(app)

    init_db(app)
    init_authz(app)
    init_dashboard(app)
    init_api(app)

    @app.route('/')
    def index():
        return {} # Empty json, implying "everything functional"

    return app
