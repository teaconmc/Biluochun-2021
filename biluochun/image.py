'''
Defines /api/image endpoints series.
'''
from io import BytesIO

from flask import Blueprint, redirect, send_file

from .model import Image

def init_image(app):
    '''
    Initialize /api/image/ series endpoints series.
    '''

    bp = Blueprint('image', __name__, url_prefix = '/api/image')

    @bp.route('/<int:img_id>')
    def get_image(img_id):
        if img_id == 1:
            return redirect(app.config['BILUOCHUN_DEFAULT_USER_AVATAR'])
        if img_id == 2:
            return redirect(app.config['BILUOCHUN_DEFAULT_TEAM_AVATAR'])
        img = Image.query.get(img_id)
        return { "error": "Not found" }, 404 if img is None \
            else send_file(BytesIO(img.data), mimetype = 'image/png')

    app.register_blueprint(bp)