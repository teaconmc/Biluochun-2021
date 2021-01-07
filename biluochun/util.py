from .model import Team
from io import BytesIO
from PIL import Image

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
