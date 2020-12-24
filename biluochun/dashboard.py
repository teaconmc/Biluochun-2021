from .api import summary
from .form import TeamInfo, UserInfo
from .model import OAuth, Team, User, db
from flask import Blueprint, Response, redirect, send_file, url_for
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.azure import azure
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from io import BytesIO
from PIL import Image
from sqlalchemy import func

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
    @login_required
    def update_personal_info():
        form = UserInfo()
        if form.validate_on_submit():
            try:
                current_user.name = form.name.data
                current_user.profile_pic = cleanse_profile_pic(form.profile_pic.data)
                current_user.team_id = form.team.data
                db.session.commit()
                return {}
            except Exception as e:
                return { 'error': 'Error occured while updating info.', 'details': str(e) }, 500
        else:
            return { 'error': 'Form contains error. Check "details" field for more information.', 'details': form.errors }, 400

    @bp.route('/team/new', methods = [ 'POST' ])
    @login_required
    def create_team():
        if current_user.team_id == None or current_user.team_id <= 0:
            next_id = db.session.query(func.max(Team.id)) + 1
            new_team = Team(next_id, f"{current_user.name}'s team")
            db.session.add(new_team)
            current_user.team_id = next_id
            db.session.commit()
        else:
            return { 'error': 'You have already been in a team!' }, 400

    @bp.route('/team/update', methods = [ 'POST' ])
    @login_required
    def update_team_info():
        if current_user.team_id == None or current_user.team_id <= 0:
            return { 'error': 'You are not in a team yet!' }, 400

        form = TeamInfo()
        if form.validate_on_submit():
            try:
                team = current_user.team
                team.name = form.name.data
                team.profile_pic = cleanse_profile_pic(form.profile_pic.data)
                team.description = form.description.data
                team.repo = form.repo.data
                db.session.commit()
                return {}
            except Exception as e:
                return { 'error': 'Error occured while updating info.', 'details': str(e) }, 500
        else:
            return { 'error': 'Form contains error. Check "details" field for more information.', 'details': form.errors }, 400

    bp.storage = SQLAlchemyStorage(OAuth, db.session, user = current_user)
    app.register_blueprint(bp)
