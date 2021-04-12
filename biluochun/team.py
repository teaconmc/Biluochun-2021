from .form import Avatar, TeamInfo
from .model import Team, User, db
from .util import cleanse_profile_pic, team_summary
from flask import Blueprint, redirect, request, send_file, url_for
from flask.json import jsonify
from flask_login import current_user, login_required
from io import BytesIO
from sqlalchemy import func
import secrets

def init_team_api(app):
    bp = Blueprint('api', __name__, url_prefix = '/api/team')
    
    @bp.route('/', methods = [ 'GET' ])
    def list_all_teams():
        return jsonify([team_summary(team) for team in Team.query.all()])

    @bp.route('/', methods = [ 'POST' ])
    @login_required
    def create_team():
        if current_user.team_id == None or current_user.team_id <= 0:
            next_id = db.session.query(func.max(Team.id)) + 1
            new_team = Team(next_id, f"{current_user.name}'s team", secrets.token_hex(8))
            db.session.add(new_team)
            current_user.team_id = next_id
            db.session.commit()
            return {}
        else:
            return { 'error': 'You have already been in a team!' }, 400

    @bp.route('/<team_name>', methods = [ 'GET' ])
    def list_team(team_name):
        team = Team.query.filter_by(name = team_name).first()
        if team == None:
            return { 'error': 'No such team' }, 404
        else:
            return team_summary(team, detailed = True)

    @bp.route('/<team_name>', methods = [ 'POST' ])
    @login_required
    def update_team(team_name):
        team = Team.query.filter_by(name = team_name).first()
        if team == None:
            return { 'error': 'No such team' }, 404

        if current_user.team_id != team.id:
            return { 'error': f"You are not in team '{team.name}'!" }, 400

        form = TeamInfo()
        if form.validate_on_submit():
            try:
                team = current_user.team
                team.name = form.name.data
                team.mod_name = form.mod_name.data
                team.description = form.desc.data
                team.repo = form.repo.data
                db.session.commit()
                return {}
            except Exception as e:
                return { 'error': 'Error occured while updating info.', 'details': str(e) }, 500
        else:
            return { 'error': 'Form contains error. Check "details" field for more information.', 'details': form.errors }, 400

    @bp.route('/<team_name>/members', methods = [ 'GET' ])
    def get_team_members(team_name):
        team = Team.query.filter_by(name = team_name).first()
        if team == None:
            return { 'error': 'No such team' }, 404
        else:
            return { 'members': [ member.name for member in team.members ] }

    @bp.route('/<team_name>/avatar', methods = [ 'GET' ])
    @bp.route('/<team_name>/icon', methods = [ 'GET' ])
    @bp.route('/<team_name>/profile_pic', methods = [ 'GET' ])
    def get_team_icon(team_name):
        team = Team.query.filter_by(name = team_name).first()
        if team == None:
            return { 'error': 'No such team' }, 404
        else:
            return send_file(BytesIO(team.profile_pic), mimetype = 'image/png')
    
    @bp.route('/<team_name>/avatar', methods = [ 'POST' ])
    @bp.route('/<team_name>/icon', methods = [ 'POST' ])
    @bp.route('/<team_name>/profile_pic', methods = [ 'POST' ])
    @login_required
    def update_team_icon(team_name):
        team = Team.query.filter_by(name = team_name).first()
        if team == None:
            return { 'error': 'No such team' }, 404

        if current_user.team_id != team.id:
            return { 'error': f"You are not in team '{team.name}'!" }, 400
        
        raw_img = None
        if form:
            form = Avatar()
            raw_img = form.avatar.data
        else:
            raw_img = request.stream # TODO Validate it
            
        if raw_img:
            team.profile_pic = cleanse_profile_pic(raw_img)
            db.session.commit()
            return {}
        else:
            return { 'error': 'No valid image file found. Check if you forget to put an image file in request body?' }, 400

    app.register_blueprint(bp)
