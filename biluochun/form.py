'''
Defines web form structures used by Biluochun.
'''

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import StringField
from wtforms.validators import Length, Optional, URL, ValidationError

from .model import User
from .util import find_team_by_invite

def validate_invite(form, field):
    if field.data is None:
        raise ValidationError("Team invite code is missing")
    if find_team_by_invite(field.data) is None:
        raise ValidationError("Team invite code does not exist")

def validate_user(form, field):
    if field.data is None:
        raise ValidationError("User id is missing")
    if User.query.get(field.data) is None:
        raise ValidationError(f"User #{field.data} does not exist")

class Avatar(FlaskForm):
    class Meta:
        csrf = True
    avatar = FileField('avatar', validators = [
        FileRequired(),
        FileAllowed([ 'jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'webp' ]) 
    ])

class UserInfo(FlaskForm):
    class Meta:
        csrf = True
    name = StringField('name', validators = [ Length(min = 1, max = 128), Optional() ])

class TeamInfo(FlaskForm):
    class Meta:
        csrf = True
    name = StringField('name', validators = [ Length(min = 1, max = 128), Optional() ])
    mod_name = StringField('mod_name', validators = [ Length(min = 1, max = 128), Optional() ])
    desc = StringField('desc', validators = [ Optional() ])
    repo = StringField('repo', validators = [ URL(), Optional() ])

class TeamInvite(FlaskForm):
    class Meta:
        csrf = True
    invite_code = StringField('invite', validators = [ validate_invite ])
