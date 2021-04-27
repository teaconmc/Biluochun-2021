from io import BytesIO

from flask import Blueprint, send_file
from flask.json import jsonify

from .model import User
from .util import user_summary

def init_users_api(app):
    '''
    Initialize the app with /api/users endpoints series.
    '''

    bp = Blueprint('users', __name__, url_prefix = '/api/users')

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
            return { 'error': 'No such user' }
        return send_file(BytesIO(user.profile_pic), mimetype = 'image/png')

    app.register_blueprint(bp)
