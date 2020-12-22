from .api import summary
from .model import Team, User, db
from flask import Blueprint, redirect, render_template, url_for
from flask_dance.contrib.azure import azure
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

def init_dashboard(app):
    bp = Blueprint('dashboard', __name__, url_prefix = '/dashboard')

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        # id is the primary key, so we can do this
        return User.query.get(id)

    @bp.route('/login')
    def login():
        if azure.authorized:
            ms_profile = azure.get('/v1.0/me').json()
            uid = int(ms_profile['id'], 16)
            user = User.query.get(uid)
            if user == None:
                user = User(id = uid, name = ms_profile['displayName'])
                db.session.add(user)
                db.session.commit()
            login_user(user)
            return {}
        else:
            return { 'error': 'Not logged in yet' }, 401

    @bp.route('/logout')
    @login_required
    def logout():
        # Log out local account
        logout_user()
        # Log out from the Microsoft Identity platform
        # See: https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-protocols-oidc#send-a-sign-out-request
        return redirect("https://login.microsoftonline.com/common/oauth2/v2.0/logout?post_logout_redirect_uri=" + url_for("index", _external=True))

    @bp.route('/')
    @login_required
    def main_page():
        return { 'name': current_user.name, 'team': summary(user.team) if not user.team == None else None }
    
    app.register_blueprint(bp)
