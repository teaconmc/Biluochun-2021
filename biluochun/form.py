"""
Defines web form structures used by Biluochun.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from PIL import Image, UnidentifiedImageError
from wtforms import StringField
from wtforms.validators import Length, Optional, URL, ValidationError

from .model import User
from .util import find_team_by_invite, find_team_by_mod_name, find_team_by_name


def validate_image(form, field):
    try:
        with Image.open(field.data):
            pass
    except UnidentifiedImageError as exc:
        raise ValidationError("The uploaded file is not image or is a broken image.") from exc


def validate_invite(form, field):
    if field.data is None:
        raise ValidationError("Team invite code is missing")
    if find_team_by_invite(field.data) is None:
        raise ValidationError("Team invite code does not exist")


def validate_team_name(form, field):
    target_team = form.target_team
    existing_team = find_team_by_name(field.data)
    if existing_team is not None and existing_team != target_team:
        raise ValidationError(f"Team name '{field.data}' already exist")


def validate_mod_name(form, field):
    target_team = form.target_team
    existing_team = find_team_by_mod_name(field.data)
    if existing_team is not None and existing_team != target_team:
        raise ValidationError(f"Mod name '{field.data}' already exist")


def validate_username(form, field):
    if field.data is None:
        raise ValidationError("Username cannot be empty")
    target_user = form.target_user
    existing_user = User.query.filter_by(name=field.data).first()
    if existing_user is not None and existing_user != target_user:
        raise ValidationError(f"Username #{field.data} has been used")


def validate_qq(form, field):
    if field.data is None:
        raise ValidationError("QQ cannot be empty")
    for ch in field.data:
        if ord(ch) > ord('9') or ord(ch) < ord('0'):
            raise ValidationError("Invalid character '{}'".format(ch))


class Avatar(FlaskForm):
    class Meta:
        csrf = False

    avatar = FileField('avatar', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'webp']),
        validate_image
    ])


class UserInfo(FlaskForm):
    class Meta:
        csrf = False

    name = StringField('name', validators=[
        Length(min=1, max=128),
        validate_username,
        Optional()
    ])

    def __init__(self, target_user=None, *args, **kwargs):
        super(UserInfo, self).__init__(*args, **kwargs)
        self.target_user = target_user


class TeamInfo(FlaskForm):
    class Meta:
        csrf = False

    name = StringField('name', validators=[
        Length(min=1, max=128),
        validate_team_name,
        Optional()])
    mod_name = StringField('mod_name', validators=[
        Length(min=1, max=128),
        validate_mod_name,
        Optional()
    ])
    desc = StringField('desc', validators=[Optional()])
    repo = StringField('repo', validators=[URL(), Optional()])

    # https://stackoverflow.com/a/62608306
    def __init__(self, target_team=None, *args, **kwargs):
        super(TeamInfo, self).__init__(*args, **kwargs)
        self.target_team = target_team


class TeamInvite(FlaskForm):
    class Meta:
        csrf = False

    invite_code = StringField('invite', validators=[validate_invite])


class QQVerify(FlaskForm):
    class Meta:
        csrf = False

    qq = StringField('qq', validators=[Length(min=1, max=128), validate_qq])
    code = StringField('code', validators=[Length(min=1, max=128)])


class QQSet(FlaskForm):
    class Meta:
        csrf = False

    qq = StringField('qq', validators=[Length(min=1, max=20), validate_qq])
