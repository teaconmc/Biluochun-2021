import hashlib
import os

# List of valid origin domains for CORS purpose.
CORS_ORIGINS = [ 'localhost' ]

CORS_ALWAYS_SEND = True

MAX_CONTENT_LENGTH = 1024 * 1024

# Secret key used for CSRF token and others
SECRET_KEY = hashlib.sha512(b"BILUOCHUN").hexdigest()

# Client ID of your Azure Active Directory (AAD) App. It is in form of UUID/GUID.
AZURE_OAUTH_CLIENT_ID = None
# Client secret of your AAD App. KEEP IT SECRET!
AZURE_OAUTH_CLIENT_SECRET = None

# URL that points to your SQL database. SQLite is used here for dev purpose.
# Major implmenetations such as MySQL and PostgesSQL also works here.
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.getcwd()}/dev.db"

# Hush.
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Domain to which Set-Cookie apply
SESSION_COOKIE_DOMAIN = 'example.invalid'
# Cookies are secure-channel-only and http-only
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
# Same for 'remember me' cookies used by Flask-Login, although we don't use that currently
REMEMBER_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_SECURE = True

WEBHOOK_ENABLED = False
WEBHOOK_URL = ""
WEBHOOK_SECRET = b""
