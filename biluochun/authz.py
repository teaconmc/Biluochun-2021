from .model import User, db
from datetime import datetime, timedelta, timezone
from flask import redirect, url_for
from flask_dance.contrib.azure import azure, make_azure_blueprint
from flask_login import LoginManager
import jwt

def init_authz(app):
    bp = make_azure_blueprint(
        # TODO: Check if we do need XboxLive.signin scope/permission
        scope = 'User.Read',
        redirect_to = 'azure.complete',
        # https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-v2-protocols#endpoints
        tenant = 'consumers'
    )

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def get_user(id):
        # id is the primary key, so we can do this
        return User.query.get(id)

    @login_manager.request_loader
    def load_user_from_token(req):
        auth = req.headers.get("Authorization")
        if auth and auth.startswith('JWT '):
            try:
                data = jwt.decode(auth[4:], app.secret_key, algorithms = [ 'HS512' ])
                user = get_user(data['uid'])
                return user
            except Exception as e:
                return None
        else:
            return None

    @login_manager.unauthorized_handler
    def no_auth():
        return { 'error': 'Not logged in yet' }, 401

    @bp.route('/complete')
    def complete():
        if azure.authorized:
            ms_profile = azure.get('/v1.0/me').json()
            uid = int(ms_profile['id'], 16)
            user = User.query.get(uid)
            if user == None:
                user = User(id = uid, name = ms_profile['displayName'])
                db.session.add(user)
                db.session.commit()
            timestamp = datetime.now(timezone.utc)
            token = jwt.encode({ 
                'uid': uid,
                'nbf': timestamp,
                'exp': timestamp + timedelta(days = 1)
            }, app.secret_key, algorithm = 'HS512')
            return { 'token': token }
        else:
            return { 'error': 'Not logged in yet' }, 401

    app.register_blueprint(bp, url_prefix = '/login')
