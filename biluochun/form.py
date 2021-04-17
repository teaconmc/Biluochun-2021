from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import IntegerField, StringField
from wtforms.fields import FieldList
from wtforms.validators import InputRequired, Optional, URL, ValidationError

from .model import Team, User

def validate_team(form, field):
    if field.data is None:
        raise ValidationError("Team id is missing")
    if Team.query.get(field.data) is None:
        raise ValidationError(f"Team #{field.data} does not exist")

def validate_user(form, field):
    if field.data is None:
        raise ValidationError("User id is missing")
    if User.query.get(field.data) is None:
        raise ValidationError(f"User #{field.data} does not exist")

class Avatar(FlaskForm):
    avatar = FileField('avatar', validators = [
        FileRequired(),
        FileAllowed([ 'jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'webp' ]) 
    ])

class UserInfo(FlaskForm):
    name = StringField('name')
    team = IntegerField('team', validators = [ InputRequired(), validate_team ])

class UserList(FlaskForm):
    users = FieldList(IntegerField('user', validators = [ InputRequired(), validate_user ]))

class TeamInfo(FlaskForm):
    name = StringField('name', validators = [ Optional() ])
    mod_name = StringField('mod_name', validators = [ Optional() ])
    desc = StringField('desc', validators = [ Optional() ])
    repo = StringField('repo', validators = [ URL(), Optional() ])
