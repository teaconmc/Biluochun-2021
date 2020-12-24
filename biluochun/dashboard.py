from .api import summary
from .model import OAuth, Team, User, db
from flask import Blueprint, Response, redirect, send_file, url_for
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.azure import azure
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from io import BytesIO
from PIL import Image
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired, URL, ValidationError

def validate_team(form, field):
    if field.data != None and Team.query.get(field.data) == None:
        raise ValidationError(f"Team #{field.data} does not exist")

class UserInfo(FlaskForm):
    name = StringField('name', validators = [ DataRequired() ])
    profile_pic = FileField(validators = [ FileRequired(), FileAllowed([ 'jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'webp' ]) ])
    team = IntegerField('team', validators = [ validate_team ])

class TeamInfo(FlaskForm):
    name = StringField('name', validators = [ DataRequired() ])
    desc = StringField('desc')
    repo = StringField('repo', validators = [ URL() ])

def init_dashboard(app):
    bp = Blueprint('dashboard', __name__, url_prefix = '/dashboard')

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        # id is the primary key, so we can do this
        return User.query.get(id)

    @bp.route('/login')
    def login():
        if azure.authorized:
            ms_profile = azure.get('/v1.0/me').json()
            uid = int(ms_profile['id'], 16)
            user = User.query.get(uid)
            if user == None:
                user = User(id = uid, name = ms_profile['displayName'])
                db.session.add(user)
                db.session.commit()
            login_user(user)
            return {} # TODO Redirect back to front-end
        else:
            return { 'error': 'Not logged in yet' }, 401

    @bp.route('/logout')
    @login_required
    def logout():
        # Log out local account
        logout_user()
        # Log out from the Microsoft Identity platform
        # See: https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-protocols-oidc#send-a-sign-out-request
        return redirect("https://login.microsoftonline.com/common/oauth2/v2.0/logout?post_logout_redirect_uri=" + url_for("index", _external=True))

    @bp.route('/')
    def main_page():
        if current_user.is_anonymous:
            return { 'error': 'Not logged in yet' }
        else:
            return { 'name': current_user.name, 'team': None if current_user.team == None else summary(current_user.team) }
    
    def cleanse_profile_pic(raw):
        '''
        Read the image and convert to png format regardless.
        '''
        img = Image.open(raw)
        cleansed = BytesIO()
        img.save(cleansed, format = 'png')
        return cleansed.getvalue()

    @bp.route('/avatar')
    @bp.route('/profile_pic')
    @login_required
    def get_profile_pic():
        img = current_user.profile_pic
        if img == None or len(img) == 0:
            return Response(None, 204)
        else:
            return send_file(BytesIO(img), mimetype = 'image/png')
    
    @bp.route('/update', methods = [ 'POST' ])
    def update_personal_info():
        form = UserInfo()
        if form.validate_on_submit():
            try:
                current_user.name = form.name.data
                current_user.profile_pic = cleanse_profile_pic(form.profile_pic.data)
                current_user.team_id = form.team.data
                db.session.commit()
                return {}
            except e:
                return { 'error': 'Error occured while updating info.' }, 500
        else:
            return { 'error': 'Form contains error. Check that you have entered a valid display name and a valid team number.'}, 400

    bp.storage = SQLAlchemyStorage(OAuth, db.session, user = current_user)
    app.register_blueprint(bp)
