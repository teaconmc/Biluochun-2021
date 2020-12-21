from .model import Team, User, db
from flask import Blueprint, redirect, render_template, url_for
from flask.json import jsonify

def summary(team):
    return { 'team': team.name, 'repo': team.repo }

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

    app.register_blueprint(bp)
