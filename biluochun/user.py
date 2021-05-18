'''
Defines /api/users endpoints series.
'''

from flask import Blueprint, redirect, request, url_for
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
        r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
        r.headers['Pragma'] = 'no-cache'
        r.headers['Expires'] = '0'
        return r

    @bp.route('/')
    def list_users():
        users = []
        if request.args.get('all', False, type = bool):
            users = User.query.all()
        else:
            page_index = request.args.get('page', 1, type = int)
            page_size = request.args.get('size', 10, type = int)
            users = User.query.paginate(page_index, page_size, error_out = False).items
        return jsonify([user_summary(user) for user in users])

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
