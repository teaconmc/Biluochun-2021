"""
QQ Verify
"""

from functools import wraps

import flask
import requests
from flask import Blueprint
from flask_login import current_user
from sqlalchemy.exc import NoResultFound

from biluochun.form import QQVerify
from biluochun.model import QQ, db

BOT_SECRET = ""
BOT_QUERY_ENDPOINT = ""


def init_qq_api(app):
    bp = Blueprint('qq', __name__, url_prefix='/api/qq')

    @bp.route('/verify', methods=['POST'])
    def verify_qq():
        if flask.request.headers.get("Authorization") != BOT_SECRET:
            return 401

        form = QQVerify()
        if form.validate_on_submit():
            try:
                entry = QQ.query.filter(QQ.qq == form.qq.data).one()
            except NoResultFound:
                # No correspond qq entry
                return {}, 200
            if entry.verify_code == form.code.data:
                entry.verified = True
                db.session.commit()
            return {}, 200
        else:
            return {
                       'error': 'Form contains error. Check "details" field for more information.',
                       'details': form.errors
                   }, 400

    app.register_blueprint(bp)


def check_qq_in_group(qq: str):
    res = requests.get(BOT_QUERY_ENDPOINT + "?qq=" + qq)
    return res.status_code == 200


def is_user_qq_verified(user: int):
    entry = QQ.query.get(user)
    if not entry:
        return False
    return entry.verified

def qq_verify_required(f):
    @wraps(f)
    def qq_verified(*args, **kwargs):
        if not is_user_qq_verified(current_user.id):
            return { 'error': 'You need to verify qq first' }, 403
        return f(args, kwargs)
    return qq_verified
