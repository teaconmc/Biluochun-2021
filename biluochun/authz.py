from flask import redirect
from flask_dance.contrib.azure import azure, make_azure_blueprint
from flask_login import LoginManager, login_user
from sqlalchemy import func

from .model import User, db

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
    def get_user(user_id):
        # id is the primary key, so we can do this
        return User.query.get(user_id)

    @login_manager.unauthorized_handler
    def no_auth():
        return { 'error': 'Not logged in yet' }, 401

    @bp.route('/complete')
    def complete():
        if azure.authorized:
            # Note: OData query $select won't work if the account is an @outlook.com account
            # (aka Microsoft account). It would work if the account in question is an 
            # office 365 account instead.
            # Ref: https://stackoverflow.com/questions/50013804/
            # Ref: https://github.com/microsoftgraph/microsoft-graph-docs/issues/2117
            ms_profile = azure.get('/v1.0/me?$select=id,displayName').json()
            uid = ms_profile['id'].lower()
            user = User.query.filter_by(ms_id = uid).first()
            if user is None:
                next_id = db.session.query(func.max(User.id)) + 1
                user = User(id = next_id, ms_id = uid, name = ms_profile['displayName'])
                db.session.add(user)
                db.session.commit()
            login_user(user)
            return redirect(app.config['FRONTEND_URL'])
        else:
            return { 'error': 'Not logged in yet' }, 401

    app.register_blueprint(bp, url_prefix = '/api/login')
