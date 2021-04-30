'''
Defines /api/profie endpoints series.
'''

from flask import Blueprint, redirect, url_for
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_login import current_user, login_required, logout_user
from sqlalchemy import func

from .form import Avatar, TeamInvite, UserInfo
from .model import Image, OAuth, Team, db
from .util import cleanse_profile_pic, find_team_by_invite, team_summary

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
            current_user.name = form.name.data
            db.session.commit()
            return {}
        else:
            return {
                'error': 'Form contains error. Check "details" field for more information.',
                'details': form.errors
            }, 400
    
    @bp.route('/team', methods = [ 'GET' ])
    @login_required
    def get_team_info():
        if current_user.team_id is not None:
            return team_summary(Team.query.get(current_user.team_id), \
                detailed = True, invitation = True)
        return { 'error': 'You have not joined a team yet!' }, 404

    @bp.route('/team', methods = [ 'POST', 'PUT' ])
    @login_required
    def join_team():
        if current_user.team_id is None:
            form = TeamInvite()
            if form.validate_on_submit():
                team = find_team_by_invite(form.invite_code.data)
                if len(team.members) <= 0:
                    return { 'error': 'Cannot join abandonded team' }, 403
                current_user.team_id = team.id
                db.session.commit()
                return {}
        return {
            'error': 'You have joined a team!'
        }, 409
    
    @bp.route('/team', methods = [ 'DELETE' ])
    @login_required
    def leave_team():
        if current_user.team_id is not None:
            current_user.team_id = None
            db.session.commit()
            return {}
        return {
            'error': 'You have not joined a team yet!'
        }, 404

    @bp.route('/avatar', methods = [ 'GET' ])
    @bp.route('/profile_pic', methods = [ 'GET' ])
    @login_required
    def get_avatar():
        return redirect(url_for('image.get_image', img_id = current_user.profile_pic_id))

    @bp.route('/avatar', methods = [ 'POST' ])
    @bp.route('/profile_pic', methods = [ 'POST' ])
    @login_required
    def update_avatar():
        form = Avatar()
        if form.validate_on_submit():
            next_id = db.session.query(func.max(Image.id)).first()[0]
            if next_id:
                next_id += 1
            else:
                next_id = 3
            avatar = Image(id = next_id, data = cleanse_profile_pic(form.avatar.data))
            db.session.add(avatar)
            current_user.profile_pic_id = next_id
            db.session.commit()
            return {}
        else:
            return {
                'error': 'Form contains error. Check "details" field for more information.',
                'details': form.errors
            }, 400

    bp.storage = SQLAlchemyStorage(OAuth, db.session, user = current_user)
    app.register_blueprint(bp)
