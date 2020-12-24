from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import IntegerField, StringField
from wtforms.validators import Optional, URL, ValidationError

def validate_team(form, field):
    if field.data != None and Team.query.get(field.data) == None:
        raise ValidationError(f"Team #{field.data} does not exist")

class UserInfo(FlaskForm):
    name = StringField('name')
    profile_pic = FileField('profile_pic', validators = [ FileAllowed([ 'jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'webp' ]), Optional() ])
    team = IntegerField('team', validators = [ validate_team ])

class TeamInfo(FlaskForm):
    name = StringField('name')
    desc = StringField('desc')
    repo = StringField('repo', validators = [ URL(), Optional() ])
