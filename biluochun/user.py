'''
Defines /api/users endpoints series.
'''

from flask import Blueprint, redirect, url_for
from flask.json import jsonify

from .model import User
from .util import user_summary

def init_users_api(app):
    '''
    Initialize the app with /api/users endpoints series.
    '''

    bp = Blueprint('users', __name__, url_prefix = '/api/users')

    @bp.after_request
    def cdn_please_stop(r):
        r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        r.headers['Pragma'] = 'no-cache'
        r.headers['Expires'] = '0'
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r

    @bp.route('/')
    def list_users():
        return jsonify([user_summary(user) for user in User.query.all()])

    @bp.route('/<int:user_id>')
    def show_user(user_id):
        user = User.query.get(user_id)
        return ({ 'error': 'No such user' }, 404) if user is None else user_summary(user)
    
    @bp.route('/<int:user_id>/avatar')
    @bp.route('/<int:user_id>/profile_pic')
    def show_user_avatar(user_id):
        user = User.query.get(user_id)
        if user is None:
            return { 'error': 'No such user' }, 404
        return redirect(url_for('image.get_image', img_id = user.profile_pic_id))

    app.register_blueprint(bp)
