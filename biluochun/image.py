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
        raw = Image.query.get(img_id)
        if raw is None:
            return { "error": "Not found" }, 404
        img = Image.open(raw)
        jpg = BytesIO()
        img.save(jpg, format = 'jpeg')
        return send_file(jpg, mimetype = 'image/jpeg')
    
    @bp.after_request
    def setup_cache_policy(r):
        r.headers['Cache-Control'] = 'immutable'
        return r

    app.register_blueprint(bp)