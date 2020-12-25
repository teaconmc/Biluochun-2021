import hashlib
import os

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
