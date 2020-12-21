# -*- coding: utf-8 -*-

from .api import init_api
from .authz import init_authz
from .dashboard import init_dashboard
from .model import init_db
from flask import Flask, redirect, render_template, url_for
from flask_cors import CORS
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
import hashlib
import secrets

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_envvar('BILUOCHUN_CONFIG_PATH')
    # Wrapped with CORS
    CORS(app)
    
    app.secret_key = hashlib.sha256(b"\x00" + secrets.token_bytes(30) + b"\x00").hexdigest()

    init_db(app)
    init_authz(app)
    init_dashboard(app)
    init_api(app)

    @app.route('/')
    def index():
        if current_user.is_anonymous:
            return render_template('index.html', text_content = "TeaCon 2021 报名系统")
        else:
            return redirect(url_for('dashboard.main_page'))

    return app
