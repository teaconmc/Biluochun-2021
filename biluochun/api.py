from .model import Team, User, db
from flask import Blueprint, redirect, render_template, send_file, url_for
from flask.json import jsonify
from io import BytesIO

def summary(team, detailed = False):
    info = { 'name': team.name, 'repo': team.repo }
    if detailed:
        info['desc'] = team.description
    return info

def init_api(app):
    bp = Blueprint('api', __name__, url_prefix = '/api')
    
    @bp.route('/team')
    def list_all_teams():
        return jsonify([summary(team) for team in Team.query.all()])

    @bp.route('/team/<team_name>')
    def list_team(team_name):
        team = Team.query.filter_by(name = team_name).first()
        if team == None:
            return { 'error': 'No such team' }, 404
        else:
            return summary(team)

    @bp.route('/team/<team_name>/avatar')
    @bp.route('/team/<team_name>/icon')
    @bp.route('/team/<team_name>/profile_pic')
    def get_team_icon(team_name):
        team = Team.query.filter_by(name = team_name).first()
        if team == None:
            return { 'error': 'No such team' }, 404
        else:
            return send_file(BytesIO(team.profile_pic), mimetype = 'image/png')
    

    app.register_blueprint(bp)
