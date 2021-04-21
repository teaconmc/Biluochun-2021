'''
Defines /api/profie endpoints series.
'''

from io import BytesIO

from flask import Blueprint, Response, request, send_file
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_login import current_user, login_required, logout_user

from .form import Avatar, UserInfo
from .model import OAuth, db
from .util import cleanse_profile_pic, team_summary

def init_dashboard(app):
    '''
    Initialize the app with /api/profie endpoints series.
    '''
    bp = Blueprint('dashboard', __name__, url_prefix = '/api/profile')

    @bp.route('/logout', methods = [ 'POST' ])
    @login_required
    def logout():
        '''
        Log out the current user from our system.
        This does not sign out the user from Microsoft's SSO system, unless the 
        request is initiated from Microsoft SSO.
        '''
        logout_user()
        return {}

    @bp.route('/', methods = [ 'GET' ])
    @login_required
    def main_page():
        '''
        Display a short summary of currently logged-in user in JSON format.
        '''
        return {
            'name': current_user.name,
            'team': None if current_user.team is None else team_summary(current_user.team) 
        }

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
            return { 
                'error': 'Form contains error. Check "details" field for more information.', 
                'details': form.errors
            }, 400

    @bp.route('/avatar', methods = [ 'GET' ])
    @bp.route('/profile_pic', methods = [ 'GET' ])
    @login_required
    def get_avatar():
        img = current_user.profile_pic
        if img is None or len(img) == 0:
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
            return {
                'error': 'No valid image file found. Check if you forget to put an image file in request body?'
            }, 400

    bp.storage = SQLAlchemyStorage(OAuth, db.session, user = current_user)
    app.register_blueprint(bp)
