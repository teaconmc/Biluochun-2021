'''
Defines /api/profie endpoints series.
'''

import secrets

from flask import Blueprint, redirect, url_for
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_login import current_user, login_required, logout_user
from sqlalchemy.sql import exists

from .form import Avatar, TeamInvite, UserInfo, QQSet
from .model import Image, OAuth, Team, db, QQ
from .qq import check_qq_in_group, qq_verify_required
from .util import cleanse_profile_pic, find_team_by_invite, team_summary


def init_dashboard(app):
    '''
    Initialize the app with /api/profie endpoints series.
    '''
    bp = Blueprint('dashboard', __name__, url_prefix='/api/profile')

    @bp.after_request
    def cdn_please_stop(r):
        r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
        r.headers['Pragma'] = 'no-cache'
        r.headers['Expires'] = '0'
        return r

    @bp.route('/logout', methods=['POST'])
    @login_required
    def logout():
        '''
        Log out the current user from our system.
        This does not sign out the user from Microsoft's SSO system, unless the 
        request is initiated from Microsoft SSO.
        '''
        logout_user()
        return {}

    @bp.route('/', methods=['GET'])
    @login_required
    def main_page():
        '''
        Display a short summary of currently logged-in user in JSON format.
        '''
        return {
            'name': current_user.name,
            'team': None if current_user.team is None else team_summary(current_user.team)
        }

    @bp.route('/', methods=['POST'])
    @login_required
    def update_personal_info():
        form = UserInfo(target_user=current_user)
        if form.validate_on_submit():
            if form.name.data:
                current_user.name = form.name.data
            db.session.commit()
            return {}
        else:
            return {
                       'error': 'Form contains error. Check "details" field for more information.',
                       'details': form.errors
                   }, 400

    @bp.route('/team', methods=['GET'])
    @login_required
    def get_team_info():
        if current_user.team_id is not None:
            return team_summary(Team.query.get(current_user.team_id),
                                detailed=True, invitation=True)
        return {'error': 'You have not joined a team yet!'}, 404

    @bp.route('/team', methods=['POST', 'PUT'])
    @login_required
    @qq_verify_required
    def join_team():
        if current_user.team_id is None:
            form = TeamInvite()
            if form.validate_on_submit():
                team = find_team_by_invite(form.invite_code.data)
                if not team.members:
                    return {'error': 'Cannot join disbanded team'}, 403
                current_user.team = team
                db.session.commit()
                return {}
            else:
                return {
                           'error': 'Form contains error. Check "details" field for more information.',
                           'details': form.errors
                       }, 400
        return {
                   'error': 'You have joined a team!'
               }, 409

    @bp.route('/team', methods=['DELETE'])
    @login_required
    def leave_team():
        if current_user.team_id is not None:
            current_user.team_id = None
            db.session.commit()
            return {}
        return {
                   'error': 'You have not joined a team yet!'
               }, 404

    @bp.route('/avatar', methods=['GET'])
    @bp.route('/profile_pic', methods=['GET'])
    @login_required
    def get_avatar():
        return redirect(url_for('image.get_image', img_id=current_user.profile_pic_id))

    @bp.route('/avatar', methods=['POST'])
    @bp.route('/profile_pic', methods=['POST'])
    @login_required
    @qq_verify_required
    def update_avatar():
        form = Avatar()
        if form.validate_on_submit():
            current_user.profile_pic = Image(id=None, data=cleanse_profile_pic(form.avatar.data))
            db.session.commit()
            return {}
        else:
            return {
                       'error': 'Form contains error. Check "details" field for more information.',
                       'details': form.errors
                   }, 400

    @bp.route('/team/invite', methods=['POST'])
    @login_required
    def reset_invite():
        team = current_user.team
        if team is None:
            return {'error': 'You are not in a team yet!'}, 404
        new_invite = secrets.token_hex(8)
        team.invite = new_invite
        db.session.commit()
        return {'invite': new_invite}

    @bp.route('/qq', methods=['GET'])
    @login_required
    def get_qq_state():
        qq = QQ.query.get(current_user.id)
        if not qq:
            return {
                       'error': 'No qq provided'
                   }, 404
        return {
                   'qq': qq.qq,
                   'verified': qq.verified,
                   'verify_code': qq.verify_code
               }, 200

    @bp.route('/qq', methods=['POST'])
    def set_qq():
        form = QQSet()
        if form.validate_on_submit():
            if QQ.query(exists().where(QQ.qq == form.qq.data)).scalar():
                return {'error': '这个 QQ 已经被他人占用'}, 409
            if check_qq_in_group(form.qq.data):
                old_entry = QQ.query.get(current_user.id)
                if old_entry:
                    db.session.delete(old_entry)
                new_qq = QQ()
                new_qq.qq = form.qq.data
                new_qq.verified = False
                new_qq.user_id = current_user.id
                new_qq.verify_code = secrets.token_hex(8)
                db.session.add(new_qq)
                db.session.commit()
                return {}, 200
            else:
                return {
                           'error': '请先加入选手群'
                       }, 403
        else:
            return {
                       'error': 'Form contains error. Check "details" field for more information.',
                       'details': form.errors
                   }, 400

    bp.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)
    app.register_blueprint(bp)
