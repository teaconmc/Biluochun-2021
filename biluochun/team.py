'''
Defines /api/team endpoints series.
'''

import secrets

from flask import Blueprint, redirect, url_for
from flask.json import jsonify
from flask_login import current_user, login_required
from sqlalchemy import func

from .form import Avatar, TeamInfo
from .model import Image, Team, db
from .util import cleanse_profile_pic, find_team_by_name, team_summary, user_summary

def init_team_api(app):
    '''
    Initialize the app with /api/team endpoints series.
    '''
    bp = Blueprint('api', __name__, url_prefix = '/api/team')
    
    @bp.route('/', methods = [ 'GET' ])
    def list_all_teams():
        return jsonify([team_summary(team) for team in Team.query.all()])

    @bp.route('/', methods = [ 'POST' ])
    @login_required
    def create_team():
        if current_user.team_id is None:
            next_id = db.session.query(func.max(Team.id)).first()[0]
            if next_id:
                next_id += 1
            else:
                next_id = 1
            new_team = Team(id = next_id, name = f"{current_user.name}'s team", \
                mod_name = f"{current_user.name}'s mod", invite = secrets.token_hex(8), \
                profile_pic_id = 2)
            current_user.team_id = new_team.id
            form = TeamInfo()
            if form.validate_on_submit():
                if form.name.data is not None:
                    new_team.name = form.name.data
                if form.mod_name.data is not None:
                    new_team.mod_name = form.mod_name.data
                if form.desc.data is not None:
                    new_team.description = form.desc.data
                if form.repo.data is not None:
                    new_team.repo = form.repo.data
            # Suffix the team name in case of duplication
            suffix = 1
            while find_team_by_name(new_team.name) is not None:
                new_team.name = new_team.name + str(suffix)
                suffix += 1
            # Commit the changes
            db.session.add(new_team)
            db.session.commit()
            return {}
        else:
            return { 'error': 'You have already been in a team!' }, 400

    @bp.route('/<int:team_id>', methods = [ 'GET' ])
    def show_team(team_id):
        team = Team.query.get(team_id)
        return ({ 'error': 'No such team' }, 404) if team is None else team_summary(team, detailed = True)

    @bp.route('/<int:team_id>', methods = [ 'POST' ])
    @login_required
    def update_team(team_id):
        team = Team.query.get(team_id)
        if team is None:
            return { 'error': 'No such team' }, 404
        if current_user.team_id != team.id:
            return { 'error': f"You are not in team '{team.name}'!" }, 400
        form = TeamInfo()
        if form.validate_on_submit():
            if form.name.data is not None:
                team.name = form.name.data
            if form.mod_name.data is not None:
                team.mod_name = form.mod_name.data
            if form.desc.data is not None:
                team.description = form.desc.data
            if form.repo.data is not None:
                team.repo = form.repo.data
            # Suffix the team name in case of duplication
            suffix = 1
            while find_team_by_name(team.name) is not None:
                team.name = team.name + str(suffix)
                suffix += 1
            # Commit the changes
            db.session.commit()
            return {}
        else:
            return {
                'error': 'Form contains error. Check "details" field for more information.',
                'details': form.errors
            }, 400

    @bp.route('/<int:team_id>/members', methods = [ 'GET' ])
    def get_team_members(team_id):
        team = Team.query.get(team_id)
        return ({ 'error': 'No such team' }, 404) if team is None \
            else jsonify([ user_summary(member) for member in team.members ])

    @bp.route('/<int:team_id>/avatar', methods = [ 'GET' ])
    @bp.route('/<int:team_id>/icon', methods = [ 'GET' ])
    @bp.route('/<int:team_id>/profile_pic', methods = [ 'GET' ])
    def get_team_icon(team_id):
        team = Team.query.get(team_id)
        if team is None:
            return { 'error': 'No such team' }, 404
        return redirect(url_for('image.get_image', img_id = team.profile_pic_id))
    
    @bp.route('/<int:team_id>/avatar', methods = [ 'POST' ])
    @bp.route('/<int:team_id>/icon', methods = [ 'POST' ])
    @bp.route('/<int:team_id>/profile_pic', methods = [ 'POST' ])
    @login_required
    def update_team_icon(team_id):
        team = Team.query.get(team_id)
        if team is None:
            return { 'error': 'No such team' }, 404
        if current_user.team_id != team.id:
            return { 'error': f"You are not in team '{team.name}'!" }, 400
        form = Avatar()
        if form.validate_on_submit():
            next_id = db.session.query(func.max(Image.id)).first()[0]
            if next_id:
                next_id += 1
            else:
                next_id = 3
            avatar = Image(next_id, data = cleanse_profile_pic(form.avatar.data))
            db.session.add(avatar)
            team.profile_pic_id = avatar.id
            db.session.commit()
            return {}
        else:
            return {
                'error': 'Form contains error. Check "details" field for more information.',
                'details': form.errors
            }, 400

    app.register_blueprint(bp)
