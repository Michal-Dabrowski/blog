
import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_ECHO=True

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

#  mail server configuration
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['you@example.com']

# pagination
POSTS_PER_PAGE = 4

UPLOAD_FOLDER = basedir + '\\app\\static\\avatars'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'csv'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024