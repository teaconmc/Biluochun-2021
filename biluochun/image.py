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
        img = Image.query.get(img_id)
        if img is None:
            return { "error": "Not found" }, 404
        return send_file(BytesIO(img.data), mimetype = 'image/png')

    app.register_blueprint(bp)