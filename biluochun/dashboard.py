from .form import Avatar, TeamInfo, UserInfo
from .model import OAuth, Team, User, db
from .util import cleanse_profile_pic, find_team_by_invite, team_summary
from flask import Blueprint, Response, request, redirect, send_file, url_for
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_login import current_user, login_required, logout_user
from io import BytesIO

def init_dashboard(app):
    bp = Blueprint('dashboard', __name__, url_prefix = '/api/profile')

    @bp.route('/logout', methods = [ 'POST' ])
    @login_required
    def logout(): # TODO Do we still need this?
        # Log out local account
        # logout_user()
        # Log out from the Microsoft Identity platform
        # See: https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-protocols-oidc#send-a-sign-out-request
        return redirect("https://login.microsoftonline.com/common/oauth2/v2.0/logout?post_logout_redirect_uri=" + url_for("index", _external=True))

    @bp.route('/', methods = [ 'GET' ])
    @login_required
    def main_page():
        return { 'name': current_user.name, 'team': None if current_user.team == None else team_summary(current_user.team) }   

    @bp.route('/', methods = [ 'POST' ])
    @login_required
    def update_personal_info():
        form = UserInfo()
        if form.validate_on_submit():
            try:
                current_user.name = form.name.data
                current_user.team_id = form.team.data
                db.session.commit()
                return {}
            except Exception as e:
                return { 'error': 'Error occured while updating info.', 'details': str(e) }, 500
        else:
            return { 'error': 'Form contains error. Check "details" field for more information.', 'details': form.errors }, 400

    @bp.route('/avatar', methods = [ 'GET' ])
    @bp.route('/profile_pic', methods = [ 'GET' ])
    @login_required
    def get_avatar():
        img = current_user.profile_pic
        if img == None or len(img) == 0:
            return Response(None, 204)
        else:
            return send_file(BytesIO(img), mimetype = 'image/png')

    @bp.route('/avatar', methods = [ 'POST' ])
    @bp.route('/profile_pic', methods = [ 'POST' ])
    @login_required
    def update_avatar():
        raw_img = None
        if form:
            form = Avatar()
            raw_img = form.avatar.data
        else:
            raw_img = request.stream # TODO Validate it
            
        if raw_img:
            current_user.profile_pic = cleanse_profile_pic(raw_img)
            db.session.commit()
            return {}
        else:
            return { 'error': 'No valid image file found. Check if you forget to put an image file in request body?' }, 400

    bp.storage = SQLAlchemyStorage(OAuth, db.session, user = current_user)
    app.register_blueprint(bp)
