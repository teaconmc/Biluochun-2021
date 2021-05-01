'''
Utility methods used by Biluochun.
'''

from io import BytesIO

from PIL import Image

from .model import Team

def cleanse_profile_pic(raw):
    '''
    Read the image and convert to png format regardless.
    '''
    img = Image.open(raw)
    cleansed = BytesIO()
    img.save(cleansed, format = 'png')
    return cleansed.getvalue()

def find_team_by_invite(invite_code):
    return Team.query.filter_by(invite = invite_code).first()

def find_team_by_name(team_name):
    return Team.query.filter_by(name = team_name).first()

def find_team_by_mod_name(mod_name):
    return Team.query.filter_by(mod_name = mod_name).first()

def team_summary(team, detailed = False, invitation = False):
    info = { 'id': team.id, 'name': team.name, 'mod_name': team.mod_name, 'repo': team.repo }
    if detailed:
        info['desc'] = team.description
    if invitation:
        info['invite'] = team.invite
    return info

def user_summary(user):
    return { 'id': user.id, 'name': user.name }
