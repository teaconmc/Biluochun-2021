from flask_dance.contrib.azure import make_azure_blueprint
from flask_login import current_user

def init_authz(app):
    bp = make_azure_blueprint(
        client_id = app.config['BILUOCHUN_OAUTH_CLIENT_ID'],
        client_secret = app.config['BILUOCHUN_OAUTH_CLIENT_SECRET'],
        # TODO: Check if we do need XboxLive.signin scope/permission
        scope = 'User.Read',
        redirect_to = 'dashboard.login',
        # https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-v2-protocols#endpoints
        tenant = 'consumers'
    )

    app.register_blueprint(bp, url_prefix = '/login')
