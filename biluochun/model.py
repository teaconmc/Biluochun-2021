from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
import flask_login
from flask_sqlalchemy import SQLAlchemy

# Note
# With Flask-SQLAlchemy, __tablename__ is auto-filled with class name,
# converted from CamelCase to snake_case. You can still manually 
# supply one if you want to override.

db = SQLAlchemy()

class Team(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.UnicodeText, nullable = False, unique = True)
    mod_name = db.Column(db.UnicodeText, nullable = False, unique = True)
    invite = db.Column(db.String(16), nullable = False, unique = True)
    profile_pic = db.Column(db.LargeBinary)
    description = db.Column(db.UnicodeText)
    repo = db.Column(db.Text, unique = True)
    members = db.relationship('User', backref = 'user', lazy = True)

    def __repr__(self):
        return f"<Team #{self.id} '{self.name}' repo={self.repo}>"

class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.UnicodeText, nullable = False, unique = True)
    profile_pic = db.Column(db.LargeBinary)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    team = db.relationship(Team)

    def get_id(self):
        return self.id

class OAuth(db.Model, OAuthConsumerMixin):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
